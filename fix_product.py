#!/usr/bin/env python
"""Fix duplicate code in product.py file"""

file_path = r'c:\Users\user\nexus_web\storefront\views\product.py'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where create_order function ends (the first return statement for the function)
# We need to find line 381 and remove everything after it that's duplicate
# The function should end at line 381

# Remove lines 383 onwards (all duplicate code)
new_lines = lines[:381]  # Keep only lines 0-380 (indices 0-380, which is lines 1-381)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Fixed! Kept {len(new_lines)} lines, removed {len(lines) - len(new_lines)} duplicate lines")
