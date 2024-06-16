'use strict';

window.shark = window.shark || {};

window.shark.info = window.shark.info || {};
window.shark.screenshots = window.shark.screenshots || {};

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
            goToWorkScreen();
        })
        .catch(function(response) {
            console.error("Failed to save screenshots.");
            console.error(response);
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
            response.json()
                .then(function(info) {
                    initVideo(info);
                    goToWorkScreen();
                })
                .catch(function(response) {
                    console.error("Failed to decode video response (json) body.");
                    console.error(response);
                    goToUploadScreen();
                });
        })
        .catch(function(response) {
            console.error("Failed to upload video.");
            console.error(response);
            goToUploadScreen();
        });
}

function initVideo(info) {
    let name = info.original_name ?? info.video_id;
    let metadata = info.key_metadata ?? {};

    let start_time = metadata.start_time_unix ?? undefined;
    let start_time_input_value = convertUnixSecsForInput(start_time);

    let video_location = metadata.location ?? {};
    let latitude = video_location.latitude ?? undefined;
    let longitude = video_location.longitude ?? undefined;

    window.shark.info['video'] = {
        id: info.video_id,
        name: name,
        start_time: start_time,
        latitude: latitude,
        longitude: longitude,
    };

    window.shark.info['key_metadata'] = info.key_metadata;
    window.shark.info['all_metadata'] = info.all_metadata;

    let videoContainer = document.querySelector('.work-screen .video-area');
    videoContainer.innerHTML = `
        <div class='video-container media-area'>
            <video controls>
                <source src='${info.path}' type='${info.type}' />
            </video>
        </div>
        <div class='metadata-area'>
            <div>
                <label for='name'>Name</label>
                <input type='text' name='name'
                        data-video-id='${info.video_id}'
                        onchange='editVideo(this, "name")'
                        value='${info.original_name}' />
            </div>
            <div>
                <label for='name'>Video Start Time</label>
                <input type='datetime-local' name='start_time'
                        data-video-id='${info.video_id}'
                        onchange='editVideo(this, "start_time")'
                        value='${start_time_input_value}' />
            </div>
            <div>
                <label for='latitude'>Latitude</label>
                <input type='number' name='latitude' step='0.01'
                        data-video-id='${info.video_id}'
                        onchange='editVideo(this, "latitude")'
                        value='${latitude}' />
            </div>
            <div>
                <label for='longitude'>Longitude</label>
                <input type='number' name='longitude' step='0.01'
                        data-video-id='${info.video_id}'
                        onchange='editVideo(this, "longitude")'
                        value='${longitude}' />
            </div>
        </div>
    `;
}

function toggleSelection() {
    // TEST - toggle

    makeSelectionBox('.video-container');
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

    let time_input_value = convertUnixSecsForInput(screenshot.time);

    let html = `
        <div class='screenshot media-metadata-container'>
            <div class='image-area media-area' width='${screenshot.width}' height='${screenshot.height}'>
                <img src='${screenshot.dataURL}' />
            </div>
            <div class='metadata-area'>
                <div>
                    <label for='name'>Name</label>
                    <input type='text' name='name'
                            data-screenshot='${screenshot.id}'
                            onchange='editScreenshot(this, "${screenshot.id}", "name")'
                            value='${screenshot.name}' />
                </div>
                <div>
                    <label for='time'>Time</label>
                    <input type='datetime-local' name='time' readonly='true' disabled
                            data-screenshot='${screenshot.id}'
                            value='${time_input_value}' />
                </div>
            </div>
        </div>
    `;

    document.querySelector('.screenshot-area').insertAdjacentHTML('beforeend', html);
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

            let input = document.querySelector(`input[name="name"][data-screenshot="${screenshot.id}"]`);
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

            let input = document.querySelector(`input[name="time"][data-screenshot="${screenshot.id}"]`);
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

    let index_string = String(Object.keys(window.shark.screenshots).length).padStart(3, '0');
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
        'width': width,
        'height': height,
        'offset': video.currentTime,
        'time': time,
        'dataURL': takeScreenshot(video, x, y, width, height, format),
        'edited_name': false,
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

function main() {
    goToUploadScreen();
}

document.addEventListener("DOMContentLoaded", main);
