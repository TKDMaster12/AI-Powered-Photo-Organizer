import os
import hashlib
import base64
from pathlib import Path
from openai import OpenAI
from models import PhotoMetadata
import piexif
from PIL import Image
from PIL import PngImagePlugin

client = OpenAI()

def calculate_hash(file_path):
    """Returns the SHA-256 hash of a file to find exact duplicates."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()
    
def encode_image(image_path):
    """Encodes an image to base64 so it can be sent to the AI."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_photo(image_path: str) -> PhotoMetadata:
    """Sends the actual image pixels to GPT-4o-mini for visual analysis."""
    print(f"AI Visually Analyzing: {os.path.basename(image_path)}")
    
    # Get the base64 string
    base64_image = encode_image(image_path)
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": "You are a professional photo organizer. View the image and provide structured metadata."
            },
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": "Analyze this photo for organization purposes."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        response_format=PhotoMetadata,
    )
    return response.choices[0].message.parsed

def bake_jpeg_metadata(image_path, metadata: PhotoMetadata):
    """Bakes AI analysis directly into the image's EXIF data."""
    try:
        # Load existing exif data or create empty if none exists
        exif_dict = piexif.load(image_path)
        
        # 0th IFD: Image Description
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = metadata.description.encode('utf-8')
        
        # Exif IFD: User Comment
        comment_str = f"Quality: {metadata.quality_score}/10 | Clutter: {metadata.is_clutter} | Tags: {', '.join(metadata.tags)}"
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = comment_str.encode('utf-8')
        
        # Convert back to bytes and insert into the image
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, image_path)
        print(f"   ✓ JPEG Metadata baked into {os.path.basename(image_path)}")
    except Exception as e:
        print(f"   × Failed to bake JPEG metadata: {e}")

def bake_png_metadata(image_path: str, metadata: PhotoMetadata):
    """Bakes AI analysis into PNG files using PNG text chunks."""
    try:
        img = Image.open(image_path)
        
        # PNGs use key-value pairs called 'chunks'
        meta = PngImagePlugin.PngInfo()
        meta.add_text("Description", metadata.description)
        meta.add_text("Tags", ", ".join(metadata.tags))
        meta.add_text("QualityScore", str(metadata.quality_score))
        meta.add_text("IsClutter", str(metadata.is_clutter))

        # We must 'save' the image to write the metadata chunks
        img.save(image_path, pnginfo=meta)
        print(f"   ✓ PNG Metadata baked into {os.path.basename(image_path)}")
    except Exception as e:
        print(f"   × Failed to bake PNG metadata: {e}")

def process_folder(target_folder: str):
    path = Path(target_folder)
    seen_hashes = {}
    unique_photos = []
    duplicates = []
    
    # Define supported extensions
    extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

    # Step 1: Detect Exact Duplicates
    print("\n--- Scanning for exact duplicates (JPG, PNG, GIF, BMP) ---")
    for file in path.iterdir():
        if file.suffix.lower() in extensions:
            file_hash = calculate_hash(file)
            if file_hash in seen_hashes:
                print(f"Duplicate found: {file.name} is the same as {seen_hashes[file_hash]}")
                duplicates.append(file)
            else:
                seen_hashes[file_hash] = file.name
                unique_photos.append(file)

    # Step 2: Prompt to delete duplicates
    if duplicates:
        confirm = input(f"\nFound {len(duplicates)} exact duplicates. Delete them? (y/n): ")
        if confirm.lower() == 'y':
            for double in duplicates:
                os.remove(double)
            print("Duplicates deleted.")

    # Step 3: AI Organization & Clutter Handling
    print("\n--- Organizing remaining photos ---")
    for photo_path in unique_photos:
        str_path = str(photo_path)
        ext = photo_path.suffix.lower()
        
        # Get AI Analysis (Visual)
        analysis = analyze_photo(str_path)
        
        # Bake metadata first so the "reasoning" stays with the file
        if ext in {'.jpg', '.jpeg'}:
            bake_jpeg_metadata(str_path, analysis)
        elif ext == '.png':
            bake_png_metadata(str_path, analysis)
        else:
            print(f"   ! Metadata baking not supported for {ext}. Moving based on AI analysis only.")
        
        print(f"File: {photo_path.name}")
        print(f"  - Description: {analysis.description}")
        print(f"  - Tags: {analysis.tags}")
        
		# Logic for determining the destination
        if analysis.is_clutter or analysis.quality_score < 4:
            destination_folder = "Review_Required"
            print(f"  [!] Flagged as Clutter: {analysis.reasoning}")
        else:
            destination_folder = analysis.suggested_folder
            print(f"  [+] Organized as: {destination_folder}")
        # Create directory and move
        target_dir = path / destination_folder
        target_dir.mkdir(exist_ok=True)
        
        # Move the file (now with updated metadata)
        new_path = target_dir / photo_path.name
        photo_path.rename(new_path)
        
        print(f"   Moved {photo_path.name} -> {destination_folder}/")

if __name__ == "__main__":
    # Change this to your local folder path
    process_folder("./my_photos")