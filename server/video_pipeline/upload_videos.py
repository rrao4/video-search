#!/usr/bin/env python3
"""
Script to upload video names and URLs from videos.json to the database.
Also converts videos to infinitely looping WebP format and saves them locally.
Reads from ./data/videos.json relative to this script's directory
and creates Video records in the database with corresponding WebP files.
"""

import sys
import json
import os
import shutil
import subprocess
import requests
from typing import List, Dict, Any
from pathlib import Path

# Configuration constants
MAX_VIDEOS_TO_PROCESS = 20  # Maximum number of videos to process
WEBP_QUALITY = 80           # Quality setting for WebP (0-100)

# Add the server directory to the Python path so we can import from it
current_dir = Path(__file__).resolve().parent
server_dir = current_dir.parent
if str(server_dir) not in sys.path:
    sys.path.insert(0, str(server_dir))

from app import create_app
from extensions import db
from db.models import Video

def clear_output_directories():
    """Clear previous output directories to start fresh."""
    current_dir = Path(__file__).parent
    temp_dir = current_dir / "temp_videos"
    webp_dir = current_dir / "webp_output"
    
    # Remove and recreate temp_videos directory
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print(f"Cleared {temp_dir}")
    temp_dir.mkdir(exist_ok=True)
    
    # Remove and recreate webp_output directory
    if webp_dir.exists():
        shutil.rmtree(webp_dir)
        print(f"Cleared {webp_dir}")
    webp_dir.mkdir(exist_ok=True)
    
    print("Output directories cleared and recreated")

def download_video(video_url: str, output_path: str) -> bool:
    """Download video from URL to local path using requests with proper SSL handling."""
    try:
        print(f"  Downloading {video_url}...")
        
        # Use browser-like headers to avoid bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(video_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        # Download in chunks
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Verify file was downloaded and has content
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"  Downloaded ({os.path.getsize(output_path)} bytes)")
            return True
        else:
            print(f"  Download failed: file is empty or doesn't exist")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  Request error downloading: {e}")
        return False
    except Exception as e:
        print(f"  Error downloading: {e}")
        return False

def convert_to_webp(input_path: str, output_path: str) -> bool:
    """Convert video to infinitely looping WebP using FFmpeg."""
    try:
        print(f"  Converting to WebP...")
        
        # FFmpeg command to convert video to infinitely looping WebP
        # No scaling filter - preserves original video dimensions
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libwebp',
            '-loop', '0',           # Infinite looping
            '-q:v', str(WEBP_QUALITY),  # Quality setting
            '-preset', 'default',
            '-y',                   # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  Successfully converted to WebP")
            return True
        else:
            print(f"  FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  Error converting to WebP: {e}")
        return False

def cleanup_temp_file(file_path: str) -> None:
    """Remove temporary file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"  Warning: Could not clean up {file_path}: {e}")

def load_videos_json(file_path: str) -> List[Dict[str, Any]]:
    """Load videos data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} videos from {file_path}")
        return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return []

def upload_videos_to_db(videos_data: List[Dict[str, Any]]) -> None:
    """Upload video data to the database and convert to WebP."""
    current_dir = Path(__file__).parent
    temp_dir = current_dir / "temp_videos"
    webp_dir = current_dir / "webp_output"
    
    uploaded_count = 0
    skipped_count = 0
    error_count = 0
    webp_success_count = 0
    webp_error_count = 0
    
    # Limit to MAX_VIDEOS_TO_PROCESS
    videos_to_process = videos_data[:MAX_VIDEOS_TO_PROCESS]
    print(f"Processing {len(videos_to_process)} videos (limited to {MAX_VIDEOS_TO_PROCESS})")
    
    for i, video_data in enumerate(videos_to_process, 1):
        try:
            video_name = video_data.get('video_name')
            video_url = video_data.get('video_url')
            
            print(f"\n[{i}/{len(videos_to_process)}] Processing: {video_name}")
            
            if not video_name or not video_url:
                print(f"  Warning: Missing video_name or video_url")
                skipped_count += 1
                continue
            
            # Check if video already exists (by path/URL)
            existing_video = Video.query.filter_by(path=video_url).first()
            if existing_video:
                print(f"  Skipping - already exists with ID {existing_video.id}")
                skipped_count += 1
                continue
            
            # Generate file paths
            temp_video_path = temp_dir / video_name
            webp_name = video_name.rsplit('.', 1)[0] + '.webp'
            webp_output_path = webp_dir / webp_name
            
            # Download and convert video to WebP
            webp_success = False
            try:
                if download_video(video_url, str(temp_video_path)):
                    if convert_to_webp(str(temp_video_path), str(webp_output_path)):
                        webp_success = True
                        webp_success_count += 1
                        print(f"  ✅ WebP conversion successful")
                    else:
                        webp_error_count += 1
                        print(f"  ❌ WebP conversion failed")
                else:
                    webp_error_count += 1
                    print(f"  ❌ Video download failed")
            except Exception as e:
                webp_error_count += 1
                print(f"  ❌ WebP processing error: {e}")
            finally:
                # Always clean up temporary video file
                cleanup_temp_file(str(temp_video_path))
            
            # Create database record regardless of WebP success
            # In the future, you might want to store webp_path in the database
            new_video = Video(
                name=video_name,
                path=video_url  # Using path field to store the video URL
                # TODO: Add webp_path field to store WebP file path/URL
            )
            
            db.session.add(new_video)
            uploaded_count += 1
            print(f"  ✅ Database record created")
            
            # Commit every 10 records to avoid memory issues and provide progress
            if uploaded_count % 10 == 0:
                db.session.commit()
                print(f"\n--- Progress: {uploaded_count} videos uploaded, {webp_success_count} WebPs created ---")
                
        except Exception as e:
            print(f"  ❌ Error processing video: {e}")
            error_count += 1
            db.session.rollback()
    
    # Final commit
    try:
        db.session.commit()
        print(f"\n{'='*60}")
        print(f"UPLOAD COMPLETE!")
        print(f"{'='*60}")
        print(f"Database records:")
        print(f"  Successfully uploaded: {uploaded_count} videos")
        print(f"  Skipped (already exist): {skipped_count} videos")
        print(f"  Errors: {error_count} videos")
        print(f"\nWebP conversions:")
        print(f"  Successfully converted: {webp_success_count} WebPs")
        print(f"  Failed conversions: {webp_error_count} WebPs")
        print(f"\nWebP files saved to: {webp_dir}")
        print(f"{'='*60}")
    except Exception as e:
        print(f"Error during final commit: {e}")
        db.session.rollback()

def main():
    """Main function to run the upload script."""
    # Define the path to the videos.json file relative to this script
    # Expected structure: video_pipeline/data/videos.json
    current_dir = Path(__file__).parent
    json_file_path = current_dir / "data" / "videos.json"
    
    # Check if the videos.json file exists
    if not json_file_path.exists():
        print(f"Error: videos.json file not found at {json_file_path}")
        print("Please ensure the videos.json file is placed in the data/ directory")
        return
    
    print("="*60)
    print("VIDEO UPLOAD & WEBP CONVERSION SCRIPT")
    print("="*60)
    print(f"Max videos to process: {MAX_VIDEOS_TO_PROCESS}")
    print(f"WebP settings: Original dimensions preserved, quality {WEBP_QUALITY}")
    print(f"Loading videos from: {json_file_path}")
    print()
    
    # Clear previous output directories
    clear_output_directories()
    print()
    
    # Load videos data
    videos_data = load_videos_json(str(json_file_path))
    if not videos_data:
        print("No videos to upload. Exiting.")
        return
    
    # Create Flask app and database context
    app = create_app()
    
    with app.app_context():
        # Check database connection
        try:
            # Test the database connection
            db.session.execute(db.text('SELECT 1'))
            print("Database connection successful")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return
        
        # Upload videos and convert to WebP
        upload_videos_to_db(videos_data)

if __name__ == "__main__":
    main()
