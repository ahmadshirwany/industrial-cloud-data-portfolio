#!/usr/bin/env python3
"""Check header emojis in containers table"""
import requests

response = requests.get("http://localhost:8000/containers")
html = response.text

# Look for the header emojis
headers = {
    "🐳 Container ID": "🐳" in html,
    "📦 Service": "📦" in html,
    "💾 CPU": "💾" in html,
    "🧠 Memory": "🧠" in html,
    "❤️ Health": "❤️" in html,
}

print("Container table header emojis:")
for header, found in headers.items():
    status = "✓" if found else "✗"
    print(f"  {status} {header}")
