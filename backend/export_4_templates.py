import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.models import PosterTemplate
import json

# Get the 4 templates
templates = PosterTemplate.objects.filter(name__in=[
    "Men's Casual T-shirt",
    "Elegant Silk Saree",
    "Men's Denim Shirt",
    "Wedding Frock"
])

print(f"Found {templates.count()} templates")

data = []
for t in templates:
    data.append({
        "name": t.name,
        "description": t.description or "",
        "prompt": t.prompt,
        "category": t.category,
        "subcategory": t.subcategory or "",
        "audience": list(t.audience) if t.audience else [],
        "offer": t.offer or "",
        "thumbnail_filename": t.thumbnail.name if t.thumbnail else None,
    })
    print(f"  - {t.name}")

# Save to file
with open('missing_4_templates.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nExported {len(data)} templates to missing_4_templates.json")