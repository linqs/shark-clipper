'use strict';

window.shark = window.shark || {};

window.shark.info = window.shark.info || {};
window.shark.screenshots = window.shark.screenshots || {};
window.shark.info['screenshot_counter'] = 0;

function goToLoadingScreen() {
    document.querySelector('.file-upload-screen').style.display = 'none';
    document.querySelector('.loading-screen').style.display = 'initial';
    document.querySelector('.work-screen').style.display = 'none';
}

function goToUploadScreen() {
    document.querySelector('.file-upload-screen').style.display = 'initial';
    document.querySelector('.loading-screen').style.display = 'none';
    document.querySelector('.work-screen').style.display = 'none';
}

function goToWorkScreen() {
    document.querySelector('.file-upload-screen').style.display = 'none';
    document.querySelector('.loading-screen').style.display = 'none';
    document.querySelector('.work-screen').style.display = 'initial';
}

function outputError(message, extra = undefined) {
    quietError(message, extra);
    window.alert(message);
}

function quietError(message, extra = undefined) {
    console.error(message);
    if (extra) {
        console.log(extra);
    }
}

// Return false if the response is bad and processing should not continue, true otherwise.
function checkSeverResponse(baseErrorMessage, response) {
    if (response.ok) {
        return true;
    }

    response.text()
        .then(function(text_body) {
            text_body = text_body.trim();
            if (text_body.length === 0) {
                outputError(baseErrorMessage);
            } else {
                outputError(`${baseErrorMessage} Message from server "${text_body}".`);
            }
        })
        .catch(function(body) {
            outputError(baseErrorMessage, body);
        })
        .finally(function() {
            goToUploadScreen();
        });

    return false;
}

function save() {
    let promise = fetch('/save', {
        method: 'POST',
        body: JSON.stringify({
            'video': window.shark.info['video'],
            'screenshots': window.shark.screenshots,
            'key_metadata': window.shark.info['key_metadata'],
            'all_metadata': window.shark.info['all_metadata'],
        }),
        headers: {
            'shark-clipper-save': true,
        },
    });

    goToLoadingScreen();

    promise
        .then(function(response) {
            checkSeverResponse('Failed to save screenshots.', response);
        })
        .catch(function(response) {
            outputError('Failed to save screenshots.', response);
        })
        .finally(function() {
            goToWorkScreen();
        });
}

function uploadVideo() {
    let file = document.querySelector('input.file-selector').files[0];

    let promise = fetch('/video', {
        method: 'POST',
        body: file,
        headers: {
            'shark-clipper-upload': true,
            'shark-clipper-filename': file.name,
            'shark-clipper-type': file.type,
        },
    });

    goToLoadingScreen();

    promise
        .then(function(response) {
            if (!checkSeverResponse('Failed to upload video.', response)) {
                return;
            }

            response.json()
                .then(function(info) {
                    initVideo(info);
                    goToWorkScreen();
                })
                .catch(function(response) {
                    outputError("Failed to decode video response from server.", response);
                    goToUploadScreen();
                });
        })
        .catch(function(response) {
            outputError("Failed to upload video.", response);
            goToUploadScreen();
        });
}

function initVideo(info) {
    let name = info.original_name ?? info.video_id;
    let metadata = info.key_metadata ?? {};

    let start_time = metadata.start_time_unix ?? undefined;

    let video_location = metadata.location ?? {};
    let latitude = video_location.latitude ?? undefined;
    let latitude_input_value = convertCoordinatesForInput(latitude);
    let longitude = video_location.longitude ?? undefined;
    let longitude_input_value = convertCoordinatesForInput(longitude);

    let videoInfo = {
        id: info.video_id,
        name: name,
        start_time: start_time,
        latitude: latitude_input_value,
        longitude: longitude_input_value,
    };

    window.shark.info['video'] = videoInfo;
    window.shark.info['key_metadata'] = info.key_metadata;
    window.shark.info['all_metadata'] = info.all_metadata;

    let videoContainer = document.querySelector('.work-screen .video-area');
    videoContainer.innerHTML = createVideoAreaHTML(videoInfo, info.path, info.type, latitude_input_value, longitude_input_value);

    removeHotkeysOnText();

    initVideoControls();
}

function toggleSelection() {
    if (document.querySelector(`.video-container .selection`)) {
        removeSelectionBox('.video-container');
    } else {
        makeSelectionBox('.video-container');
    }
}

function captureFrame() {
    // Default values used if there is no selection;
    let widthPercent = 1.0;
    let heightPercent = 1.0;
    let xPercent = 0.0;
    let yPercent = 0.0;

    let selection = document.querySelector('.video-container .selection');

    if (selection) {
        let selectionBounding = selection.getBoundingClientRect();
        let parentBounding = selection.offsetParent.getBoundingClientRect();

        widthPercent = selectionBounding.width / parentBounding.width;
        heightPercent = selectionBounding.height / parentBounding.height;
        xPercent = (selectionBounding.x - parentBounding.x) / parentBounding.width;
        yPercent = (selectionBounding.y - parentBounding.y) / parentBounding.height;
    }

    let screenshot = takeVideoScreenshot('.video-container video', xPercent, yPercent, widthPercent, heightPercent);

    addScreenshot(screenshot);
}

function addScreenshot(screenshot) {
    window.shark.screenshots[screenshot.id] = screenshot;

    let html = createScreenshotHTML(screenshot);
    document.querySelector('.screenshot-area').insertAdjacentHTML('afterbegin', html);

    removeHotkeysOnText();
}

// Flip a screenshot by adding it the the canvas flipped horizontally or vertically.
function flipScreenshot(screenshot_id, flip_vertical) {
    let img = document.querySelector(`.screenshot[data-id="${screenshot_id}"] img`);

    // Default values for horizontal flip;
    let direction = 'flipped_horizontally';
    let scale_x = -1;
    let scale_y = 1;
    let draw_x = -img.naturalWidth;
    let draw_y = 0;

    if (flip_vertical) {
        direction = 'flipped_vertically';
        scale_x = 1;
        scale_y = -1;
        draw_x = 0;
        draw_y = -img.naturalHeight;
    }

    let canvas = document.createElement('canvas');
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;

    let context = canvas.getContext('2d');
    context.scale(scale_x, scale_y);
    context.drawImage(img, draw_x, draw_y);
    img.src = canvas.toDataURL('image/jpeg');

    // Update image metadata.
    window.shark.screenshots[screenshot_id][direction] = !Boolean(window.shark.screenshots[screenshot_id][direction]);
    window.shark.screenshots[screenshot_id]['dataURL'] = canvas.toDataURL('image/jpeg');
}

// Edit the global video record (which may change screenshots).
function editVideo(element, field) {
    if (field === 'name') {
        window.shark.info['video']['name'] = element.value;

        // Update screenshots.
        Object.values(window.shark.screenshots).forEach(function(screenshot) {
            // Ignore names that have been manually edited.
            if (screenshot.edited_name) {
                return;
            }

            let index_string = screenshot.name.substring(screenshot.name.length - 3);
            let name = window.shark.info['video'].name + "_" + index_string;

            screenshot.name = name;

            let input = document.querySelector(`.screenshot[data-id="${screenshot_id}"] input[name="name"]`);
            input.value = name;
        });
    } else if (field === 'start_time') {
        if (element.value) {
            window.shark.info['video']['start_time'] = (new Date(element.value)).getTime() / 1000;
        } else {
            window.shark.info['video']['start_time'] = undefined;
        }

        // Update screenshots.
        Object.values(window.shark.screenshots).forEach(function(screenshot) {
            let time = undefined;
            let time_input_value = undefined;

            if (window.shark.info.video.start_time) {
                time = window.shark.info.video.start_time + screenshot.offset;
                time_input_value = convertUnixSecsForInput(time);
            }

            screenshot.time = time;

            let input = document.querySelector(`.screenshot[data-id="${screenshot_id}"] input[name="time"]`);
            input.value = time_input_value;
        });
    } else {
        window.shark.info['video'][field] = element.value;
    }
}

// Edit the global screenshot record.
function editScreenshot(element, id, field) {
    window.shark.screenshots[id][field] = element.value;

    if (field === 'name') {
        window.shark.screenshots[id]['edited_name'] = true;
    }
}

// Use percentage values since we will have to compute sizes based off of the video's intrinsic (not apparent) size.
function takeVideoScreenshot(query, xPercent, yPercent, widthPercent, heightPercent, format = 'image/jpeg') {
    let video = document.querySelector(query);

    let x = xPercent * video.videoWidth;
    let y = yPercent * video.videoHeight;
    let width = widthPercent * video.videoWidth;
    let height = heightPercent * video.videoHeight;

    let id = randomHex();

    // Get screenshot counter value and update counter.
    let index_string = String(window.shark.info['screenshot_counter']).padStart(3, '0');
    window.shark.info['screenshot_counter']++;

    let name = window.shark.info['video'].name + "_" + index_string;

    let time = undefined;
    let time_input_value = undefined;

    if (window.shark.info.video.start_time) {
        time = window.shark.info.video.start_time + video.currentTime;
        time_input_value = convertUnixSecsForInput(time);
    }

    return {
        'id': id,
        'name': name,
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'offset': video.currentTime,
        'time': time,
        'dataURL': takeScreenshot(video, x, y, width, height, format),
        'edited_name': false,
        'flipped_horizontally': false,
        'flipped_vertically': false,
    };
}

function takeScreenshot(source, x, y, width, height, format = 'image/jpeg') {
    var canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;

    var context = canvas.getContext('2d');
    context.drawImage(source, x, y, width, height, 0, 0, width, height);

    return canvas.toDataURL(format);
}

function deleteScreenshot(screenshot_id) {
    document.querySelector(`.screenshot[data-id="${screenshot_id}"]`).remove();
    delete window.shark.screenshots[screenshot_id];
}

// Inputs don't have a timezone aware type.
// Instead we use datetime-local (which is always local).
// But to format to set it's input is a bit tricky to set (while getting the timezone correct).
// Converting from an input is simple, since Date() will assume local time.
function convertUnixSecsForInput(unixSeconds) {
    if (!unixSeconds) {
        return undefined;
    }

    // Adjust the local time with the timezone offset.
    let offsetDate = new Date((unixSeconds * 1000) + (new Date().getTimezoneOffset() * -60 * 1000));

    // Strip off the timezone portion of the string.
    return offsetDate.toISOString().slice(0, 19);
}

function convertCoordinatesForInput(coordinates) {
    if (!coordinates) {
        return undefined;
    }

    // Remove the leading + from coordinates.
    return coordinates.replace(/^\+/, '');
}

// Fetch the server's version and add it to the page's title.
function fetchVersion() {
    let promise = fetch('/version', {
        method: 'GET',
    });

    promise
        .then(function(response) {
            if (!response.ok) {
                quietError("Got a failure to version request.", response);
                return;
            }

            response.text()
                .then(function(text_body) {
                    text_body = text_body.trim();
                    if (text_body.length === 0) {
                        quietError("Got an empty version from the server.");
                        return;
                    }

                    document.querySelector('.header').insertAdjacentHTML('beforeend', `<h2>Version ${text_body}</h2>`);
                })
                .catch(function(body) {
                    quietError('Failed to get text from version response body.', response);
                });
        })
        .catch(function(response) {
            quietError('Failed to fetch server version.', response);
        });
}

// Initialize hotkey functionality.
function initializeHotkeys() {
    document.addEventListener('keydown', (event) => {
        if (event.code === 'KeyB') {
            toggleSelection();
        } else if (event.code === 'KeyF') {
            captureFrame();
        } else if (event.code === 'KeyS') {
            save();
        }
    });

    removeHotkeysOnText();
}

function removeHotkeysOnText() {
    document.querySelectorAll('input[type="text"]').forEach((input) => {
        input.setAttribute('onkeydown', 'event.stopPropagation()');
    });
}

function main() {
    fetchVersion();
    initializeHotkeys();
    goToUploadScreen();
}

document.addEventListener("DOMContentLoaded", main);
