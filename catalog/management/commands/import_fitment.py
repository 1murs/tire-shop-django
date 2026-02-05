"""
Import car fitment data from MySQL dump (catalog.sql)
Usage: python manage.py import_fitment
"""

import re
from django.core.management.base import BaseCommand
from catalog.models import CarFitment


class Command(BaseCommand):
    help = 'Import car fitment data from MySQL dump'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='catalog.sql',
            help='Path to SQL dump file'
        )

    def handle(self, *args, **options):
        sql_file = options['file']

        self.stdout.write(f'Reading {sql_file}...')

        with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find INSERT INTO podbor_shini_i_diski
        pattern = r"INSERT INTO `podbor_shini_i_diski` VALUES (.+?);"
        matches = re.findall(pattern, content, re.DOTALL)

        if not matches:
            self.stdout.write(self.style.ERROR('No fitment data found'))
            return

        self.stdout.write(f'Found {len(matches)} INSERT statements')
        self.stdout.write('Parsing fitment data...')

        # Parse all records
        records = []
        for values_str in matches:
            records.extend(self.parse_values(values_str))

        self.stdout.write(f'Found {len(records)} records')

        # Clear existing data
        CarFitment.objects.all().delete()
        self.stdout.write('Cleared existing fitment data')

        # Import records
        created = 0
        batch = []
        batch_size = 1000

        for i, record in enumerate(records):
            try:
                fitment = self.create_fitment(record)
                if fitment:
                    batch.append(fitment)
                    created += 1

                if len(batch) >= batch_size:
                    CarFitment.objects.bulk_create(batch)
                    batch = []
                    self.stdout.write(f'Processed {i + 1} records...')

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error: {e}'))

        # Save remaining
        if batch:
            CarFitment.objects.bulk_create(batch)

        self.stdout.write(self.style.SUCCESS(f'Done! Created {created} fitment records'))

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

    def create_fitment(self, record):
        """Create CarFitment object from record"""
        # Table structure:
        # 0: id, 1: vendor, 2: car, 3: year, 4: modification
        # 5: pcd, 6: diametr, 7: gaika
        # 8: zavod_shini, 9: zamen_shini, 10: tuning_shini
        # 11: zavod_diskov, 12: zamen_diskov, 13: tuning_diski, 14: url

        if len(record) < 14:
            return None

        vendor = self.clean_value(record[1])
        car = self.clean_value(record[2])

        if not vendor or not car:
            return None

        return CarFitment(
            vendor=vendor[:100],
            car=car[:100],
            year=self.clean_value(record[3])[:50],
            modification=self.clean_value(record[4])[:200],
            pcd=self.clean_value(record[5])[:50],
            center_bore=self.clean_value(record[6])[:50],
            bolt_type=self.clean_value(record[7])[:100],
            oem_tires=self.clean_value(record[8]),
            replacement_tires=self.clean_value(record[9]),
            tuning_tires=self.clean_value(record[10]),
            oem_wheels=self.clean_value(record[11]),
            replacement_wheels=self.clean_value(record[12]),
            tuning_wheels=self.clean_value(record[13]),
        )
