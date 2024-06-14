'use strict';

window.shark = window.shark || {};

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
    // TEST
    let name = 'TEST';

    let html = `
        <div class='screenshot'>
            <div class='image-area' width='${screenshot.width}' height='${screenshot.height}'>
                <img src='${screenshot.dataURL}' />
            </div>
            <div class='metadata-area'>
                <div>
                    <label for='name'>Name</label>
                    <input type='text' name='name' value='${name}' />
                </div>
                <div>
                    <label for='time'>Time</label>
                    <input type='number' name='time' readonly='true' disabled value='${screenshot.time}' />
                </div>
            </div>
        </div>
    `;

    document.querySelector('.screenshot-area').insertAdjacentHTML('beforeend', html);
}

// Use percentage values since we will have to compute sizes based off of the video's intrinsic (not apparent) size.
function takeVideoScreenshot(query, xPercent, yPercent, widthPercent, heightPercent, format = 'image/jpeg') {
    let video = document.querySelector(query);

    let x = xPercent * video.videoWidth;
    let y = yPercent * video.videoHeight;
    let width = widthPercent * video.videoWidth;
    let height = heightPercent * video.videoHeight;

    return {
        'width': width,
        'height': height,
        'time': video.currentTime,
        'dataURL': takeScreenshot(video, x, y, width, height, format),
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

function main() {
    // TEST
    console.log("TEST - main");
}

document.addEventListener("DOMContentLoaded", main);
