# applemusic-mv-downloader

A graphical Apple Music music video downloader, developed based on [gamdl](https://github.com/glomatico/gamdl).  
It provides a visual interface and common features such as resolution / codec / container format selection, cover saving, and more.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)  
![Version](https://img.shields.io/badge/version-1.1-blue.svg)

**Important note:** This tool is only a GUI wrapper for gamdl and does not include any functionality for bypassing authorization or circumventing paid protection. When downloading Apple Music content, please comply with local laws and Apple’s Terms of Service, and use an account that is logged in and has an active Apple Music subscription via Cookies.

## Table of Contents

- [Feature Overview](#feature-overview)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Interface Description](#interface-description)
- [FAQ](#faq)
- [Privacy and Security](#privacy-and-security)
- [Acknowledgements](#acknowledgements)
- [License](#license)

## Feature Overview

- Supports single or multiple Apple Music links, one per line.
- Supports one-click downloading of all content from an album or artist.
- Supports selecting video resolution, video codec priority order (h264 / h265), and output container format (m4v / mp4).
- Supports specifying the path to the FFmpeg executable if remuxing is required.
- Supports saving the cover as a separate file. By default, gamdl also embeds the cover into the media tags.
- Temporary directory strategy: prefers short paths to reduce the risk of fragment write failures on Windows.
- Automatic log output to the GUI log window, making it easier to check errors and progress information.

## Configuration

- Python 3.10 or later
- A valid Apple Music subscription account
- Apple Music Cookies exported from your browser in Netscape format, usually named `cookies.txt`
- Install the gamdl Python package:

```bash
pip install gamdl
```

- Optional: FFmpeg, if remuxing or certain decryption processes are required. Place FFmpeg in your system PATH or specify its executable path in the interface.
- Optional but recommended: install the latest yt-dlp, as gamdl may call it internally:

```bash
pip install yt-dlp
```

**Windows note:** If your output directory or temporary directory is located on a sync drive such as OneDrive, it is strongly recommended to change the temporary directory to a local short path. The script prefers `C:\gamdl_temp` by default. Also add that directory to the exclusion list of your antivirus or sync tool to prevent downloaded fragments from being automatically deleted or locked, which may cause download failures.

## Quick Start

1. Clone this project:

```bash
git clone https://github.com/pglp006688/applemusic-mv-downloader.git
cd applemusic-mv-downloader
```

2. Run the program in your terminal after installing dependencies:

```bash
python amv_downloader_gui.py
```

## Interface Description

- **Apple Music links:** Enter one URL per line. Multiple links are supported.
- **Cookies file:** Select a Netscape-format `cookies.txt` file. This is required.
- **Output directory:** The final location where media files are saved.
- **FFmpeg:** Optional. If not specified, the program will use FFmpeg from the system PATH if available.
- **Video resolution:** Select the desired maximum resolution. The script will try to choose according to priority.
- **Container format:** Choose `m4v` or `mp4`. `m4v` preserves some Apple-specific features.
- **Video codec priority:** Specify whether h264 or h265 should be preferred.
- **Save cover:** Whether to save the cover as a separate file, such as `Cover.jpg` or `Cover.png`.
- **Start Download / Stop:** Control the download task.

## FAQ

**Q: The downloaded file is very small, for example around 50KB, and is not a video.**

A: This usually means the download was incomplete. yt-dlp may have failed while merging or writing fragments. You can try the original gamdl version.

**Q: Why does “Requested format is not available” sometimes appear?**

A: The requested codec or resolution is not available for that media. Try adjusting the video codec priority or lowering the resolution.

## Privacy and Security

This tool logs in to Apple Music using a Cookies file provided by the user. Cookies contain sensitive information. Please keep them secure and do not share them casually. It is recommended to use this tool only in a trusted local environment.

Do not upload Cookies to public networks or third-party services. The script does not actively upload or send Cookies or downloaded content to any remote server.

## Acknowledgements

This GUI script is a wrapper around the functionality of the open-source project gamdl by glomatico. gamdl provides the core capabilities for downloading, stream parsing, and decryption logic. For more implementation details, please refer to the gamdl repository and documentation.

This script uses and depends on third-party open-source components such as gamdl, yt-dlp, and FFmpeg. Please comply with their respective licenses and terms.

## License

This GUI script, as described in this README, is released under the MIT License.

You may freely use, modify, and distribute it, provided that the copyright notice and license notice are retained.

pglp006688 By
