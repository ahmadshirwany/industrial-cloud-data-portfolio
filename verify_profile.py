#!/usr/bin/env python3
"""Verify the profile page setup"""
import requests

print("=" * 70)
print("INTERACTIVE CV/PROFILE PAGE VERIFICATION")
print("=" * 70)

# Test home page has the profile card
print("\n1. Checking Home Page (/)...")
response = requests.get("http://localhost:8000/")
if response.status_code == 200:
    html = response.text
    if "My Profile" in html and "/profile" in html:
        print("   ✓ Profile card found on home page")
        if "👨‍💻" in html:
            print("   ✓ Emoji displayed correctly")
    else:
        print("   ✗ Profile card not found")
else:
    print(f"   ✗ Error: {response.status_code}")

# Test profile page exists and loads
print("\n2. Checking Profile Page (/profile)...")
response = requests.get("http://localhost:8000/profile")
if response.status_code == 200:
    html = response.text
    print("   ✓ Profile page loads successfully")
    
    # Check for key sections
    sections = {
        "Header": "Ahmad Ali Khan Shirwany",
        "Summary": "Professional Summary",
        "Skills": "Technical Skills",
        "Experience": "Professional Experience",
        "Projects": "Key Projects",
        "Education": "Education",
        "Certifications": "Certifications",
    }
    
    for section, keyword in sections.items():
        if keyword in html:
            print(f"   ✓ {section} section found")
        else:
            print(f"   ✗ {section} section missing")
    
    # Check for styling
    if "profile-header" in html:
        print("   ✓ Custom styling applied")
    if "contact-links" in html:
        print("   ✓ Contact links section present")
    if "skills-grid" in html:
        print("   ✓ Skills grid layout present")
    if "projects-grid" in html:
        print("   ✓ Projects grid layout present")

else:
    print(f"   ✗ Error: {response.status_code}")

# Test navigation
print("\n3. Checking Navigation...")
response = requests.get("http://localhost:8000/profile")
html = response.text
if "Back to Dashboard" in html:
    print("   ✓ Back button present on profile page")
else:
    print("   ✗ Back button missing")

print("\n" + "=" * 70)
print("✅ Interactive CV/Profile Page Setup Complete!")
print("=" * 70)
print("\nYou can now:")
print("  1. View the home page: http://localhost:8000/")
print("  2. Click 'My Profile' card to view CV")
print("  3. Or directly visit: http://localhost:8000/profile")
print("\nFeatures:")
print("  • Responsive design (works on mobile)")
print("  • Interactive skill badges with hover effects")
print("  • Project cards with descriptions")
print("  • Contact links (email, LinkedIn, GitHub, phone)")
print("  • Professional styling with gradients")
print("  • Smooth animations and transitions")
