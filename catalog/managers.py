# managers.py
from django.db import models, transaction

class FilterManager(models.Manager):
    def get_or_create_normalized(self, name, normalization_type='title'):
        """
        Normalize the name based on the model type and return (object, created).
        
        normalization_type:
        - 'title': Category, Brand, Color, Subcategory 
        - 'upper': Size
        - 'lower': Tag
        """
        if not name:
            return None, False
        
        name = name.strip()
        if normalization_type == 'title':
            normalized = name.title()
        elif normalization_type == 'upper':
            normalized = name.upper()
        elif normalization_type == 'lower':
            normalized = name.lower()
        else:
            normalized = name
        
        return self.get_or_create(name=normalized)
    
    def with_products(self):
        """
        Return only filters that are linked to at least one product.
        """
        return self.filter(
            products__isnull=False
        ).distinct()

class ProductManager(models.Manager):
    def create_with_filters(self, **validated_data):
        """
        Create a product and automatically upsert related filters.
        Uses transaction for atomicity and single save() call for performance.
        """
        with transaction.atomic():
            # Import here to avoid circular imports
            from .models import Category, Subcategory, Brand, Size, Color, Tag
            
            # Pop relational fields out of validated_data BEFORE creating product
            category_name = validated_data.pop('category_name', None)
            subcategory_name = validated_data.pop('subcategory_name', None)
            brand_name = validated_data.pop('brand_name', None)
            size_names = validated_data.pop('size_names', [])
            color_names = validated_data.pop('color_names', [])
            tag_names = validated_data.pop('tag_names', [])
            
            # Also remove any ID fields that might have been passed
            size_ids = validated_data.pop('size_ids', [])
            color_ids = validated_data.pop('color_ids', [])
            tag_ids = validated_data.pop('tag_ids', [])
            
            # Handle foreign key relations first
            if category_name:
                category, _ = Category.objects.get_or_create_normalized(
                    category_name, 'title'
                )
                validated_data['category'] = category
                
                # Handle subcategory (depends on category)
                if subcategory_name:
                    subcategory, _ = Subcategory.objects.get_or_create(
                        name=subcategory_name.strip().title(),
                        category=category
                    )
                    validated_data['subcategory'] = subcategory
            
            if brand_name:
                brand, _ = Brand.objects.get_or_create_normalized(
                    brand_name, 'title'
                )
                validated_data['brand'] = brand
            
            # Create product with all foreign keys in one save()
            product = self.create(**validated_data)
            
            # Handle many-to-many relationships after product creation
            if size_names or size_ids:
                sizes = []
                # Handle size names
                for size_name in size_names:
                    size, _ = Size.objects.get_or_create_normalized(
                        size_name, 'upper'
                    )
                    sizes.append(size)
                # Handle size IDs
                if size_ids:
                    sizes.extend(Size.objects.filter(id__in=size_ids))
                if sizes:
                    product.sizes.set(sizes)
            
            if color_names or color_ids:
                colors = []
                # Handle color names
                for color_name in color_names:
                    color, _ = Color.objects.get_or_create_normalized(
                        color_name, 'title'
                    )
                    colors.append(color)
                # Handle color IDs
                if color_ids:
                    colors.extend(Color.objects.filter(id__in=color_ids))
                if colors:
                    product.colors.set(colors)
            
            if tag_names or tag_ids:
                tags = []
                # Handle tag names
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create_normalized(
                        tag_name, 'lower'
                    )
                    tags.append(tag)
                # Handle tag IDs
                if tag_ids:
                    tags.extend(Tag.objects.filter(id__in=tag_ids))
                if tags:
                    product.tags.set(tags)
            
            return product
    
    def get_active_filters(self):
        """
        Return a dict of filters that are linked to products.
        Optimized queries with proper joins.
        """
        from .models import Category, Subcategory, Brand, Size, Color, Tag
        
        return {
            'categories': list(Category.objects.with_products().values('id', 'name')),
            'subcategories': list(
                Subcategory.objects
                .filter(products__isnull=False)  # More explicit filter
                .select_related('category')
                .values('id', 'name', 'category__name')
                .distinct()
            ),
            'brands': list(Brand.objects.with_products().values('id', 'name')),
            'sizes': list(Size.objects.with_products().values('id', 'name')),
            'colors': list(Color.objects.with_products().values('id', 'name')),
            'tags': list(Tag.objects.with_products().values('id', 'name')),
        }