'use strict';

function createVideoAreaHTML(videoInfo, path, type, latitude_input_value, longitude_input_value) {
    let start_time_input_value = convertUnixSecsForInput(videoInfo.start_time);

    return `
        <div class='video-container media-area media-area-background'>
            <div class='video-wrap'>
                <video class='main-video' preload='auto' muted>
                    <source src='${path}' type='${type}' />
                </video>
            </div>
            <div class='video-controls'>
                <div class='video-controls-row video-controls-progress'>
                    <input type='range'
                            class='progress-bar'
                            value='0.0' min='0.0' max='1.0' step='0.01'
                            onchange='videoSeekProportional(this)' />
                    <div class='clip-highlight-container'>
                        <div class='clip-highlight'></div>
                    </div>
                </div>
                <div class='video-controls-row video-controls-clip'>
                    <button class='clip-start-now' onclick='setClipNow(true)'>Clip Start</button>
                    <input type='text' class='clip-start' onchange='setClipAbsolute(this, true)' value='-' />
                    <input type='text' class='current-time' onchange='videoSeek(this)' value='-' />
                    <input type='text' class='clip-end' onchange='setClipAbsolute(this, false)' value='-' />
                    <button class='clip-end-now' onclick='setClipNow(false)'>Clip End</button>
                </div>
                <div class='video-controls-row video-controls-seek'>
                    <button class='skip-far-back' onclick='videoSeekOffset(-5.0)'>↺</button>
                    <button class='skip-back' onclick='videoSeekOffset(-0.5)'>↶</button>
                    <button class='play-pause' onclick='videoTogglePlay()'>⏵</button>
                    <button class='skip-far-back' onclick='videoSeekOffset(0.5)'>↷</button>
                    <button class='skip-far-back' onclick='videoSeekOffset(5.0)'>↻</button>
                </div>
            </div>
        </div>
        <div class='metadata-area'>
            <div>
                <label for='name'>Name:</label>
                <input type='text' name='name'
                        data-video-id='${videoInfo.id}'
                        onchange='editVideo(this, "name")'
                        value='${videoInfo.name}' />
            </div>
            <div>
                <label for='name'>Video Start Time:</label>
                <input type='datetime-local' name='start_time'
                        data-video-id='${videoInfo.id}'
                        onchange='editVideo(this, "start_time")'
                        value='${start_time_input_value}' />
            </div>
            <div>
                <label for='latitude'>Latitude:</label>
                <input type='number' name='latitude' step='0.01'
                        data-video-id='${videoInfo.id}'
                        onchange='editVideo(this, "latitude")'
                        value='${latitude_input_value}' />
            </div>
            <div>
                <label for='longitude'>Longitude:</label>
                <input type='number' name='longitude' step='0.01'
                        data-video-id='${videoInfo.id}'
                        onchange='editVideo(this, "longitude")'
                        value='${longitude_input_value}' />
            </div>
        </div>
    `;
}

function createScreenshotHTML(screenshot) {
    let time_input_value = convertUnixSecsForInput(screenshot.time);

    return `
        <div class='screenshot media-metadata-container' data-id='${screenshot.id}'>
            <div class='image-area media-area' width='${screenshot.width}' height='${screenshot.height}'>
                <img class='media-area-background' src='${screenshot.dataURL}'/>
            </div>
            <div class='metadata-area'>
                <div>
                    <label for='name'>Name:</label>
                    <input type='text' name='name'
                            onchange='editScreenshot(this, "${screenshot.id}", "name")'
                            value='${screenshot.name}' />
                </div>
                <div>
                    <label for='time'>Time:</label>
                    <input type='datetime-local' name='time' readonly='true' disabled
                            value='${time_input_value}' />
                </div>
                <div>
                    <span>
                        <button onclick='flipScreenshot("${screenshot.id}", true)'>Vertical Flip</button>
                        <button onclick='flipScreenshot("${screenshot.id}", false)'>Horizontal Flip</button>
                    </span>
                </div>
                <div>
                    <button onclick='deleteScreenshot("${screenshot.id}")'>Delete</button>
                </div>
            </div>
        </div>
    `;
}
