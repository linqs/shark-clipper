'use strict';

// Initialize the video controls and block until the video is ready.
function initVideoControls() {
    let video = document.querySelector('.main-video');
    video.load();

    // Register a handler for updating as we progress through the video.
    video.addEventListener("timeupdate", function(event) {
        setCurrentTime(video.currentTime);
    });

    // Set initial values for times.
    setCurrentTime(0);
    setClip(0, true);

    // Some browsers (often mobile) may not have the duration ready yet.
    if (!isNaN(video.duration)) {
        setEndTime();
    } else {
        video.addEventListener('loadedmetadata', function(event) {
            setEndTime();
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
function setEndTime() {
    let video = document.querySelector('.main-video');

    let duration = video.duration;
    if (isNaN(duration)) {
        return;
    }

    let progress = document.querySelector('.video-controls progress');

    // Check if we have already set the duration.
    if (progress.getAttribute("max")) {
        return;
    }

    setClip(duration, false);
    progress.setAttribute('max', duration);
}

// Set the visual elements for the current time.
// Does not seek.
function setCurrentTime(secs) {
    let video = document.querySelector('.main-video');
    let currentTimeInput = document.querySelector('.video-controls .current-time');

    // The duration (video metadata) may not be loaded yet,
    var maxTime = video.duration;
    if (isNaN(maxTime)) {
        maxTime = Infinity;
    } else {
        // Try to set the end time if we have duration information.
        setEndTime();
    }

    secs = Math.max(0, Math.min(maxTime, secs));

    currentTimeInput.value = formatTimeString(secs);

    // Replace the seek input with the correctly formatted time.
    currentTimeInput.value = formatTimeString(secs);

    // Update the progress bar.
    document.querySelector('.video-controls progress').value = secs;
}

function videoSeekOffset(offset) {
    let video = document.querySelector('.main-video');

    let newTime = video.currentTime + offset;
    videoSeek(newTime);
}

function videoSeekProgress(element, event) {
    let video = document.querySelector('.main-video');
    if (isNaN(video.duration)) {
        return;
    }

    let boundingBox = element.getBoundingClientRect();
    let proportion = (event.x - boundingBox.x) / boundingBox.width;

    videoSeek(video.duration * proportion);
}

function videoSeek(value) {
    if ((typeof value) !== 'number') {
        value = validateTimeString(value.value);
    }

    if (value === undefined) {
        return;
    }

    let video = document.querySelector('.main-video');

    value = Math.max(0, Math.min(video.duration, value))
    video.currentTime = value;

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

function setClip(value, isStart) {
    if ((typeof value) !== 'number') {
        value = validateTimeString(event.value);
    }

    if (value === undefined) {
        return;
    }

    let element = null;
    if (isStart) {
        element = document.querySelector('.video-controls .clip-start');
    } else {
        element = document.querySelector('.video-controls .clip-end');
    }

    element.value = formatTimeString(value);
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
function formatTimeString(totalSecs) {
    let parts = ['00', '00', '00.00'];

    let hours = Math.floor(totalSecs / 60 / 60);
    if (hours > 0) {
        totalSecs -= (hours * 60.0 * 60.0);
        parts[0] = String(hours).padStart('0', 2);
    }

    let mins = Math.floor(totalSecs / 60);
    if (mins > 0) {
        totalSecs -= (mins * 60.0);
        parts[1] = String(mins).padStart('0', 2);
    }

    parts[2] = (totalSecs).toFixed(2).padStart('0', 5);

    return parts.join(':');
}
