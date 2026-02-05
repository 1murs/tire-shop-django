#!/usr/bin/env python
"""Import disks from Excel price list"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pandas as pd
from decimal import Decimal, InvalidOperation
from django.utils.text import slugify
from catalog.models import Disk, Brand

def generate_unique_slug(brand_name, model_name, width, diameter, pcd, et, bolts):
    """Generate unique slug for disk"""
    base = f"{brand_name}-{model_name}-{width}x{diameter}-{bolts}x{pcd}-et{et}"
    slug = slugify(base, allow_unicode=True)
    if not slug:
        slug = f"disk-{brand_name}-{model_name}"
    return slug[:200]

def parse_decimal(value):
    """Parse decimal from string with comma"""
    if pd.isna(value):
        return None
    try:
        str_val = str(value).replace(',', '.').replace(' ', '').strip()
        if not str_val or str_val == '0,00' or str_val == '0.00':
            return None
        return Decimal(str_val)
    except (InvalidOperation, ValueError):
        return None

def parse_float(value):
    """Parse float from string with comma"""
    if pd.isna(value):
        return None
    try:
        str_val = str(value).replace(',', '.').strip()
        return float(str_val)
    except ValueError:
        return None

def parse_int(value):
    """Parse integer"""
    if pd.isna(value):
        return None
    try:
        return int(float(str(value).replace(',', '.')))
    except (ValueError, TypeError):
        return None

def map_disk_type(type_str):
    """Map disk type from Russian to English"""
    if pd.isna(type_str):
        return 'alloy'
    type_str = str(type_str).lower().strip()
    if 'штамп' in type_str:
        return 'steel'
    elif 'кован' in type_str:
        return 'forged'
    else:
        return 'alloy'

def import_disks(filepath):
    print(f"Reading {filepath}...")
    df = pd.read_excel(filepath, header=None)
    print(f"Found {len(df)} rows")

    created = 0
    updated = 0
    skipped = 0
    errors = 0

    for idx, row in df.iterrows():
        try:
            brand_name = str(row[0]).strip() if pd.notna(row[0]) else None
            model_name = str(row[1]).strip() if pd.notna(row[1]) else None

            if not brand_name or not model_name:
                skipped += 1
                continue

            # Parse values
            width = parse_float(row[3])
            diameter = parse_int(row[4])
            pcd = parse_float(row[5])
            et = parse_int(row[7])
            dia = parse_float(row[8])
            color = str(row[9]).strip() if pd.notna(row[9]) else None
            disk_type = map_disk_type(row[10])
            bolts = parse_int(row[11])
            stock_qty = parse_int(row[13]) or 0
            price = parse_decimal(row[15])  # Selling price
            article = str(row[20]) if pd.notna(row[20]) else None
            image = str(row[21]).strip() if pd.notna(row[21]) else None

            # Skip if no price or zero price
            if not price or price <= 0:
                # Try purchase price
                price = parse_decimal(row[14])
                if not price or price <= 0:
                    skipped += 1
                    continue

            # Required fields
            if not all([width, diameter, pcd, bolts]):
                skipped += 1
                continue

            # Get or create brand
            brand, _ = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': brand_name.lower().replace(' ', '-').replace('.', '')}
            )

            # Try to find existing disk by article or by specs
            disk = None
            if article:
                disk = Disk.objects.filter(article=article).first()

            if not disk:
                disk = Disk.objects.filter(
                    brand=brand,
                    model_name=model_name,
                    width=width,
                    diameter=diameter,
                    pcd=pcd,
                    et=et or 0
                ).first()

            if disk:
                # Update existing
                disk.price = price
                disk.stock_quantity = stock_qty
                if image and image != 'nan':
                    disk.image = image
                if color:
                    disk.color = color
                disk.save()
                updated += 1
            else:
                # Create new with unique slug
                base_slug = generate_unique_slug(brand_name, model_name, width, diameter, pcd, et or 0, bolts)
                slug = base_slug
                counter = 1
                while Disk.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"[:200]
                    counter += 1

                disk = Disk.objects.create(
                    brand=brand,
                    model_name=model_name,
                    slug=slug,
                    article=article or f"D{idx}",
                    width=width,
                    diameter=diameter,
                    bolts=bolts,
                    pcd=pcd,
                    et=et or 0,
                    dia=dia or 0,
                    color=color or '',
                    disk_type=disk_type,
                    price=price,
                    stock_quantity=stock_qty,
                    image=image if image and image != 'nan' else ''
                )
                created += 1

            if (created + updated) % 1000 == 0:
                print(f"Progress: {created} created, {updated} updated...")

        except Exception as e:
            errors += 1
            if errors <= 10:
                print(f"Error row {idx}: {e}")

    print(f"\nDone!")
    print(f"Created: {created}")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'price_diski_04-02-26.xls'
    import_disks(filepath)
