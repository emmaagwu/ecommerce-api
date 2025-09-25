from rest_framework import serializers
from .models import (
    Category,
    Brand,
    Size,
    Color,
    Tag,
    Subcategory,
    Product
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class SubcategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(source='category.id', read_only=True)

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category', 'category_id']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(source='category.id', required=False, allow_null=True, write_only=True)
    subcategory = SubcategorySerializer(read_only=True)
    subcategory_id = serializers.UUIDField(source='subcategory.id', required=False, allow_null=True, write_only=True)
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.UUIDField(source='brand.id', required=False, allow_null=True, write_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    size_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, write_only=True
    )
    colors = ColorSerializer(many=True, read_only=True)
    color_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'price',
            'original_price',
            'description',
            'image',
            'images',
            'in_stock',
            'created_at',
            'rating',
            'review_count',
            'category',
            'category_id',
            'subcategory',
            'subcategory_id',
            'brand',
            'brand_id',
            'sizes',
            'size_ids',
            'colors',
            'color_ids',
            'tags',
            'tag_ids',
        ]
        read_only_fields = ['id', 'created_at', 'rating', 'review_count']

    def create(self, validated_data):
        # Pop related fields
        category_id = validated_data.pop('category', {}).get('id', None)
        subcategory_id = validated_data.pop('subcategory', {}).get('id', None)
        brand_id = validated_data.pop('brand', {}).get('id', None)
        size_ids = validated_data.pop('size_ids', [])
        color_ids = validated_data.pop('color_ids', [])
        tag_ids = validated_data.pop('tag_ids', [])

        product = Product.objects.create(
            **validated_data,
            category=Category.objects.get(id=category_id) if category_id else None,
            subcategory=Subcategory.objects.get(id=subcategory_id) if subcategory_id else None,
            brand=Brand.objects.get(id=brand_id) if brand_id else None,
        )

        if size_ids:
            product.sizes.set(Size.objects.filter(id__in=size_ids))
        if color_ids:
            product.colors.set(Color.objects.filter(id__in=color_ids))
        if tag_ids:
            product.tags.set(Tag.objects.filter(id__in=tag_ids))

        return product

    def update(self, instance, validated_data):
        # Pop related fields
        category_id = validated_data.pop('category', {}).get('id', None)
        subcategory_id = validated_data.pop('subcategory', {}).get('id', None)
        brand_id = validated_data.pop('brand', {}).get('id', None)
        size_ids = validated_data.pop('size_ids', None)
        color_ids = validated_data.pop('color_ids', None)
        tag_ids = validated_data.pop('tag_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if category_id is not None:
            instance.category = Category.objects.get(id=category_id)
        if subcategory_id is not None:
            instance.subcategory = Subcategory.objects.get(id=subcategory_id)
        if brand_id is not None:
            instance.brand = Brand.objects.get(id=brand_id)

        instance.save()

        if size_ids is not None:
            instance.sizes.set(Size.objects.filter(id__in=size_ids))
        if color_ids is not None:
            instance.colors.set(Color.objects.filter(id__in=color_ids))
        if tag_ids is not None:
            instance.tags.set(Tag.objects.filter(id__in=tag_ids))

        return instance