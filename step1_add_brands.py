#!/usr/bin/env python3
"""Step 1: Add 5 new brands to master.csv"""
import csv
import os

ROOT = "/workspace/pinpai-ai-in"
CSV_PATH = os.path.join(ROOT, "master.csv")

# 5 new brands
new_brands = [
    {"slug": "disney", "name_en": "Disney", "name_zh": "迪士尼", "category": "entertainment", "country": "United States", "deployed": "true"},
    {"slug": "toyota", "name_en": "Toyota", "name_zh": "丰田", "category": "automotive", "country": "Japan", "deployed": "true"},
    {"slug": "samsung", "name_en": "Samsung", "name_zh": "三星", "category": "technology", "country": "South Korea", "deployed": "true"},
    {"slug": "starbucks", "name_en": "Starbucks", "name_zh": "星巴克", "category": "food", "country": "United States", "deployed": "true"},
    {"slug": "mercedes-benz", "name_en": "Mercedes-Benz", "name_zh": "梅赛德斯-奔驰", "category": "automotive", "country": "Germany", "deployed": "true"},
]

# Read existing
with open(CSV_PATH, 'r', newline='') as f:
    reader = csv.reader(f)
    existing = list(reader)

print(f"Existing master.csv: {len(existing)-1} brands")

# Append new
with open(CSV_PATH, 'a', newline='') as f:
    writer = csv.writer(f)
    for b in new_brands:
        writer.writerow([b["slug"], b["name_en"], b["name_zh"], b["category"], b["country"], b["deployed"]])
        print(f"➕ Added: {b['name_zh']} ({b['name_en']}) → {b['slug']}")

# Verify
with open(CSV_PATH, 'r', newline='') as f:
    reader = csv.reader(f)
    rows = list(reader)
print(f"\nTotal brands in master.csv: {len(rows)-1}")
