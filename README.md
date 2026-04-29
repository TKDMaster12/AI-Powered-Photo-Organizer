# AI-Powered Photo Organizer

## Introduction
The **AI-Powered Photo Organizer** is an intelligent utility designed to declutter and categorize personal image libraries. By leveraging OpenAI's `gpt-4o-mini` vision capabilities, the application goes beyond simple file management to understand the actual content of your photos. It automatically identifies duplicates, flags "clutter" (like screenshots or blurry shots), and "bakes" AI-generated metadata directly into the image files using EXIF standards.

## Key Features
- **Exact Duplicate Detection:** Uses SHA-256 hashing to find bit-for-bit identical files instantly.
- **Visual AI Analysis:** Utilizes GPT-4o-mini to "see" images and generate descriptions, tags, and quality scores.
- **Metadata Baking:** Permanently embeds AI descriptions and tags into the image's EXIF data (UserComment and ImageDescription fields).
- **Smart Categorization:** Automatically moves photos into folders based on AI-suggested categories (e.g., Travel, Pets, Receipts).
- **Clutter Management:** Identifies and isolates low-quality images or temporary screenshots into a `Review_Required` folder.

## Prerequisites
- Python 3.11 or higher
- OpenAI API key
- Standard image formats (currently optimized for `.jpg`, `.jpeg` and `.png`)

## Installation

### Setup
1. Navigate to the project directory:
```bash
cd photo-organizer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\\Scripts\\activate
```

3. Install the required dependencies:
```bash
pip install openai piexif Pillow pydantic
```

4. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'  # On Windows, use: set OPENAI_API_KEY=your-api-key-here
```

## Usage
Ensure your photos are in the target directory (default is `./my_photos`) and run the main script:

```bash
python main.py
```

### The Workflow
1. **Hash Check:** Identifies exact duplicates and prompts for deletion.
2. **AI Vision:** Unique images are analyzed visually by GPT-4o-mini.
3. **Baking:** Metadata is written directly into the file's EXIF headers.
4. **Filing:** Files are moved to organized subfolders or the `Review_Required` folder based on quality and content.

## License
This project is provided "as is" under the MIT License. Feel free to use, modify, and distribute it as you wish.