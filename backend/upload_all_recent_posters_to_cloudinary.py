#!/usr/bin/env python
"""Upload all recent posters to Cloudinary and create HTML pages for Facebook sharing"""
import os
import sys
import django
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.models import GeneratedPoster
from ai_services.utils.cloudinary_utils import upload_to_cloudinary, create_shareable_html_page, upload_html_to_cloudinary
from django.core.files.storage import default_storage
from django.utils import timezone
from datetime import timedelta

print("=" * 60)
print("Uploading All Recent Posters to Cloudinary")
print("=" * 60)

# Get all posters from the last 7 days that don't have public_url
recent_date = timezone.now() - timedelta(days=7)
posters = GeneratedPoster.objects.filter(
    created_at__gte=recent_date
).order_by('-created_at')

print(f"\n📋 Found {posters.count()} posters from the last 7 days")

# Filter posters that need Cloudinary upload
posters_to_upload = []
for poster in posters:
    if not poster.public_url or not poster.public_url.startswith('http'):
        posters_to_upload.append(poster)

print(f"📤 {len(posters_to_upload)} posters need Cloudinary upload")
print(f"✅ {posters.count() - len(posters_to_upload)} posters already have public_url")

if not posters_to_upload:
    print("\n✅ All recent posters already have public_url set!")
    sys.exit(0)

print(f"\n🔨 Starting upload process...")
print("=" * 60)

success_count = 0
failed_count = 0

for idx, poster in enumerate(posters_to_upload, 1):
    print(f"\n[{idx}/{len(posters_to_upload)}] Processing poster {poster.id}")
    print(f"   Created: {poster.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Image Path: {poster.image_path}")
    
    try:
        # Check if image file exists
        if not poster.image_path:
            print(f"   ⚠️  No image_path, skipping...")
            failed_count += 1
            continue
        
        if not default_storage.exists(poster.image_path):
            print(f"   ⚠️  Image file not found: {poster.image_path}")
            failed_count += 1
            continue
        
        # Step 1: Upload image to Cloudinary
        print(f"   📤 Step 1: Uploading image to Cloudinary...")
        image_url = upload_to_cloudinary(poster.image_path)
        
        if not image_url:
            print(f"   ❌ Failed to upload image to Cloudinary")
            failed_count += 1
            continue
        
        print(f"   ✅ Image uploaded: {image_url[:60]}...")
        
        # Step 2: Create HTML page with caption
        print(f"   📄 Step 2: Creating HTML page...")
        caption = poster.caption or ""
        full_caption = poster.full_caption or caption
        
        if not caption and not full_caption:
            print(f"   ⚠️  No caption available, using default")
            caption = "AI Generated Poster"
            full_caption = "Check out this amazing AI-generated poster!"
        
        html_content = create_shareable_html_page(
            image_url,
            caption,
            full_caption
        )
        
        # Step 3: Upload HTML page to Cloudinary
        print(f"   📤 Step 3: Uploading HTML page to Cloudinary...")
        html_filename = f"poster_{poster.id.hex[:8]}_{int(time.time())}"
        html_url = upload_html_to_cloudinary(html_content, filename=html_filename)
        
        if not html_url:
            print(f"   ⚠️  Failed to upload HTML page, using image URL")
            html_url = image_url
        
        # Step 4: Update poster in database
        print(f"   💾 Step 4: Updating database...")
        poster.public_url = html_url
        poster.save()
        
        print(f"   ✅ SUCCESS! Poster updated with public_url: {html_url[:60]}...")
        success_count += 1
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        failed_count += 1

print("\n" + "=" * 60)
print("📊 Summary:")
print("=" * 60)
print(f"   ✅ Successfully uploaded: {success_count}")
print(f"   ❌ Failed: {failed_count}")
print(f"   📋 Total processed: {len(posters_to_upload)}")
print("\n" + "=" * 60)

if success_count > 0:
    print(f"\n✅ {success_count} posters are now ready for Facebook sharing!")
    print(f"   You can now share them from the social media page.")
else:
    print(f"\n⚠️  No posters were successfully uploaded.")
    print(f"   Check the errors above for details.")

print("\n" + "=" * 60)


