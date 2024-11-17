'use strict';

window.shark = window.shark || {};
window.shark.media = window.shark.media || {};

// Initialize the video controls and block until the video is ready.
function initVideoControls() {
    let video = document.querySelector('.main-video');
    video.load();

    // Register a handler for updating as we progress through the video.
    video.addEventListener("timeupdate", function(event) {
        setCurrentTime(video.currentTime);
    });

    // Some browsers (often mobile) may not have the duration ready yet.
    if (!isNaN(video.duration)) {
        metadataLoaded();
    } else {
        video.addEventListener('loadedmetadata', function(event) {
            metadataLoaded();
        });
    }

    // Set play/pause icons.
    let playPauseButton = document.querySelector('.video-controls .play-pause');
    video.addEventListener("play", function(event) {
        playPauseButton.innerHTML = '⏸';
    });
    video.addEventListener("pause", function(event) {
        playPauseButton.innerHTML = '⏵';
    });
}

// Call when the video's metadata is loaded.
function metadataLoaded() {
    if (_has_duration()) {
        // Metadata has already been registered.
        return;
    }

    let video = document.querySelector('.main-video');
    let duration = video.duration;
    if (isNaN(duration)) {
        // Metadata has not been recieved from the server.
        return;
    }

    _set_duration(duration);
    setClipAbsolute(duration, false);

    // Set initial values for times.
    setCurrentTime(0);
    setClipAbsolute(0, true);
    setClipAbsolute(duration, false);
}

// Set the visual elements for the current time.
// Does not seek.
function setCurrentTime(secs) {
    // The duration (video metadata) load may not have triggered the event yet.
    metadataLoaded();

    // Bound the time.
    secs = _bound_video_time(secs);

    // Replace the seek input with the correctly formatted time.
    document.querySelector('.video-controls .current-time').value = formatTimeString(secs);

    // Update the progress bar.
    let proportion = 0.0;
    if (_has_duration()) {
        proportion = secs / _get_duration();
    }

    document.querySelector('.video-controls .progress-bar').value = proportion;
}

function videoSeekOffset(offset) {
    let video = document.querySelector('.main-video');

    let newTime = video.currentTime + offset;
    videoSeek(newTime);
}

function videoSeekProportional(element) {
    if (!_has_duration()) {
        return;
    }

    videoSeek(_get_duration() * element.value);
}

function videoSeekBoundingClick(element, event) {
    if (!_has_duration()) {
        return;
    }

    let boundingBox = element.getBoundingClientRect();
    let proportion = (event.x - boundingBox.x) / boundingBox.width;

    videoSeek(_get_duration() * proportion);
}

function videoSeek(value) {
    if ((typeof value) !== 'number') {
        value = validateTimeString(value.value);
    }

    if (value === undefined) {
        return;
    }

    value = _bound_video_time(value);

    document.querySelector('.main-video').currentTime = value;
    setCurrentTime(value);
}

function videoTogglePlay() {
    let video = document.querySelector('.main-video');

    if (video.paused || video.ended) {
        video.play();
    } else {
        video.pause();
    }
}

function setClipNow(isStart) {
    if (!_has_duration) {
        return;
    }

    let video = document.querySelector('.main-video');
    setClipAbsolute(video.currentTime, isStart);
}

function setClipProportional(value, isStart) {
    if (!_has_duration) {
        return;
    }

    if ((typeof value) !== 'number') {
        value = validateTimeString(value.value);
    }

    setClipAbsolute(value * _get_duration, isStart);
}

function setClipAbsolute(value, isStart) {
    if (!_has_duration) {
        return;
    }

    if ((typeof value) !== 'number') {
        value = validateTimeString(value.value);
    }

    if (value === undefined) {
        return;
    }

    let start = window.shark.media['clip-start'] ?? 0;
    let end = window.shark.media['clip-end'] ?? _get_duration();

    if (isStart) {
        start = value;
    } else {
        end = value;
    }

    // Correct ordering if a user crossed the values.
    let newStart = Math.min(start, end);
    let newEnd = Math.max(start, end);

    window.shark.media['clip-start'] = newStart;
    window.shark.media['clip-end'] = newEnd;

    document.querySelector('.video-controls .clip-start').value = formatTimeString(newStart);
    document.querySelector('.video-controls .clip-end').value = formatTimeString(newEnd);

    _updateClipHighlight()
}

// Use the clip start and end to compute and update the size of the clip highlight.
function _updateClipHighlight() {
    if (!_has_duration) {
        return;
    }

    let duration = _get_duration();
    if (duration <= 0) {
        return;
    }

    let start = window.shark.media['clip-start'] ?? 0;
    let end = window.shark.media['clip-end'] ?? _get_duration();

    let startPercent = 100.0 * (start / duration);
    let widthPercent = 100.0 * ((end - start) / duration);

    let highlight = document.querySelector('.video-controls-progress .clip-highlight');
    highlight.style.left = `${startPercent.toFixed(2)}%`;
    highlight.style.width = `${widthPercent.toFixed(2)}%`;
}

// Convert a time string (hh:mm:ss.ss) to just the total number of seconds.
// This does not do detailed validation, so strange cases are supported like:
// fractional hours/mins, negative values, mins/secs >= 60.
// If values/position are omitted, it is assumed that larger values are omitted first.
// So, mm:ss and ss are both allowed, but not hh.
function validateTimeString(text) {
    text = String(text).trim();
    if (text.length === 0) {
        return undefined;
    }

    let parts = text.split(':');
    if (parts.length > 3) {
        console.warn(`Too many time components in '${text}'. Max: 3, Found: ${parts.length}.`);
        return undefined;
    }

    let totalSecs = 0.0;
    for (let i = 0; i < parts.length; i++) {
        let value = parseFloat(parts[i].trim());
        if (isNaN(value)) {
            console.warn(`Failed to parse time '${text}'. Component at index ${i} is not a number: '${parts[i]}.`);
            return undefined;
        }

        parts[i] = value;
    }

    // Now that the values are clean, go through them in reverse order (so seconds are counted first).
    parts.reverse();
    for (let i = 0; i < parts.length; i++) {
        if (i === 0) {
            // Seconds
            totalSecs += parts[i];
        } else if (i === 1) {
            // Minutes
            totalSecs += (parts[i] * 60.0);
        } else {
            // Hours
            totalSecs += (parts[i] * 60.0 * 60.0);
        }
    }

    return totalSecs;
}

// The reverse of validateTimeString().
function formatTimeString(totalSecs, includeHours = false) {
    let parts = [];

    if (includeHours) {
        let hours = Math.floor(totalSecs / 60 / 60);
        totalSecs -= (hours * 60.0 * 60.0);
        parts.push(String(hours).padStart(2, '0'));
    }

    let mins = Math.floor(totalSecs / 60);
    totalSecs -= (mins * 60.0);
    parts.push(String(mins).padStart(2, '0'));

    parts.push((totalSecs).toFixed(2).padStart(5, '0'));

    return parts.join(':');
}

// Return a video time (seconds) bound by the duration of the video.
function _bound_video_time(secs) {
    let maxTime = Infinity;
    if (_has_duration()) {
        maxTime = _get_duration();
    }

    return Math.max(0.0, Math.min(maxTime, secs));
}

function _get_duration() {
    return window.shark.media['duration'];
}

function _has_duration() {
    return !isNaN(window.shark.media['duration']);
}

function _set_duration(value) {
    window.shark.media['duration'] = value;
}
