# Shark Clipper

Shark Clipper is a tool to take screenshots from a video while maintaining the metadata and timing information in the video.

 - [Requirements](#requirements)
 - [Installation / Setup](#installation---setup)
   - [Using a Prebuilt Binary](#using-a-prebuilt-binary)
     - [Using the Linux Prebuilt Binary](#using-the-linux-prebuilt-binary)
     - [Using the Mac Prebuilt Binary](#using-the-mac-prebuilt-binary)
     - [Using the Windows Prebuilt Binary](#using-the-windows-prebuilt-binary)
   - [From Source](#from-source)
 - [Usage](#usage)
   - [Video Controls](#video-controls)
   - [Keyboard Shortcuts](#keyboard-shortcuts)
 - [Notes](#notes)

## Requirements

To run Shark Clipper you need:
 - [Python 3](https://www.python.org/downloads/)
 - [FFmpeg](https://ffmpeg.org/download.html)

## Installation / Setup

### Using a Prebuilt Binary

We provide prebuilt binaries for Shark Clipper that support various operating systems.
All releases can be viewed on the [releases page](https://github.com/linqs/shark-clipper/releases).
This document will assume that you are specifically using the [latest prebuilt releases](https://github.com/linqs/shark-clipper/releases/tag/latest-release).
These "latest" builds are built automatically whenever new code is added.
They have all the newest features, but are not guaranteed to be stable.

Prebuilt binaries include all the required dependencies (like Python and FFmpeg).

OS-specific instructions will be provided bellow,
but here are the general steps for using a prebuilt binary.

1) Go to the [latest prebuilt releases page](https://github.com/linqs/shark-clipper/releases/tag/latest-release)
and download the file under "Assets" that best matches your machine.

2) Set the correct permissions for your downloaded binary.
Operating systems will do this differently,
see below for os-specific instructions.

3) Run the binary in a terminal.

4) Navigate a web browser to the address indicated in the binary's output,
and use the Shark Clipper as outlined in the [Usage section](#usage).
The default address for the Shark Clipper is http://127.0.0.1:12345 .

#### Using the Linux Prebuilt Binary

You will need to set execute permissions on the Linux prebuilt binary, e.g.:
```
chmod +x shark-clipper-linux-x64-latest.bin
```

After that, you may run the binary as any normal program:
```
./shark-clipper-linux-x64-latest.bin
```

#### Using the Mac Prebuilt Binary

Mac requires additional security steps to run the prebuilt binary.
These steps need to be done every time a new binary is downloaded and run for the first time.
Running binary files is best done via the command line.
If you're not familiar with the terminal, you can use [this guide](https://gomakethings.com/navigating-the-file-system-with-terminal/)
to get started.
For a more comprehensive command line guide refer to MIT's [Missing Semester course](https://missing.csail.mit.edu/2020/course-shell/).

1) Unzip the downloaded shark-clipper-macos-x64-latest.zip file.

2) Open the Terminal application and navigate to the directory where shark-clipper-macos-x64-latest.bin is located e.g. if the file is in the "Downloads" folder:
```
cd ~/Downloads
```

3) Set execute permissions on the Mac prebuilt binary, e.g.:
```
chmod +x shark-clipper-macos-x64-latest.bin
```

4) Run the binary as any normal program:
```
./shark-clipper-macos-x64-latest.bin
```

5) Click "OK" on a popup that may appear saying that the file cannot be opened because Apple cannot check it for malicious software.

6) Open System Settings and navigate to the "Privacy & Security" tab.

7) Scroll down to the "Security" section.
A message should appear stating that shark-clipper-macos-x64-latest.bin was blocked because it is not from an identified developer.
Click the "Allow Anyway" button.
You may be required to provide a password.

8) Return to the terminal and re-run the binary:
```
./shark-clipper-macos-x64-latest.bin
```

9) Click "Open" on a popup that may appear again warning about running the file.

#### Using the Windows Prebuilt Binary

Windows requires some additional security steps to run the prebuilt binary.
The first of these steps needs to be done every time a new binary is downloaded,
and the second step will need to be done every time you run the Shark Clipper server.

1) Double-Click the Windows prebuilt binary.

2) If the "Windows Protected" window pops up, click "More Info" at the bottom and then click "Run Anyway".

3) If the "Windows Security Alert" window pops up, check "Private Network", uncheck "Public Network", and then click "Allow Access".

### From Source

Follow these instructions to run Shark Clipper from source.

1) Ensure that the above [requirements](#requirements) are installed.

2) Get this repository.
You can download the repo as a zip, but we will demonstrate getting it using git.
```
# Using SSH keys.
git@github.com:linqs/shark-clipper.git

# Using HTTPS (no authentication required).
git clone https://github.com/linqs/shark-clipper.git
```

3) Install the project dependencies (and dev dependencies).
```
pip install -r requirements.txt -r requirements-dev.txt
```

4) Run the Shark Clipper server:
```
python3 -m sharkclipper.cli.server

# OR
./scripts/run-server.sh
```
Use the `--help` flag to see all the possible options.

5) If the server runs, then all your setup is complete.

## Usage

Once the Shark Clipper server is started (see the [Installation / Setup](#installation--setup) section),
open a web browser to the local address indicated by the server.
This is usually something like: [http://127.0.0.1:12345](http://127.0.0.1:12345).

In the webpage, you can select a video to work on.
Once a video is selected, it will need to be encoded so it can be used in a web browser.
This can take several minutes for large videos.

Once the video is ready, it will show on the screen and you can start taking screenshots and setting your clip boundaries.

A video's "clip" is a special portion of the video that is put in the output directory with the "clip" suffix
(the full original video is also written).
The clip's duration is shows by the highlighted section of the video's progress bar.
By default, the entire video is set as the clip.
You can use the video control's to set the clip's boundaries,
see the [Video Controls](#video-controls) section.

You can take screenshots without the selection box (which will take a screenshot of the entire video screen),
or you can use the selection box and only take a picture of a section of the screen.
Once a screenshot is taken, you can see it and information about it below.
You can edit some attributes of the screenshot before saving.

Once you are happy with your screenshots and data, you can save your work.
This will write the encoded video, screenshots, and all metadata to your "output" directory
(which defaults to a directory called "out" in the same place you started the server).

### Video Controls

You can control the video player using the controls below the video.

The progress bar (directly below the video) shows where in the video your are currently looking.
You may click on the progress bar or slide the thump to seek to where you wish in the video.
The highlighted portion of the progress bar shows the current clip selection.

Below the progress bar is the clip boundary buttons as well as the numerical timing information.
From left to right, the elements are:
 - "Clip Start" Button -- Clicking this button sets the start boundary of the clip to the current time.
 - Clip Start Time -- This field shows the time (MM:SS.ss) of the clip's start boundary.
   You can manually edit this field (any bad input is discarded).
 - Current Time -- This field shows the current position (MM:SS.ss) in the video.
   You can manually edit this field (any bad input is discarded).
 - Clip End Time -- This field shows the time (MM:SS.ss) of the clip's end boundary.
   You can manually edit this field (any bad input is discarded).
 - "Clip End" Button -- Clicking this button sets the end boundary of the clip to the current time.

The next section are video control buttons.
From left to right, the buttons are:
 - `<<` -- Seek backwards a large amount.
 - `<` -- Seek backwards a small amount.
 - `⏵` / `⏸` -- Toggle play/pause.
 - `>` -- Seek forwards a small amount.
 - `>>` -- Seek forwards a large amount.

### Keyboard Shortcuts

| Key             | Action |
|-----------------|--------|
| `b`             | Toggle the selection box. |
| `f`             | Take a screenshot of the video at the current frame. |
| `s`             | Save the video and all screenshots to the output directory. |
| `spacebar`      | Toggle play/pause. |
| `←`             | Seek backwards a large amount. |
| `→`             | Seek forwards a large amount. |
| `shift` + `←`   | Seek backwards a small amount. |
| `shift` + `→`   | Seek forwards a small amount. |
| `control` + `←` | Seek backwards a very small amount. |
| `control` + `→` | Seek forwards a very small amount. |
| `home`          | Seek to the beginning. |
| `end`           | Seek to the end. |

## Notes

 - Currently, all times are shown in your local timezone (the one your computer uses).
