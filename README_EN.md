# Whisper Japanese Speech Transcription Tool (whisper-transcriber-ja)

This project provides a simple way to transcribe audio files using OpenAI's Whisper models. Although the default language is Japanese, the tool can be used for other languages by changing command line options.

## Features
- Supports multiple audio formats (MP3, WAV, M4A, FLAC, AAC, OGG)
- Selectable model sizes: tiny, base, small, medium, large, turbo
- GPU acceleration with CUDA when available
- Batch processing for multiple files
- Processed files are moved to a dedicated folder
- Optional web interface

## Quick Setup
1. Install Python 3.8 or later.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv myenv
   source myenv/bin/activate        # Windows: myenv\Scripts\activate
   pip install -r requirements.txt
   ```
   If you want GPU support, install the appropriate CUDA version of PyTorch as described in `CUDA_SETUP.md`.

## Running the Demo
Execute the included demo script to see a sample transcription:
```bash
./run_demo.sh
```
If the sample audio cannot be downloaded automatically, place an audio file named `demo_sample.mp3` in the project directory.

## Command Line Usage
Place audio files in the `audiofile` folder and run:
```bash
python audio_transcribe.py --model base --language ja
```
Adjust `--model` and `--language` as needed. Use `--device cuda` and `--compute_type float16` for faster GPU processing if available.

## Web Interface
Run the web application for a browser‑based GUI:
```bash
./run_webapp.sh
```
Then open `http://localhost:8080` in your browser.

## License
This project is released under the MIT License.
