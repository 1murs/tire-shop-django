import csv
from django.core.management.base import BaseCommand
from catalog.models import CarFitment


class Command(BaseCommand):
    help = "Import car fitment data from CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        self.stdout.write(f"Importing data from {csv_file}...")

        # Clear existing data
        CarFitment.objects.all().delete()
        self.stdout.write("Cleared existing car fitment data.")

        imported = 0
        errors = 0

        # Try different encodings
        encodings = ["cp1251", "utf-8", "iso-8859-1"]

        for encoding in encodings:
            try:
                with open(csv_file, "r", encoding=encoding) as f:
                    # Read first line to check encoding
                    first_line = f.readline()
                    if "vendor" in first_line.lower() or "Acura" in first_line:
                        self.stdout.write(f"Using encoding: {encoding}")
                        break
            except UnicodeDecodeError:
                continue
        else:
            encoding = "cp1251"

        with open(csv_file, "r", encoding=encoding, errors="replace") as f:
            reader = csv.DictReader(f, delimiter=";")

            batch = []
            batch_size = 1000

            for row in reader:
                try:
                    fitment = CarFitment(
                        vendor=row.get("vendor", "").strip(),
                        car=row.get("car", "").strip(),
                        year=row.get("year", "").strip(),
                        modification=row.get("modification", "").strip(),
                        pcd=row.get("pcd", "").strip(),
                        center_bore=row.get("diametr", "").strip(),
                        bolt_type=row.get("gaika", "").strip(),
                        oem_tires=row.get("zavod_shini", "").strip(),
                        replacement_tires=row.get("zamen_shini", "").strip(),
                        tuning_tires=row.get("tuning_shini", "").strip(),
                        oem_wheels=row.get("zavod_diskov", "").strip(),
                        replacement_wheels=row.get("zamen_diskov", "").strip(),
                        tuning_wheels=row.get("tuning_diski", "").strip(),
                    )
                    batch.append(fitment)
                    imported += 1

                    if len(batch) >= batch_size:
                        CarFitment.objects.bulk_create(batch)
                        batch = []
                        self.stdout.write(f"Imported {imported} records...")

                except Exception as e:
                    errors += 1
                    if errors < 10:
                        self.stdout.write(
                            self.style.WARNING(f"Error in row: {e}")
                        )

            # Import remaining batch
            if batch:
                CarFitment.objects.bulk_create(batch)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {imported} records with {errors} errors."
            )
        )
