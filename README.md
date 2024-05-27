![icon](vidalign/assets/icon-wide.png)

A tool to perform multi-camera video temporal alignment and clip extraction.

## Installation

Install Anaconda [here](https://www.anaconda.com/download/success) or Miniconda [here](https://docs.anaconda.com/free/miniconda/miniconda-install/), then run the following commands:

```bash
conda env create -f environment.yml;
```

## Usage

```bash
conda activate vidalign;
python -m vidalign;
```

### Overview

![screenshot](vidalign/assets/ui_screenshot.png)

1. **Video Player**: Basic video playback and frame seeking, with support for panning and zooming using the mouse. Take note of the keyboard shortcuts on the playback buttons, as they'll be your best friend.
2. **Video Dropper**: Drop video files and folders here to import them. Directories will be descended recursively looking for video files. At the time of writing the supported extensions are: `{mp4, avi, mkv, mov, mxf}`.
3. **Video Info**: Information about the currently selected video, with buttons to set metadata. See [workflow](#workflow) below for more detail.
4. **Video List**: List of imported videos. If there are no empty cells here, you've done what's needed for the videos. _Ensure you don't set the same alias for multiple videos!_
5. **Clip Info**: Information about the currently selected clip, with buttons to set the start and end frames, and other useful things. See [workflow](#workflow) below for more detail.
6. **Clip List**: List of clips videos. If there are no empty cells here, you've done what's needed for the clips. _Ensure you don't set the same clip name for multiple clips!_
7. **Video/Clip File Utilities**: Set the output directory for your exported clips, and save/load/reset the videos and clips. Handy if you need to save your progress and return to it later.
8. **Encoder Settings**: Here you can choose your encoder application (just FFmpeg at this point), configure some of the encoding parameters, and save/load/reset them. If you figure out parameters that you like, export them and load them at the start of each session.

### Workflow

1. Load some videos by dragging them onto the video dropper.
   1. You can optionally filter the video filenames using the text box.
1. For each video:
   1. Select it and click _Set alias_. Give it a recognisable name like "left_camera".
   1. Scrub through the video and find a frame with a clearly visible event which can be used for time-synchronisation across cameras. Click _Set sync frame_. Typically you would use the flash of a light or a clap.
1. For each desired clip:
   1. Click _New clip_. The clip's start frame will be automatically set at the current frame, but this can be changed by navigating to the desired frame and clicking _Set_; same goes for the end frame.
   1. Rename the clip to something recognisable like "calibration" or "run_1".
1. Set your output directory with the button on the right. The videos will be output here with filenames like `{output_dir}/{clip_name}_{video_alias}.{ext}`
   - Save the videos/clips configuration to file if you want to be safe.
1. Open up the encoder options and check that you're happy with them.
   - Instead you can load a previous encoder configuration from file if you have one prepared.
   - I like using PyAV for encoding, but FFmpeg is also a good choice as it's more tried and tested.
1. View the encoder commands to check that everything is as expected.
   - You can copy-paste them elsewhere if you want to make any changes that the app can't facilitate.
   - This is only available for FFmpeg at the moment.
1. Run the encode commands by clicking _Run encode commands_.
1. Have a coffee and come back when it's done!

### Cropping

This tool also supports spatially cropping a video over time. This is visually editable by interacting with the video player.

- **Move the bounding box** by holding <ctrl>, clicking and dragging it.
- **Resize the bounding box horizontally** by holding <ctrl> and scrolling the mouse wheel.
- **Resize the bounding box vertically** by holding <ctrl>+<shift> and scrolling the mouse wheel.

A red bounding box indicates that a bounding box has been set on the current frame. A yellow bounding box indicates that the current bounding box location is being interpolated between the previous and next annotated frames.

Right-clicking on the video player will clear the bounding box for the current frame.

### Contributing

Please feel free to open an issue or pull request if you have any suggestions or find any bugs.
