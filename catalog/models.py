import uuid
from django.db import models
from django.core.exceptions import ValidationError
from .managers import FilterManager, ProductManager

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def clean(self):
        # Case normalization - convert to title case
        if self.name:
            self.name = self.name.strip().title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    objects = FilterManager()

class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    objects = FilterManager()

class Size(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def clean(self):
        if self.name:
            # Sizes should be uppercase for consistency (XL, M, L)
            self.name = self.name.strip().upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    objects = FilterManager()

class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    objects = FilterManager()

class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def clean(self):
        if self.name:
            self.name = self.name.strip().lower()  # Tags typically lowercase

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    objects = FilterManager()

class Subcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    # CHANGED: CASCADE to PROTECT - prevents accidental deletion
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('name', 'category')
        verbose_name_plural = "subcategories"

    def clean(self):
        if self.name:
            self.name = self.name.strip().title()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    objects = FilterManager()

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    originalPrice = models.FloatField(null=True, blank=True)
    description = models.TextField()
    image = models.URLField(blank=True, default="")
    images = models.JSONField(default=list, blank=True)
    inStock = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0, null=True, blank=True)
    reviewCount = models.IntegerField(default=0, null=True, blank=True)

    # CHANGED: SET_NULL to PROTECT for critical relationships
    # This prevents accidental deletion of categories/brands that have products
    category = models.ForeignKey(Category, related_name='products', on_delete=models.PROTECT, null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, related_name='products', on_delete=models.PROTECT, null=True, blank=True)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.PROTECT, null=True, blank=True)

    # Many-to-many relationships remain as-is since they don't trigger cascading deletes
    sizes = models.ManyToManyField(Size, related_name='products', blank=True)
    colors = models.ManyToManyField(Color, related_name='products', blank=True)
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)

    class Meta:
        ordering = ['-createdAt']  # Most recent first by default

    def clean(self):
        # Validate price fields
        if self.price and self.price < 0:
            raise ValidationError("Price cannot be negative")
        if self.originalPrice and self.originalPrice < 0:
            raise ValidationError("Original price cannot be negative")
        if self.rating and (self.rating < 0 or self.rating > 5):
            raise ValidationError("Rating must be between 0 and 5")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    objects = ProductManager()