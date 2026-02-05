"""
Update tire images from Excel price list
Usage: python manage.py update_images
"""

import pandas as pd
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Tire


class Command(BaseCommand):
    help = 'Update tire images from Excel price list'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='price_shini_28-01-26.xls',
            help='Path to Excel file'
        )

    def handle(self, *args, **options):
        excel_file = options['file']

        self.stdout.write(f'Reading {excel_file}...')

        # Read Excel
        df = pd.read_excel(excel_file)
        self.stdout.write(f'Found {len(df)} rows')

        # Column indices:
        # 0: brand, 1: model, 2: width, 3: profile, 4: diameter
        # 21: image path

        # Build image mapping by brand+model+size key
        image_map = {}
        for _, row in df.iterrows():
            try:
                brand = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                model = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''

                # Handle numeric values with comma decimal separator
                width_val = str(row.iloc[2]).replace(',', '.') if pd.notna(row.iloc[2]) else ''
                profile_val = str(row.iloc[3]).replace(',', '.') if pd.notna(row.iloc[3]) else ''
                diameter_val = str(row.iloc[4]).replace(',', '.') if pd.notna(row.iloc[4]) else ''

                width = str(int(float(width_val))) if width_val else ''
                profile = str(int(float(profile_val))) if profile_val else ''
                diameter = str(int(float(diameter_val))) if diameter_val else ''

                image = str(row.iloc[21]).strip() if pd.notna(row.iloc[21]) else ''

                if brand and model and width and profile and diameter and image:
                    # Create lookup key
                    key = f"{brand.lower()}|{model.lower()}|{width}|{profile}|{diameter}"
                    image_map[key] = image
            except Exception:
                continue

        self.stdout.write(f'Built image map with {len(image_map)} entries')

        # Update tires
        updated = 0
        not_found = 0

        tires = Tire.objects.select_related('brand').all()
        total = tires.count()

        for i, tire in enumerate(tires):
            key = f"{tire.brand.name.lower()}|{tire.model_name.lower()}|{tire.width}|{tire.profile}|{tire.diameter}"

            if key in image_map:
                image_path = image_map[key]
                tire.image = image_path
                tire.save(update_fields=['image'])
                updated += 1
            else:
                not_found += 1

            if (i + 1) % 5000 == 0:
                self.stdout.write(f'Processed {i + 1}/{total} tires... (updated: {updated})')

        self.stdout.write(self.style.SUCCESS(
            f'Done! Updated: {updated}, Not found: {not_found}'
        ))
