<div align="center">

# ⚡ Arrow
### High-Speed Video & Music Downloader for Linux

[![Linux](https://img.shields.io/badge/Platform-Linux%20(Wayland%20%2F%20X11)-22c55e?style=for-the-badge&logo=linux&logoColor=white)](https://www.kernel.org/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-8b5cf6?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![yt-dlp](https://img.shields.io/badge/Engine-yt--dlp-ff0000?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
[![FFmpeg](https://img.shields.io/badge/Processing-FFmpeg%20Multi--Core-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

<p align="center">
  <b>Arrow</b> is a modern, blazing-fast Linux desktop application designed to download videos and music from over 1,000+ platforms at the <b>absolute highest available video and audio quality</b>.
  <br />
  Built with a modern GNOME Libadwaita dark theme, native Wayland/X11 acceleration, multi-connection fragment pipelines, and persistent user configuration.
</p>

---

</div>

## 📑 Table of Contents

- [⚡ Why Arrow? (Speed & Performance)](#-why-arrow-speed--performance)
- [✨ Key Features](#-key-features)
- [🌐 Supported Platforms & Websites](#-supported-platforms--websites)
- [⚙️ How It Works (Internal Architecture)](#️-how-it-works-internal-architecture)
- [📂 Project Structure](#-project-structure)
- [🚀 Quick Start & Installation](#-quick-start--installation)
- [💻 Desktop Environment Integration](#-desktop-environment-integration)
- [🔧 Configuration & Persistence](#-configuration--persistence)
- [🧪 Testing](#-testing)
- [🤝 Contributing & License](#-contributing--license)

---

## ⚡ Why Arrow? (Speed & Performance)

Traditional downloaders download streams sequentially using a single HTTP connection and process video muxing on a single CPU thread. **Arrow** implements multi-tier performance optimizations that drastically shorten download and conversion times:

1. **8x Concurrent Fragment Pipeline**:
   - For DASH and HLS multi-part streams (YouTube, Vimeo, Twitch, etc.), Arrow pulls **8 chunks in parallel** across separate connection workers.
   - Boosts download speeds by **5x to 10x** compared to standard single-stream utilities.

2. **10 MB HTTP Buffer Sizing**:
   - Uses an optimized 10 MB chunk request size (`http_chunk_size: 10485760`) and 1 MB disk I/O write buffer (`buffersize: 1048576`) to eliminate server-side CDN rate limiting and cut system call overhead.

3. **Multi-Threaded FFmpeg Stream Muxing (`-threads 0`)**:
   - Post-processing (merging `bestvideo` + `bestaudio`, audio transcoding to MP3 320k, FLAC encoding, and metadata muxing) utilizes **all available CPU cores**, completing stream mergers in seconds.

4. **Lightning-Fast Media Inspection**:
   - Flat playlist extraction and manifest pre-filtering allow Arrow to retrieve titles, creators, durations, and album art preview in fractions of a second without downloading redundant metadata.
   - Built-in in-memory thumbnail cache eliminates repeated network requests.

5. **Asynchronous Non-Blocking UI Loop**:
   - Heavy network I/O and FFmpeg processing run on dedicated worker threads (`QThread`), communicating with the Qt event loop via thread-safe signals (`pyqtSignal`). The UI never freezes or stutters.

---

## ✨ Key Features

- 🎬 **Highest Available Video Fidelity**:
  - Automatically analyzes and combines the highest bitrate video stream (`bestvideo`) with the highest bitrate audio stream (`bestaudio`).
  - Supports **8K**, **4K UHD (2160p)**, **2K QHD (1440p)**, **Full HD (1080p)**, and **HD (720p)** with 60fps and HDR.
  - Lossless merging into standard **MP4** (universal playback), **MKV** (advanced multi-track), or **WEBM**.

- 🎵 **Studio-Grade Music / Audio Extraction**:
  - **MP3 (320 kbps CBR)**: Highest bit-rate MP3 audio with universal compatibility for all hardware players, car stereos, and mobile devices.
  - **FLAC**: Lossless studio master quality with 0% generational loss.
  - **M4A / AAC**: High-efficiency, modern Apple and mobile playback standard.
  - **OPUS**: Ultra-low-latency, next-gen audiophile codec.
  - **Original Audio Stream**: Direct stream extraction (pure 1:1 stream copy without re-encoding).
  - **Automatic Album Artwork & ID3 Tags**: Embeds cover art, artist name, track title, and chapter markers into the output audio file.

- 📁 **Custom Storage Directory Selection**:
  - User-configurable download location via the native Linux directory picker (`QFileDialog`).
  - Automatically remembers the last selected directory across sessions in `~/.config/arrow/config.json`.
  - One-click **"Open Folder"** button to view downloaded files directly in your default Linux file manager (`xdg-open`).

- 📊 **Real-Time Telemetry & Progress**:
  - Live percentage progress bar with smooth gradient styling.
  - Granular telemetry: **Download Speed** (e.g. `18.5 MB/s`), **ETA**, **Downloaded Bytes / Total Size**, and current operation status (*Turbo downloading*, *Muxing streams*, *Embedding ID3 tags*).
  - Clean **Cancel** button to safely abort tasks and clean up temporary chunks.

- 📜 **Download History & File Management**:
  - Keeps track of recent downloads with one-click buttons to play media, open containing folders, or delete files.
  - **Comprehensive Delete Options**:
    - **Delete Finished File**: A direct `Delete` button on completed downloads to immediately remove unwanted files from disk.
    - **History Item Delete**: Choose between *Delete File from Disk* (permanently cleans up the file) or *Remove from List Only* (preserves the local file).
    - **Clear History**: Clear past history with confirmation.

---

## 🌐 Supported Platforms & Websites

Arrow is powered by the battle-tested `yt-dlp` extraction engine, supporting **over 1,000+ streaming sites and media platforms**:

| Category | Supported Platforms & Services |
| :--- | :--- |
| **Video Sharing & 4K/8K** | **YouTube** (up to 8K, 60fps HDR, Shorts), **Vimeo** (1080p/4K), **Dailymotion**, **Bilibili**, **PeerTube**, **Rumble**, **Odysee**, **Loom** |
| **Music & Audio Streams** | **YouTube Music**, **SoundCloud** (High-Quality MP3/AAC), **Bandcamp** (Lossless/320k), **Mixcloud**, **Audiomack**, **Jamendo**, **Free Music Archive**, **Podcast RSS feeds** |
| **Social Media & Clips** | **TikTok** (HD without watermark where available), **Instagram** (Reels, Videos, Posts), **Twitter / X** (Highest bitrate MP4), **Reddit** (v.redd.it audio+video merged), **Facebook Video**, **Threads**, **Pinterest** |
| **Live Streaming & VODs** | **Twitch** (VODs, Highlights, Clips), **Kick**, **YouTube Live Recordings**, **AfreecaTV** |
| **Educational & Talks** | **TED Talks**, **Khan Academy**, **Coursera**, **MIT OpenCourseWare**, **Archive.org** (Internet Archive audio & video) |
| **Direct Media Links** | **MP4 / MKV / MP3 / M4A / FLAC / HLS / M3U8 / DASH streams**, Google Drive public shares, Dropbox direct links, Nextcloud media shares |

---

## ⚙️ How It Works (Internal Architecture)

```
                     ┌──────────────────────────────────────────────┐
                     │              Arrow User Interface            │
                     │          (Modern Dark PyQt6 Window)          │
                     └──────────────────────┬───────────────────────┘
                                            │
                     ┌──────────────────────┴───────────────────────┐
                     │           User Input: Media URL              │
                     └──────────────────────┬───────────────────────┘
                                            │
                     ┌──────────────────────▼───────────────────────┐
                     │     Asynchronous InfoFetchWorker (QThread)   │
                     │  - Fast flat extraction without manifests    │
                     │  - Extracts: Title, Artist, Duration, Views  │
                     │  - Pulls & caches high-resolution thumbnail  │
                     └──────────────────────┬───────────────────────┘
                                            │
                     ┌──────────────────────▼───────────────────────┐
                     │   User Mode & Directory Preferences Selected │
                     │  - Video Mode: 4K / 1080p / MP4 / MKV        │
                     │  - Audio Mode: MP3 320k / FLAC / M4A / OPUS  │
                     │  - Destination: ~/Downloads or custom folder │
                     └──────────────────────┬───────────────────────┘
                                            │
                     ┌──────────────────────▼───────────────────────┐
                     │       DownloadWorker Turbo Engine (QThread)  │
                     │                                              │
                     │  ┌────────────────────────────────────────┐  │
                     │  │ 8x Parallel Fragment Downloader (yt-dlp│  │
                     │  │ 10 MB HTTP Buffer Stream Pipeline      │  │
                     │  └───────────────────┬────────────────────┘  │
                     │                      │                       │
                     │  ┌───────────────────▼────────────────────┐  │
                     │  │ Multi-Core FFmpeg Post-Processing      │  │
                     │  │ - Video+Audio Lossless Muxing (-threads 0)│
                     │  │ - Audio Transcoding (MP3 320k / FLAC)  │  │
                     │  │ - ID3 Metadata & Album Cover Injection │  │
                     │  └───────────────────┬────────────────────┘  │
                     └──────────────────────┼───────────────────────┘
                                            │ (Thread-Safe Qt Signals)
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │             Real-Time Telemetry              │
                     │  - Speed (MB/s), ETA, Progress %, Size       │
                     │  - "Open Media" & "Show in Folder" Actions   │
                     │  - Persisted in ~/.config/arrow/config.json  │
                     └──────────────────────────────────────────────┘
```

### Module Breakdown

- **`main.py`**:
  Initializes application properties, desktop window managers (`arrow.desktop`), checks Wayland/X11 display sockets, handles DBus gracefully, and applies the custom global theme.
- **`app/config.py` (`ConfigManager`)**:
  Manages configuration saved at `~/.config/arrow/config.json`. Persists download folders, format preferences, turbo concurrency levels, and download history.
- **`app/info_fetcher.py` (`InfoFetchWorker`)**:
  Performs lightweight metadata inspection without downloading whole playlists or heavy manifests. Manages a high-resolution thumbnail cache.
- **`app/downloader.py` (`DownloadWorker`)**:
  Executes the download process on a background thread. Manages concurrency settings, 10MB chunk buffering, live status messages, multi-core FFmpeg execution, and cancellation tokens.
- **`app/ui/main_window.py` (`MainWindow`)**:
  Central UI controller coordinating URL inputs, preview card updates, directory selection, download triggers, and history management.
- **`app/ui/components.py`**:
  Modular UI widgets including `MediaPreviewWidget` (rounded thumbnail, duration badge, metadata), `DownloadProgressWidget` (live stats, cancel button, success banner), and `RecentDownloadsWidget`.
- **`app/ui/icons.py` (`IconFactory`)**:
  Custom vector icon generator rendering resolution-independent vector icons via `QPainter` (aerodynamic Arrow logo, play, music, video, folder, paste, download, refresh).
- **`app/ui/styles.py`**:
  Modern dark stylesheet with deep slate backgrounds (`#0b0f19`), elevated card surfaces (`#161f30`), and electric indigo/purple gradients.

---

## 📂 Project Structure

```text
yt_downloader/
├── main.py                     # Application entry point with Wayland/X11 auto-detection
├── run.sh                      # Executable Linux bash launcher
├── install_desktop.sh          # Desktop entry installer for GNOME / KDE application menu
├── arrow.desktop               # FreeDesktop application shortcut
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation & architecture guide
│
├── assets/
│   └── icon.png                # High-resolution 256x256 Arrow application logo
│
├── app/
│   ├── __init__.py             # Package initialization & version metadata
│   ├── config.py               # Settings & download history manager (~/.config/arrow/)
│   ├── downloader.py           # Multi-threaded download worker with 8x parallel chunks
│   ├── info_fetcher.py         # Asynchronous metadata & thumbnail preview engine
│   └── ui/
│       ├── __init__.py         # UI package initialization
│       ├── components.py       # Reusable UI cards, preview, progress & history widgets
│       ├── icons.py            # High-DPI QPainter vector icon factory
│       ├── main_window.py      # Main window layout, event routing & signal connectors
│       └── styles.py           # Modern dark Libadwaita-inspired stylesheet
│
└── tests/
    └── test_app.py             # 19 automated unit & integration tests
```

---

## 🚀 Quick Start & Installation

### Prerequisites

Ensure you have **Python 3.10+** and **FFmpeg** installed on your Linux distribution:

```bash
# Debian / Ubuntu / Linux Mint / Pop!_OS
sudo apt update && sudo apt install -y python3 python3-pip ffmpeg

# Fedora / RHEL
sudo dnf install -y python3 python3-pip ffmpeg

# Arch Linux / Manjaro
sudo pacman -S --needed python python-pip ffmpeg

# openSUSE
sudo zypper install python3 python3-pip ffmpeg
```

### 1. Clone & Enter Directory

```bash
git clone https://github.com/your-username/arrow.git
cd arrow
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

*(Dependencies: `PyQt6`, `yt-dlp`, `mutagen`, `Pillow`)*

### 3. Launch Arrow

Run the launcher script:
```bash
./run.sh
```

Or run directly with Python:
```bash
python3 main.py
```

---

## 💻 Desktop Environment Integration

To add Arrow to your Linux application menu (GNOME Dash, KDE Kickoff, XFCE Menu, Rofi, etc.) so you can search and launch it like a native system app:

```bash
./install_desktop.sh
```

This creates an application entry at `~/.local/share/applications/arrow.desktop` linked with the high-resolution vector icon.

---

## 🔧 Configuration & Persistence

Arrow stores user preferences and recent history in:

```text
~/.config/arrow/config.json
```

### Example `config.json`

```json
{
  "download_dir": "/home/username/Downloads",
  "media_mode": "video",
  "video_quality": "best",
  "video_format": "mp4",
  "audio_format": "mp3",
  "audio_quality": "320",
  "embed_thumbnail": true,
  "embed_metadata": true,
  "concurrent_fragments": 8,
  "history": [
    {
      "title": "Stunning 4K Nature Showcase",
      "file_path": "/home/username/Downloads/Stunning 4K Nature Showcase [xyz123].mp4",
      "file_size": 154829104,
      "file_size_str": "147.6 MB",
      "mode": "video",
      "format": "mp4"
    }
  ]
}
```

---

## 🧪 Testing

Arrow includes a unit and integration test suite covering configuration persistence, number/duration formatters, turbo options, vector icon generation, and UI interactions in headless offscreen mode:

```bash
python3 -m unittest discover -s tests
```

Expected output:
```text
...................
----------------------------------------------------------------------
Ran 19 tests in 0.233s

OK
```

---

## 🤝 Contributing & License

Contributions, feature requests, and bug reports are welcome! Feel free to open an issue or submit a pull request.

Released under the **MIT License**.
