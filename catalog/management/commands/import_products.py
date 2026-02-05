"""
Import products from MySQL dump (shop.sql)
Usage: python manage.py import_products
"""

import re
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Brand, Tire, Disk


class Command(BaseCommand):
    help = 'Import tires and disks from MySQL dump'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='shop.sql',
            help='Path to SQL dump file'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limit number of products to import (0 = all)'
        )

    def handle(self, *args, **options):
        sql_file = options['file']
        limit = options['limit']

        self.stdout.write(f'Reading {sql_file}...')

        # Read SQL file and find ALL product_flat INSERTs
        with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find ALL INSERT INTO product_flat statements
        pattern = r"INSERT INTO `product_flat` VALUES (.+?);"
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            self.stdout.write(self.style.ERROR('No product_flat data found'))
            return

        self.stdout.write(f'Found {len(matches)} INSERT statements')
        self.stdout.write('Parsing products...')

        # Parse all records from all INSERT statements
        records = []
        for values_str in matches:
            records.extend(self.parse_values(values_str))

        self.stdout.write(f'Found {len(records)} records')

        # Filter unique products (by locale='ukr' to avoid duplicates)
        unique_products = {}
        for record in records:
            if len(record) < 70:
                continue
            locale = self.clean_value(record[21]) if len(record) > 21 else ''
            product_id = self.clean_value(record[23]) if len(record) > 23 else ''

            # Only Ukrainian locale to avoid duplicates
            if locale == 'ukr' and product_id:
                unique_products[product_id] = record

        self.stdout.write(f'Unique products: {len(unique_products)}')

        # Import products
        tires_created = 0
        disks_created = 0
        skipped = 0

        products_list = list(unique_products.values())
        if limit > 0:
            products_list = products_list[:limit]

        for i, record in enumerate(products_list):
            try:
                result = self.import_product(record)
                if result == 'tire':
                    tires_created += 1
                elif result == 'disk':
                    disks_created += 1
                else:
                    skipped += 1

                if (i + 1) % 1000 == 0:
                    self.stdout.write(f'Processed {i + 1} products...')

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error: {e}'))
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! Tires: {tires_created}, Disks: {disks_created}, Skipped: {skipped}'
        ))

    def clean_value(self, val):
        """Remove quotes and clean value"""
        if val is None:
            return ''
        val = str(val).strip()
        if val.startswith("'") and val.endswith("'"):
            val = val[1:-1]
        if val == 'NULL':
            return ''
        return val

    def parse_values(self, values_str):
        """Parse SQL VALUES into list of records"""
        records = []
        current_record = []
        current_value = ''
        in_string = False
        escape_next = False
        paren_depth = 0

        i = 0
        while i < len(values_str):
            char = values_str[i]

            if escape_next:
                current_value += char
                escape_next = False
                i += 1
                continue

            if char == '\\':
                escape_next = True
                current_value += char
                i += 1
                continue

            if char == "'" and not in_string:
                in_string = True
                i += 1
                continue
            elif char == "'" and in_string:
                # Check for escaped quote
                if i + 1 < len(values_str) and values_str[i + 1] == "'":
                    current_value += "'"
                    i += 2
                    continue
                in_string = False
                i += 1
                continue

            if in_string:
                current_value += char
                i += 1
                continue

            if char == '(':
                if paren_depth == 0:
                    current_record = []
                    current_value = ''
                paren_depth += 1
                i += 1
                continue

            if char == ')':
                paren_depth -= 1
                if paren_depth == 0:
                    if current_value or current_record:
                        current_record.append(current_value.strip())
                    records.append(current_record)
                    current_record = []
                    current_value = ''
                i += 1
                continue

            if char == ',' and paren_depth == 1:
                current_record.append(current_value.strip())
                current_value = ''
                i += 1
                continue

            if paren_depth > 0:
                current_value += char

            i += 1

        return records

    def import_product(self, record):
        """Import single product record"""
        # Record structure (based on product_flat columns):
        # 0: id, 1: sku, 3: name, 10: price, 21: locale, 23: product_id
        # Tires: 38: tire_radius_label, 40: tire_width_label, 42: tire_aspect_ratio_label
        #        44: tire_season_label, 46: tire_brand_label, 48: vehicle_type_label
        #        50: tire_speed_rating_label, 52: tire_load_index_label
        #        53: studded_tire, 55: tire_model_label
        # Wheels: 57: wheel_radius_label, 59: wheel_width_label, 61: wheel_pcd_label
        #         63: wheel_dia_label, 65: wheel_et_label, 67: wheel_type_label
        #         69: wheel_brand_label, 71: wheel_model_label
        # 72: category_id, 73: stock

        name = self.clean_value(record[3]) if len(record) > 3 else ''
        sku = self.clean_value(record[1]) if len(record) > 1 else ''
        price_str = self.clean_value(record[10]) if len(record) > 10 else '0'
        category_id = self.clean_value(record[72]) if len(record) > 72 else ''

        # Parse price
        try:
            price = Decimal(price_str) if price_str else Decimal('0')
        except:
            price = Decimal('0')

        # Skip products without price
        if price <= 0:
            return 'skipped'

        # Check tire fields (use _label fields)
        tire_radius = self.clean_value(record[38]) if len(record) > 38 else ''
        tire_brand = self.clean_value(record[46]) if len(record) > 46 else ''

        # Check wheel fields (use _label fields)
        wheel_radius = self.clean_value(record[57]) if len(record) > 57 else ''
        wheel_brand = self.clean_value(record[69]) if len(record) > 69 else ''

        if tire_radius and tire_brand:
            return self.import_tire(record, name, sku, price)
        elif wheel_radius and wheel_brand:
            return self.import_disk(record, name, sku, price)

        return 'skipped'

    def import_tire(self, record, name, sku, price):
        """Import tire product"""
        # Indices: 38: tire_radius_label, 40: tire_width_label, 42: tire_aspect_ratio_label
        #          44: tire_season_label, 46: tire_brand_label, 48: vehicle_type_label
        #          50: tire_speed_rating_label, 52: tire_load_index_label
        #          53: studded_tire, 55: tire_model_label

        # Get or create brand
        brand_name = self.clean_value(record[46]) if len(record) > 46 else 'Unknown'
        if not brand_name:
            brand_name = 'Unknown'

        brand, _ = Brand.objects.get_or_create(
            name=brand_name,
            defaults={'slug': slugify(brand_name) or 'unknown'}
        )

        # Parse tire specs
        try:
            diameter = int(self.clean_value(record[38])) if len(record) > 38 else 0
        except:
            diameter = 0

        try:
            width = int(self.clean_value(record[40])) if len(record) > 40 else 0
        except:
            width = 0

        try:
            profile = int(self.clean_value(record[42])) if len(record) > 42 else 0
        except:
            profile = 0

        if not all([diameter, width, profile]):
            return 'skipped'

        # Season
        season_label = self.clean_value(record[44]) if len(record) > 44 else ''
        season_map = {
            'летняя': 'summer',
            'зимняя': 'winter',
            'всесезонная': 'allseason',
            'всесезонка': 'allseason',
        }
        season = season_map.get(season_label.lower(), 'summer') if season_label else 'summer'

        # Vehicle type
        vehicle_label = self.clean_value(record[48]) if len(record) > 48 else ''
        vehicle_map = {
            'легковой': 'passenger',
            'внедорожник': 'suv',
            'suv': 'suv',
            'грузовой': 'truck',
            'микроавтобус': 'van',
        }
        vehicle_type = vehicle_map.get(vehicle_label.lower(), 'passenger') if vehicle_label else 'passenger'

        # Speed and load index
        speed_index = self.clean_value(record[50]) if len(record) > 50 else 'H'
        if not speed_index:
            speed_index = 'H'
        try:
            load_index = int(self.clean_value(record[52])) if len(record) > 52 else 91
        except:
            load_index = 91

        # Studded
        studded_val = self.clean_value(record[53]) if len(record) > 53 else '0'
        studded = studded_val == '1'

        # Model name
        model_name = self.clean_value(record[55]) if len(record) > 55 else name
        if not model_name:
            model_name = name

        # Generate unique slug
        base_slug = slugify(f"{brand_name}-{model_name}-{width}-{profile}-{diameter}")
        slug = base_slug or f"tire-{sku}"

        # Check if exists
        if Tire.objects.filter(article=sku).exists():
            return 'skipped'

        # Make slug unique
        counter = 1
        original_slug = slug
        while Tire.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        # Create tire
        Tire.objects.create(
            brand=brand,
            model_name=model_name[:200],
            slug=slug[:250],
            width=width,
            profile=profile,
            diameter=diameter,
            load_index=load_index,
            speed_index=speed_index[:2] if speed_index else 'H',
            season=season,
            vehicle_type=vehicle_type,
            studded=studded,
            price=price,
            in_stock=True,
            stock_quantity=4,
            article=sku[:50],
        )

        return 'tire'

    def import_disk(self, record, name, sku, price):
        """Import disk/wheel product"""
        # Indices: 57: wheel_radius_label, 59: wheel_width_label, 61: wheel_pcd_label
        #          63: wheel_dia_label, 65: wheel_et_label, 67: wheel_type_label
        #          69: wheel_brand_label, 71: wheel_model_label

        # Get or create brand
        brand_name = self.clean_value(record[69]) if len(record) > 69 else 'Unknown'
        if not brand_name:
            brand_name = 'Unknown'

        brand, _ = Brand.objects.get_or_create(
            name=brand_name,
            defaults={'slug': slugify(brand_name) or 'unknown'}
        )

        # Parse wheel specs
        try:
            diameter = int(self.clean_value(record[57])) if len(record) > 57 else 0
        except:
            diameter = 0

        try:
            width = Decimal(self.clean_value(record[59]) or '6.5') if len(record) > 59 else Decimal('6.5')
        except:
            width = Decimal('6.5')

        if not diameter:
            return 'skipped'

        # PCD (e.g., "5x114.3")
        pcd_label = self.clean_value(record[61]) if len(record) > 61 else '5x114.3'
        pcd_match = re.match(r'(\d+)[xX](\d+\.?\d*)', pcd_label) if pcd_label else None
        if pcd_match:
            bolts = int(pcd_match.group(1))
            pcd = Decimal(pcd_match.group(2))
        else:
            bolts = 5
            pcd = Decimal('114.3')

        # DIA
        try:
            dia = Decimal(self.clean_value(record[63]) or '67.1') if len(record) > 63 else Decimal('67.1')
        except:
            dia = Decimal('67.1')

        # ET
        try:
            et = int(self.clean_value(record[65]) or '45') if len(record) > 65 else 45
        except:
            et = 45

        # Type
        type_label = self.clean_value(record[67]) if len(record) > 67 else ''
        type_map = {
            'литой': 'alloy',
            'литые': 'alloy',
            'стальной': 'steel',
            'стальные': 'steel',
            'кованый': 'forged',
            'кованые': 'forged',
        }
        disk_type = type_map.get(type_label.lower(), 'alloy') if type_label else 'alloy'

        # Model
        model_name = self.clean_value(record[71]) if len(record) > 71 else name
        if not model_name:
            model_name = name

        # Generate slug
        base_slug = slugify(f"{brand_name}-{model_name}-{diameter}")
        slug = base_slug or f"disk-{sku}"

        # Check if exists
        if Disk.objects.filter(article=sku).exists():
            return 'skipped'

        # Make slug unique
        counter = 1
        original_slug = slug
        while Disk.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        # Create disk
        Disk.objects.create(
            brand=brand,
            model_name=model_name[:200],
            slug=slug[:250],
            diameter=diameter,
            width=width,
            bolts=bolts,
            pcd=pcd,
            dia=dia,
            et=et,
            disk_type=disk_type,
            price=price,
            in_stock=True,
            stock_quantity=4,
            article=sku[:50],
        )

        return 'disk'
