# Aparat Downloader Manager (AparatDM)

Aparat Downloader Manager (AparatDM) is a Python-based application for downloading videos from the Aparat platform. It provides a 
graphical user interface (GUI) for managing video downloads, including support for playlists, channels, and individual videos. 

**If you're tired of videos being downloaded with unclear names, or if you want to download a playlist all at once while preserving the order and title of each video, this program is perfect for you**.

The application also supports multi-threaded downloads, quality selection, and pause and resume support.

## Features

- **Download Videos**: Download individual videos, playlists, or entire channels from Aparat.
- **Quality Selection**: Choose from multiple video qualities (1080p, 720p, 480p, etc.).
- **GUI Interface**: User-friendly interface built with `ttkbootstrap` and `Tkinter`.
- **Resume Support**: Resume downloads and save progress.
- **Clipboard Monitoring**: Automatically detect and add Aparat links copied to the clipboard.
- **Thumbnail Previews**: Display video thumbnails in the GUI.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Aliround/AparatDM.git
   cd AparatDM
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Launch the application by running `main.py`.
2. Just copy a video or playlist link to your clipboard,
The program will automatically recognize and add it to the download queue.

3. Use the GUI to manage your downloads. You can start, pause, or cancel downloads as needed.

4. In the top panel you can select the default video quality for the videos you are going to add.
Or you can change the quality individualy for every video

5. You can change the default path as well


## Project Structure

```
AparatDM/
├── aparat_dl/
│   ├── gui.py          # GUI implementation
│   ├── video.py        # Video class for handling video metadata and downloads
│   ├── videolist.py    # VideoList class for managing multiple videos
│   ├── utils.py        # Utility functions
├── main.py             # Entry point for the application
├── README.md           # Project documentation
└── requirements.txt    # Python dependencies
```

## Dependencies

- `requests`
- `ttkbootstrap`
- `Pillow`
- `pyperclip`
- `pypdl`

Install all dependencies using:
```bash
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

## License

I am new here just use it and send salawat and dua for me ❤️.


