"""
HTML page creation utilities for shareable poster pages.
No longer uses Cloudinary - creates HTML pages for local storage.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def create_shareable_html_page(image_url: str, caption: str, full_caption: str) -> str:
    """
    Create a simple HTML page with Open Graph meta tags for Facebook sharing.
    Returns the HTML content as a string.
    """
    # Escape HTML special characters for meta tags
    def escape_html(text: str) -> str:
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    safe_caption = escape_html(caption[:60] if caption else "AI Generated Poster")
    # Use longer description - Facebook allows up to 300 characters
    safe_full_caption = escape_html(full_caption[:300] if full_caption else caption[:300] if caption else "Check out this amazing AI-generated poster!")
    safe_image_url = image_url.replace('&', '&amp;')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_caption}</title>
    
    <!-- Open Graph Meta Tags for Facebook -->
    <meta property="og:title" content="{safe_caption}" />
    <meta property="og:description" content="{safe_full_caption}" />
    <meta property="og:image" content="{safe_image_url}" />
    <meta property="og:image:secure_url" content="{safe_image_url}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="1200" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{safe_image_url}" />
    
    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{safe_caption}" />
    <meta name="twitter:description" content="{safe_full_caption}" />
    <meta name="twitter:image" content="{safe_image_url}" />
    
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            max-width: 800px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        h1 {{
            color: #333;
            margin-top: 20px;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <img src="{safe_image_url}" alt="{safe_caption}" />
        <h1>{safe_caption}</h1>
        <p>{safe_full_caption}</p>
    </div>
</body>
</html>"""
    return html_content
