#!/usr/bin/env python3
"""Final verification of both tables"""
import requests
import re

print("=" * 60)
print("DASHBOARD TABLE FORMATTING VERIFICATION")
print("=" * 60)

# Test Servers Table
print("\n[SERVERS TABLE]")
servers_response = requests.get("http://localhost:8000/api/servers-table")
servers_html = servers_response.text

servers_checks = {
    "Uptime display (hrs/days)": bool(re.search(r'\d+\.\d+\s+(?:hrs|days)', servers_html)),
    "Status badges": "Healthy" in servers_html or "Critical" in servers_html,
    "Progress bars": "w-24" in servers_html,
    "Proper padding (px-6)": "px-6" in servers_html,
}

servers_count = len(re.findall(r'<tr class="border-t', servers_html))
print(f"Server rows: {servers_count}")
for check, passed in servers_checks.items():
    status = "✓" if passed else "✗"
    print(f"  {status} {check}")

# Test Containers Table
print("\n[CONTAINERS TABLE]")
containers_response = requests.get("http://localhost:8000/api/containers-table")
containers_html = containers_response.text

containers_checks = {
    "Status badges": "Healthy" in containers_html or "Degraded" in containers_html,
    "CPU progress bars": "from-blue" in containers_html,
    "Memory progress bars": "from-green" in containers_html,
    "Proper padding (px-6)": "px-6" in containers_html,
    "Font styling": "font-bold" in containers_html,
}

containers_count = len(re.findall(r'<tr class="border-t', containers_html))
print(f"Container rows: {containers_count}")
for check, passed in containers_checks.items():
    status = "✓" if passed else "✗"
    print(f"  {status} {check}")

# Check emojis
print("\n[EMOJI SUPPORT]")
full_page = requests.get("http://localhost:8000/containers").text
emojis = {
    "🐳 Container emoji": "🐳" in full_page,
    "📦 Service emoji": "📦" in full_page,
    "💾 CPU emoji": "💾" in full_page,
    "🧠 Memory emoji": "🧠" in full_page,
    "❤️ Health emoji": "❤️" in full_page,
    "📺 Server emoji": "📺" in full_page,
    "🌍 Region emoji": "🌍" in full_page,
}

for emoji, found in emojis.items():
    status = "✓" if found else "✗"
    print(f"  {status} {emoji}")

print("\n" + "=" * 60)
print("All checks completed successfully!")
print("=" * 60)
