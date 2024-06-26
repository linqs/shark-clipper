# Shark Clipper

Shark Clipper is a tool to take screenshots from a video while maintaining the metadata and timing information in the video.

## Requirements

To run Shark Clipper you need:
 - [Python 3](https://www.python.org/downloads/)
 - [ffmpeg](https://ffmpeg.org/download.html)

## Usage

To run Shark Clipper, you first need to start with server:
```
python3 -m sharkclipper.cli.server

# OR
./scripts/run-server.sh
```
There are various options you can set for the server (use the `--help` flag to see them).

Next, open a web browser to the local address indicated by the server.
This is usually something like: [http://127.0.0.1:12345](http://127.0.0.1:12345).

In the webpage, you can select a video to work on.
Once a video is selected, it will need to be encoded so it can be used in a web browser.
This can take several minutes for large videos.

Once the video is ready, it will show on the screen and you can start taking screenshots.
You can take screenshots without the selection box (which will take a screenshot of the entire video screen),
or you can use the selection box and only take a picture of a section of the screen.

Once a screenshot is taken, you can see it and information about it below.
You can edit some attributes of the screenshot before saving.

Once you are happy with your screenshots and data, you can save your work.
This will write the encoded video, screenshots, and all metadata to your "output" directory
(which defaults to a directory called "out" in the same place you started the server).

## Notes

 - Currently, all times are shown in your local timezone (the one your computer uses).
