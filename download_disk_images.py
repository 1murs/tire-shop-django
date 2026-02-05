#!/usr/bin/env python
"""Download disk images from remote server"""
import os
import sys
import django
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Disk

BASE_URL = "https://km120.com.ua/media/"
MEDIA_ROOT = Path("/Users/1murs/Desktop/tire-shop-django/media")

def download_image(image_path):
    """Download single image"""
    if not image_path or image_path == 'nan':
        return None, "empty"

    local_path = MEDIA_ROOT / image_path

    # Skip if already exists
    if local_path.exists():
        return image_path, "exists"

    # Create directory
    local_path.parent.mkdir(parents=True, exist_ok=True)

    url = BASE_URL + image_path
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return image_path, "downloaded"
        else:
            return image_path, f"error:{response.status_code}"
    except Exception as e:
        return image_path, f"error:{str(e)[:30]}"

def main():
    # Get unique image paths
    images = list(Disk.objects.exclude(image='').exclude(image__isnull=True)
                  .values_list('image', flat=True).distinct())

    print(f"Found {len(images)} unique disk images to download")

    downloaded = 0
    exists = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(download_image, img): img for img in images}

        for i, future in enumerate(as_completed(futures)):
            path, status = future.result()

            if status == "downloaded":
                downloaded += 1
            elif status == "exists":
                exists += 1
            else:
                errors += 1

            if (i + 1) % 500 == 0:
                print(f"Progress: {i+1}/{len(images)} - Downloaded: {downloaded}, Exists: {exists}, Errors: {errors}")

    print(f"\nDone!")
    print(f"Downloaded: {downloaded}")
    print(f"Already exists: {exists}")
    print(f"Errors: {errors}")

if __name__ == '__main__':
    main()
