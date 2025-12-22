#!/usr/bin/env python3
"""Check profile page HTML structure"""
import requests
import re

response = requests.get("http://localhost:8000/profile")
html = response.text

# Check for the actual rendered image
if 'google.com/uc?export=view' in html:
    print("✓ Google Drive image URL is in the HTML")
    
    # Extract just the image section
    img_section = re.search(r'<img[^>]*src="[^"]*"[^>]*class="profile-image"[^>]*>', html)
    if img_section:
        print(f"\nImage tag HTML:")
        print(img_section.group(0))
    
    # Check if there's any JavaScript that might be interfering
    if 'image' in html.lower():
        print("\n✓ Page contains 'image' references")
    
    # Check the overall structure
    if '<div class="profile-header">' in html:
        print("✓ Profile header div found")
        
        # Extract the header section
        header_match = re.search(r'<div class="profile-header">(.*?)</div>\s*<!-- Professional Summary -->', html, re.DOTALL)
        if header_match:
            header_html = header_match.group(1)
            if 'img' in header_html:
                print("✓ Image tag is inside profile-header")
            if 'Ahmad' in header_html:
                print("✓ Name is in the header")
else:
    print("✗ Image URL not found in HTML")
    
    # Show first 2000 chars of HTML to debug
    print("\nFirst part of HTML:")
    print(html[:2000])
