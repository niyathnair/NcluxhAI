# Storyverse Video Generator

This project generates videos from images and audio files using MoviePy, creating engaging visual stories from text-based scripts.

## Prerequisites

- Python 3.x
- FFmpeg
- ImageMagick

On macOS, you can install FFmpeg and ImageMagick using Homebrew:

bash
brew install ffmpeg imagemagick


## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/storyverse.git
   cd storyverse
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following content:
   ```
   FFMPEG_BINARY=path/to/ffmpeg
   IMAGEMAGICK_BINARY=path/to/convert
   ```
   Adjust the paths if your FFmpeg and ImageMagick binaries are located elsewhere.

## Project Structure
storyverse
├── result
│ └── {slug}
│ ├── images
│ │ ├── flux
│ │ │ └── generated_image_{id}.png
│ │ └── dalle
│ │ └── generated_image_{id}.png


## Usage

1. Ensure you have set up your environment variables in the `.env` file, including any necessary API keys for script generation, image generation, and audio generation services.

2. Prepare your topic and language. The default is set to:
   - Topic: "Lifestyle in Bengaluru"
   - Language: "English"

   You can modify these in the `s5_main_flow.py` file if needed.

3. Run the main flow script:
   ```bash
   python s5_main_flow.py
   ```

   This script will:
   - Generate a script based on the given topic and language
   - Generate images using both Flux and DALL-E
   - Generate audio for the script
   - Create two videos: one using Flux images and another using DALL-E images

4. The generated content will be saved in the `result/{slug}/` directory, where `{slug}` is a unique identifier for your generated story.

5. The final output will be two video files:
   - `result/{slug}/flux_FINAL_VIDEO.mp4` (using Flux images)
   - `result/{slug}/dalle_FINAL_VIDEO.mp4` (using DALL-E images)

You can customize the topic and language by modifying the variables in the `if __name__ == "__main__":` block of the `s5_main_flow.py` script.
