#!/usr/bin/env python3
"""Check actual container table HTML"""
import requests
import re

response = requests.get("http://localhost:8000/api/containers-table")
html = response.text

# Find first row
first_row = re.search(r'<tr[^>]*>.*?</tr>', html, re.DOTALL)
if first_row:
    row = first_row.group(0)
    print("First container row (formatted):")
    print(row[:500])
    print("...")
    
    # Check for padding classes
    if 'px-6' in row:
        print("\n✓ Found px-6 padding")
    elif 'px-' in row:
        print(f"\n! Found different padding: {re.findall(r'px-\d+', row)}")
    else:
        print("\n! No horizontal padding found")
        
    # Show total length
    print(f"\nTotal row length: {len(row)} chars")
