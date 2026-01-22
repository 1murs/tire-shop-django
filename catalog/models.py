from django.db import models


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

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="tires",
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

    # Price and stock
    price = models.DecimalField(max_digits=10, decimal_places=2)
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
    price = models.DecimalField(max_digits=10, decimal_places=2)
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
