"""Service for importing tires and disks from Excel files"""
import pandas as pd
from decimal import Decimal, InvalidOperation
from pathlib import Path
from django.utils.text import slugify
from django.conf import settings
from .models import Tire, Disk, Brand, Supplier


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


def check_image_exists(image_path):
    """Check if image file exists"""
    if not image_path or image_path == 'nan' or pd.isna(image_path):
        return ''
    media_root = Path(settings.MEDIA_ROOT)
    if (media_root / str(image_path)).exists():
        return str(image_path)
    return ''


def get_or_create_supplier(supplier_code):
    """Get or create supplier from code like 'kiev_Склад Колёс' or 'kh_DTW Харьков (21 день)'"""
    if not supplier_code or pd.isna(supplier_code) or str(supplier_code).strip() == '':
        return None

    supplier_code = str(supplier_code).strip()

    # Try to find existing supplier
    supplier = Supplier.objects.filter(code=supplier_code).first()
    if supplier:
        return supplier if supplier.is_active else None

    # Create new supplier
    # Detect if it's preorder (contains "день" or "дней" etc.)
    is_preorder = any(word in supplier_code.lower() for word in ['день', 'дней', 'дні', 'днів'])

    # Extract name from code
    name = supplier_code
    if '_' in supplier_code:
        name = supplier_code.split('_', 1)[1]

    supplier = Supplier.objects.create(
        name=name,
        code=supplier_code,
        is_preorder=is_preorder,
        markup_percent=0,  # Default, admin can change
        delivery_days="10-14 днів" if is_preorder else "1-3 дні",
        is_active=True
    )

    return supplier


def import_tires(file_path):
    """Import tires from Excel file"""
    df = pd.read_excel(file_path, header=None)

    created = 0
    updated = 0
    skipped = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            brand_name = str(row[0]).strip() if pd.notna(row[0]) else None
            model_name = str(row[1]).strip() if pd.notna(row[1]) else None

            if not brand_name or not model_name:
                skipped += 1
                continue

            # Parse values - adjusted for actual Excel structure
            width = parse_int(row[2])
            profile = parse_int(row[3])
            diameter = parse_int(row[4])

            # Load index can be like "104/102" - take first number
            load_index_raw = str(row[5]) if pd.notna(row[5]) else "0"
            load_index = parse_int(load_index_raw.split('/')[0])

            speed_index = str(row[6]).strip() if pd.notna(row[6]) else None
            season_raw = str(row[12]).strip().lower() if pd.notna(row[12]) else 'summer'

            # Map season
            if 'зим' in season_raw:
                season = 'winter'
            elif 'всесезон' in season_raw or 'все сезон' in season_raw:
                season = 'all_season'
            else:
                season = 'summer'

            stock_qty = parse_int(row[13]) or 0
            purchase_price = parse_decimal(row[14])  # Purchase price
            selling_price = parse_decimal(row[15])   # Selling price

            # Get supplier (column 18 for tires)
            supplier_code = str(row[18]).strip() if pd.notna(row[18]) and len(row) > 18 else None
            supplier = get_or_create_supplier(supplier_code)

            # Skip if supplier is inactive
            if supplier_code and not supplier:
                skipped += 1
                continue

            article = str(row[20]) if pd.notna(row[20]) and len(row) > 20 else None
            image = str(row[21]).strip() if pd.notna(row[21]) and len(row) > 21 else None

            # Determine price - use selling price or apply markup to purchase price
            price = selling_price
            if (not price or price <= 0) and purchase_price and purchase_price > 0:
                if supplier:
                    price = supplier.apply_markup(purchase_price)
                else:
                    price = purchase_price

            if not price or price <= 0:
                skipped += 1
                continue

            # Required fields
            if not all([width, profile, diameter]):
                skipped += 1
                continue

            # Determine in_stock based on supplier
            in_stock = True
            if supplier and supplier.is_preorder:
                in_stock = False

            # Get or create brand
            brand, _ = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': slugify(brand_name, allow_unicode=True) or brand_name.lower().replace(' ', '-')}
            )

            # Find existing tire
            tire = None
            if article:
                tire = Tire.objects.filter(article=article).first()

            if not tire:
                tire = Tire.objects.filter(
                    brand=brand,
                    model_name=model_name,
                    width=width,
                    profile=profile,
                    diameter=diameter
                ).first()

            if tire:
                # Update existing
                tire.price = price
                tire.stock_quantity = stock_qty
                tire.in_stock = in_stock
                tire.supplier = supplier
                image_path = check_image_exists(image)
                if image_path:
                    tire.image = image_path
                tire.save()
                updated += 1
            else:
                # Create new
                base_slug = slugify(f"{brand_name}-{model_name}-{width}-{profile}-{diameter}", allow_unicode=True)
                slug = base_slug or f"tire-{idx}"
                counter = 1
                while Tire.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"[:200]
                    counter += 1

                tire = Tire.objects.create(
                    brand=brand,
                    model_name=model_name,
                    slug=slug,
                    article=article or f"T{idx}",
                    width=width,
                    profile=profile,
                    diameter=diameter,
                    load_index=load_index or 0,
                    speed_index=speed_index or '',
                    season=season,
                    price=price,
                    stock_quantity=stock_qty,
                    in_stock=in_stock,
                    supplier=supplier,
                    image=check_image_exists(image)
                )
                created += 1

        except Exception as e:
            errors.append(f"Row {idx}: {str(e)}")

    return {
        'created': created,
        'updated': updated,
        'skipped': skipped,
        'errors': errors[:20],
        'total_rows': len(df)
    }


def import_disks(file_path):
    """Import disks from Excel file"""
    df = pd.read_excel(file_path, header=None)

    created = 0
    updated = 0
    skipped = 0
    errors = []

    def map_disk_type(type_str):
        if pd.isna(type_str):
            return 'alloy'
        type_str = str(type_str).lower().strip()
        if 'штамп' in type_str:
            return 'steel'
        elif 'кован' in type_str:
            return 'forged'
        return 'alloy'

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
            purchase_price = parse_decimal(row[14])  # Purchase price
            selling_price = parse_decimal(row[15])   # Selling price

            # Get supplier (column 18 for disks)
            supplier_code = str(row[18]).strip() if pd.notna(row[18]) and len(row) > 18 else None
            supplier = get_or_create_supplier(supplier_code)

            # Skip if supplier is inactive
            if supplier_code and not supplier:
                skipped += 1
                continue

            article = str(row[20]) if pd.notna(row[20]) and len(row) > 20 else None
            image = str(row[21]).strip() if pd.notna(row[21]) and len(row) > 21 else None

            # Determine price
            price = selling_price
            if (not price or price <= 0) and purchase_price and purchase_price > 0:
                if supplier:
                    price = supplier.apply_markup(purchase_price)
                else:
                    price = purchase_price

            if not price or price <= 0:
                skipped += 1
                continue

            # Required fields
            if not all([width, diameter, pcd, bolts]):
                skipped += 1
                continue

            # Determine in_stock based on supplier
            in_stock = True
            if supplier and supplier.is_preorder:
                in_stock = False

            # Get or create brand
            brand, _ = Brand.objects.get_or_create(
                name=brand_name,
                defaults={'slug': slugify(brand_name, allow_unicode=True) or brand_name.lower().replace(' ', '-')}
            )

            # Find existing disk
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
                disk.in_stock = in_stock
                disk.supplier = supplier
                image_path = check_image_exists(image)
                if image_path:
                    disk.image = image_path
                if color:
                    disk.color = color
                disk.save()
                updated += 1
            else:
                # Create new
                base_slug = slugify(f"{brand_name}-{model_name}-{width}x{diameter}-{bolts}x{pcd}-et{et or 0}", allow_unicode=True)
                slug = base_slug or f"disk-{idx}"
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
                    in_stock=in_stock,
                    supplier=supplier,
                    image=check_image_exists(image)
                )
                created += 1

        except Exception as e:
            errors.append(f"Row {idx}: {str(e)}")

    return {
        'created': created,
        'updated': updated,
        'skipped': skipped,
        'errors': errors[:20],
        'total_rows': len(df)
    }
