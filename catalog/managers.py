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
        return self.annotate(
            product_count=models.Count('products')
        ).filter(product_count__gt=0)

class ProductManager(models.Manager):
    def create_with_filters(self, **validated_data):
        """
        Create a product and automatically upsert related filters.
        Uses transaction for atomicity and single save() call for performance.
        """
        with transaction.atomic():
            # Import here to avoid circular imports
            from .models import Category, Subcategory, Brand, Size, Color, Tag
            
            # Pop relational fields out of validated_data
            category_name = validated_data.pop('category_name', None)
            subcategory_name = validated_data.pop('subcategory_name', None)
            brand_name = validated_data.pop('brand_name', None)
            size_names = validated_data.pop('size_names', [])
            color_names = validated_data.pop('color_names', [])
            tag_names = validated_data.pop('tag_names', [])
            
            # Handle foreign key relations first
            category = None
            subcategory = None
            brand = None
            
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
            
            # Handle many-to-many relationships
            if size_names:
                sizes = []
                for size_name in size_names:
                    size, _ = Size.objects.get_or_create_normalized(
                        size_name, 'upper'
                    )
                    sizes.append(size)
                product.sizes.set(sizes)
            
            if color_names:
                colors = []
                for color_name in color_names:
                    color, _ = Color.objects.get_or_create_normalized(
                        color_name, 'title'
                    )
                    colors.append(color)
                product.colors.set(colors)
            
            if tag_names:
                tags = []
                for tag_name in tag_names:
                    tag, _ = Tag.objects.get_or_create_normalized(
                        tag_name, 'lower'
                    )
                    tags.append(tag)
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
                .annotate(product_count=models.Count('products'))
                .filter(product_count__gt=0)
                .select_related('category')
                .values('id', 'name', 'category__name')
            ),
            'brands': list(Brand.objects.with_products().values('id', 'name')),
            'sizes': list(Size.objects.with_products().values('id', 'name')),
            'colors': list(Color.objects.with_products().values('id', 'name')),
            'tags': list(Tag.objects.with_products().values('id', 'name')),
        }