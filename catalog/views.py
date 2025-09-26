# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Min, Max

from .models import Product, Category, Brand, Size, Color, Tag
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    BrandSerializer,
    SizeSerializer,
    ColorSerializer,
    TagSerializer
)

class ProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'limit'
    max_page_size = 100

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        """
        Filter products based on query parameters
        """
        queryset = Product.objects.select_related(
            'category', 'subcategory', 'brand'
        ).prefetch_related('sizes', 'colors', 'tags')

        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__name__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)

        # Filter by subcategory
        subcategory = self.request.query_params.get('subcategory')
        if subcategory:
            queryset = queryset.filter(subcategory__name__iexact=subcategory)

        # Filter by brands (comma-separated)
        brands = self.request.query_params.get('brands')
        if brands:
            brand_list = [b.strip() for b in brands.split(',')]
            queryset = queryset.filter(brand__name__in=brand_list)

        # Filter by sizes (comma-separated)
        sizes = self.request.query_params.get('sizes')
        if sizes:
            size_list = [s.strip() for s in sizes.split(',')]
            queryset = queryset.filter(sizes__name__in=size_list).distinct()

        # Filter by colors (comma-separated)
        colors = self.request.query_params.get('colors')
        if colors:
            color_list = [c.strip() for c in colors.split(',')]
            queryset = queryset.filter(colors__name__in=color_list).distinct()

        # Filter by price range
        min_price = self.request.query_params.get('minPrice')
        max_price = self.request.query_params.get('maxPrice')
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))

        # Filter by stock status
        in_stock = self.request.query_params.get('inStock')
        if in_stock is not None:
            queryset = queryset.filter(inStock=in_stock.lower() == 'true')

        # Sorting
        sort_field = self.request.query_params.get('sortField', 'createdAt')
        sort_direction = self.request.query_params.get('sortDirection', 'desc')

        # Map frontend field names to model field names
        sort_mapping = {
            'createdAt': 'createdAt',
            'name': 'name',
            'price': 'price',
            'rating': 'rating',
            'brand': 'brand__name'
        }

        model_sort_field = sort_mapping.get(sort_field, 'createdAt')
        if sort_direction == 'desc':
            model_sort_field = f'-{model_sort_field}'

        queryset = queryset.order_by(model_sort_field)

        return queryset

@api_view(['GET'])
def filters_view(request):
    """
    Return all active filters for frontend dropdowns/checkboxes.
    Only returns filters that are linked to at least one product.
    """
    try:
        # Use the manager method we created
        filters = Product.objects.get_active_filters()

        # Get price range
        price_range = Product.objects.aggregate(
            min=Min('price'),
            max=Max('price')
        )

        response_data = {
            'categories': filters['categories'],
            'subcategories': [
                {
                    'id': sc['id'],
                    'name': sc['name'],
                    'category': sc['category__name']
                } for sc in filters['subcategories']
            ],
            'brands': filters['brands'],
            'sizes': filters['sizes'],
            'colors': filters['colors'],
            'tags': filters['tags'],
            'priceRange': {
                'min': price_range['min'] or 0,
                'max': price_range['max'] or 0
            }
        }

        return Response(response_data)
    except Exception:
        return Response(
            {'error': 'Failed to fetch filters'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def categories_view(request):
    """Get all categories with their subcategories"""
    categories = Category.objects.prefetch_related('subcategories').all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def brands_view(request):
    """Get all brands"""
    brands = Brand.objects.all()
    serializer = BrandSerializer(brands, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def sizes_view(request):
    """Get all sizes"""
    sizes = Size.objects.all()
    serializer = SizeSerializer(sizes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def colors_view(request):
    """Get all colors"""
    colors = Color.objects.all()
    serializer = ColorSerializer(colors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tags_view(request):
    """Get all tags"""
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)

# Optional: If you need individual filter management endpoints
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
