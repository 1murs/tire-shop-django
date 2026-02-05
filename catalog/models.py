from django.db import models
from decimal import Decimal


class Supplier(models.Model):
    """
    Supplier model - постачальники товарів.
    Визначає націнку та статус наявності.
    """
    name = models.CharField(max_length=200, verbose_name="Назва")
    code = models.CharField(max_length=200, unique=True, verbose_name="Код з прайсу",
                           help_text="Наприклад: kiev_Склад Колёс, kh_DTW Харьков (21 день)")

    is_preorder = models.BooleanField(default=False, verbose_name="Під замовлення",
                                      help_text="Якщо True - товар показується як 'Під замовлення'")

    markup_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                         verbose_name="Націнка %",
                                         help_text="Націнка на ціну постачальника")

    delivery_days = models.CharField(max_length=50, default="1-3 дні",
                                     verbose_name="Термін доставки",
                                     help_text="Відображається на сайті")

    is_active = models.BooleanField(default=True, verbose_name="Активний",
                                    help_text="Неактивні постачальники не імпортуються")

    class Meta:
        ordering = ["name"]
        verbose_name = "Постачальник"
        verbose_name_plural = "Постачальники"

    def __str__(self):
        status = "Під замовлення" if self.is_preorder else "В наявності"
        return f"{self.name} ({status}, +{self.markup_percent}%)"

    def apply_markup(self, price):
        """Застосувати націнку до ціни"""
        if self.markup_percent:
            return price * (1 + self.markup_percent / 100)
        return price


class Brand(models.Model):
    """
    Brand model - stores tire and wheel manufacturers.
    Example: Michelin, Bridgestone, Continental
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name


class Tire(models.Model):
    """
    Tire model - main product of the shop.
    Example: Bridgestone Turanza 6 265/60 R18 110V
    """

    SEASON_SUMMER = "summer"
    SEASON_WINTER = "winter"
    SEASON_ALL = "allseason"

    SEASON_CHOICES = [
        (SEASON_SUMMER, "Summer"),
        (SEASON_WINTER, "Winter"),
        (SEASON_ALL, "All Season"),
    ]

    VEHICLE_PASSENGER = "passenger"
    VEHICLE_SUV = "suv"
    VEHICLE_TRUCK = "truck"
    VEHICLE_VAN = "van"

    VEHICLE_CHOICES = [
        (VEHICLE_PASSENGER, "Легковий"),
        (VEHICLE_SUV, "Позашляховик"),
        (VEHICLE_TRUCK, "Вантажний"),
        (VEHICLE_VAN, "Мікроавтобус"),
    ]

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="tires",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tires",
        verbose_name="Постачальник"
    )

    # Basic info
    model_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)

    # Size specifications
    width = models.PositiveIntegerField()
    profile = models.PositiveIntegerField()
    diameter = models.PositiveIntegerField()

    # Performance specs
    load_index = models.PositiveIntegerField()
    speed_index = models.CharField(max_length=2)
    season = models.CharField(
        max_length=20,
        choices=SEASON_CHOICES,
        default=SEASON_SUMMER,
    )
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_CHOICES,
        default=VEHICLE_PASSENGER,
    )
    studded = models.BooleanField(default=False)

    # Price and stock
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         verbose_name="Закупівельна ціна")
    price = models.DecimalField(max_digits=10, decimal_places=2,
                               verbose_name="Продажна ціна")
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)

    # Meta info
    article = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to="tires/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["brand__name", "model_name"]
        verbose_name = "Tire"
        verbose_name_plural = "Tires"

    def __str__(self):
        return f"{self.brand.name} {self.model_name} {self.width}/{self.profile} R{self.diameter}"


class Disk(models.Model):
    """
    Disk (wheel) model - second main product.
    Example: K&K Drakon 6.5x16 5x114.3 ET45 DIA67.1
    """

    # Disk types
    TYPE_ALLOY = "alloy"
    TYPE_STEEL = "steel"
    TYPE_FORGED = "forged"

    TYPE_CHOICES = [
        (TYPE_ALLOY, "Alloy"),
        (TYPE_STEEL, "Steel"),
        (TYPE_FORGED, "Forged"),
    ]

    # Relationships
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="disks")
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="disks",
        verbose_name="Постачальник"
    )

    # Basic info
    model_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)

    # Size specifications
    diameter = models.PositiveIntegerField()
    width = models.DecimalField(max_digits=3, decimal_places=1)

    # Bolt pattern (PCD)
    bolts = models.PositiveIntegerField()
    pcd = models.DecimalField(max_digits=5, decimal_places=1)
    color = models.CharField(max_length=100, blank=True)

    # Other specs
    dia = models.DecimalField(max_digits=5, decimal_places=1)
    et = models.IntegerField()  # 45 (can be negative)

    # Type
    disk_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_ALLOY
    )

    # Price and stock
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         verbose_name="Закупівельна ціна")
    price = models.DecimalField(max_digits=10, decimal_places=2,
                               verbose_name="Продажна ціна")
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)

    # Meta info
    article = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to="disks/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["brand__name", "model_name"]
        verbose_name = "Disk"
        verbose_name_plural = "Disks"

    def __str__(self):
        return f"{self.brand.name} {self.model_name} {self.width}x{self.diameter} {self.bolts}x{self.pcd}"


class CarFitment(models.Model):
    """
    Car fitment data for tire/wheel calculator.
    Stores OEM and replacement sizes for each car model/year/modification.
    """

    # Car identification
    vendor = models.CharField(max_length=100, db_index=True)  # Manufacturer (BMW, Audi, etc.)
    car = models.CharField(max_length=100, db_index=True)  # Model (X5, A4, etc.)
    year = models.CharField(max_length=50, db_index=True)  # Year or year range
    modification = models.CharField(max_length=200)  # Engine/trim variant

    # Wheel specs
    pcd = models.CharField(max_length=50, blank=True)  # Bolt pattern (5*120)
    center_bore = models.CharField(max_length=50, blank=True)  # Center bore diameter
    bolt_type = models.CharField(max_length=100, blank=True)  # Bolt/nut type

    # Tire sizes (separated by | for multiple options, # for front/rear)
    oem_tires = models.TextField(blank=True)  # Factory tire sizes
    replacement_tires = models.TextField(blank=True)  # Replacement options
    tuning_tires = models.TextField(blank=True)  # Tuning/upgrade options

    # Wheel sizes
    oem_wheels = models.TextField(blank=True)  # Factory wheel sizes
    replacement_wheels = models.TextField(blank=True)  # Replacement options
    tuning_wheels = models.TextField(blank=True)  # Tuning/upgrade options

    class Meta:
        ordering = ["vendor", "car", "year"]
        verbose_name = "Car Fitment"
        verbose_name_plural = "Car Fitments"
        indexes = [
            models.Index(fields=["vendor", "car"]),
            models.Index(fields=["vendor", "car", "year"]),
        ]

    def __str__(self):
        return f"{self.vendor} {self.car} {self.year} {self.modification}"
