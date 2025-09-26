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

# Keep your existing read-only serializers as-is
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
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category', 'category_name']

class ProductSerializer(serializers.ModelSerializer):
    # Read-only nested serializers for response
    category = CategorySerializer(read_only=True)
    subcategory = SubcategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    colors = ColorSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    # Write-only fields for input - support BOTH IDs and names
    category_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    category_name = serializers.CharField(required=False, allow_blank=True, write_only=True)

    subcategory_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    subcategory_name = serializers.CharField(required=False, allow_blank=True, write_only=True)

    brand_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    brand_name = serializers.CharField(required=False, allow_blank=True, write_only=True)

    size_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, write_only=True
    )
    size_names = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )

    color_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, write_only=True
    )
    color_names = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )

    tag_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, write_only=True
    )
    tag_names = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'originalPrice', 'description', 'image', 'images',
            'inStock', 'createdAt', 'rating', 'reviewCount',
            # Read-only nested objects
            'category', 'subcategory', 'brand', 'sizes', 'colors', 'tags',
            # Write-only input fields
            'category_id', 'category_name', 'subcategory_id', 'subcategory_name',
            'brand_id', 'brand_name', 'size_ids', 'size_names',
            'color_ids', 'color_names', 'tag_ids', 'tag_names'
        ]
        read_only_fields = ['id', 'createdAt', 'rating', 'reviewCount']

    def validate(self, data):
        """
        Ensure either ID or name is provided for each filter type, not both.
        """
        conflicts = []

        if data.get('category_id') and data.get('category_name'):
            conflicts.append('Provide either category_id OR category_name, not both')
        if data.get('subcategory_id') and data.get('subcategory_name'):
            conflicts.append('Provide either subcategory_id OR subcategory_name, not both')
        if data.get('brand_id') and data.get('brand_name'):
            conflicts.append('Provide either brand_id OR brand_name, not both')
        if data.get('size_ids') and data.get('size_names'):
            conflicts.append('Provide either size_ids OR size_names, not both')
        if data.get('color_ids') and data.get('color_names'):
            conflicts.append('Provide either color_ids OR color_names, not both')
        if data.get('tag_ids') and data.get('tag_names'):
            conflicts.append('Provide either tag_ids OR tag_names, not both')

        if conflicts:
            raise serializers.ValidationError(conflicts)

        return data

    def create(self, validated_data):
        """
        Use the ProductManager.create_with_filters() method for upsert functionality.
        """
        # Convert ID-based inputs to name-based for the manager
        manager_data = validated_data.copy()

        # Handle category
        if 'category_id' in validated_data:
            try:
                category = Category.objects.get(id=validated_data.pop('category_id'))
                manager_data['category_name'] = category.name
            except Category.DoesNotExist as err:
                raise serializers.ValidationError({'category_id': 'Category not found'}) from err
        elif 'category_name' in validated_data:
            manager_data['category_name'] = validated_data.pop('category_name')

        # Handle subcategory
        if 'subcategory_id' in validated_data:
            try:
                subcategory = Subcategory.objects.get(id=validated_data.pop('subcategory_id'))
                manager_data['subcategory_name'] = subcategory.name
            except Subcategory.DoesNotExist as err:
                raise serializers.ValidationError({'subcategory_id': 'Subcategory not found'}) from err
        elif 'subcategory_name' in validated_data:
            manager_data['subcategory_name'] = validated_data.pop('subcategory_name')

        # Handle brand
        if 'brand_id' in validated_data:
            try:
                brand = Brand.objects.get(id=validated_data.pop('brand_id'))
                manager_data['brand_name'] = brand.name
            except Brand.DoesNotExist as err:
                raise serializers.ValidationError({'brand_id': 'Brand not found'}) from err
        elif 'brand_name' in validated_data:
            manager_data['brand_name'] = validated_data.pop('brand_name')

        # Handle many-to-many fields
        self._handle_m2m_field('size', Size, validated_data, manager_data)
        self._handle_m2m_field('color', Color, validated_data, manager_data)
        self._handle_m2m_field('tag', Tag, validated_data, manager_data)

        # Use the manager method
        return Product.objects.create_with_filters(**manager_data)

    def _handle_m2m_field(self, field_name, model_class, validated_data, manager_data):
        """Helper method to convert IDs to names for M2M fields"""
        ids_key = f'{field_name}_ids'
        names_key = f'{field_name}_names'

        if ids_key in validated_data:
            ids = validated_data.pop(ids_key)
            try:
                objects = model_class.objects.filter(id__in=ids)
                if len(objects) != len(ids):
                    raise serializers.ValidationError(f'Some {field_name} IDs not found')
                manager_data[names_key] = [obj.name for obj in objects]
            except Exception as err:
                # broad except kept, but we link error chain
                raise serializers.ValidationError(f'Invalid {field_name} IDs') from err
        elif names_key in validated_data:
            manager_data[names_key] = validated_data.pop(names_key)

    def update(self, instance, validated_data):
        """
        Update product. For now, keep the simpler ID-based approach.
        You can enhance this later if needed.
        """
        # Extract filter IDs
        category_id = validated_data.pop('category_id', None)
        subcategory_id = validated_data.pop('subcategory_id', None)
        brand_id = validated_data.pop('brand_id', None)
        size_ids = validated_data.pop('size_ids', None)
        color_ids = validated_data.pop('color_ids', None)
        tag_ids = validated_data.pop('tag_ids', None)

        # Remove name fields (not supported in update for now)
        validated_data.pop('category_name', None)
        validated_data.pop('subcategory_name', None)
        validated_data.pop('brand_name', None)
        validated_data.pop('size_names', None)
        validated_data.pop('color_names', None)
        validated_data.pop('tag_names', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update foreign keys
        if category_id is not None:
            instance.category = Category.objects.get(id=category_id) if category_id else None
        if subcategory_id is not None:
            instance.subcategory = Subcategory.objects.get(id=subcategory_id) if subcategory_id else None
        if brand_id is not None:
            instance.brand = Brand.objects.get(id=brand_id) if brand_id else None

        instance.save()

        # Update many-to-many
        if size_ids is not None:
            instance.sizes.set(Size.objects.filter(id__in=size_ids))
        if color_ids is not None:
            instance.colors.set(Color.objects.filter(id__in=color_ids))
        if tag_ids is not None:
            instance.tags.set(Tag.objects.filter(id__in=tag_ids))

        return instance