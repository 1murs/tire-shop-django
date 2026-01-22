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
