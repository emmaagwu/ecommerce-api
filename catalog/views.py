from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, NumberFilter, BooleanFilter
from .models import Product, Category, Subcategory, Brand, Size, Color, Tag
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    SubcategorySerializer,
    BrandSerializer,
    SizeSerializer,
    ColorSerializer,
    TagSerializer,
)

# ----------- Filters for Product -----------
class ProductFilter(FilterSet):
    category = CharFilter(field_name="category__name", lookup_expr="iexact")
    subcategory = CharFilter(field_name="subcategory__name", lookup_expr="iexact")
    brands = CharFilter(method="filter_brands")
    sizes = CharFilter(method="filter_sizes")
    colors = CharFilter(method="filter_colors")
    minPrice = NumberFilter(field_name="price", lookup_expr="gte")
    maxPrice = NumberFilter(field_name="price", lookup_expr="lte")
    inStock = BooleanFilter(field_name="in_stock")

    def filter_brands(self, queryset, name, value):
        brands = [v.strip() for v in value.split(",") if v.strip()]
        if brands:
            return queryset.filter(brand__name__in=brands)
        return queryset

    def filter_sizes(self, queryset, name, value):
        sizes = [v.strip() for v in value.split(",") if v.strip()]
        if sizes:
            return queryset.filter(sizes__name__in=sizes).distinct()
        return queryset

    def filter_colors(self, queryset, name, value):
        colors = [v.strip() for v in value.split(",") if v.strip()]
        if colors:
            return queryset.filter(colors__name__in=colors).distinct()
        return queryset

    class Meta:
        model = Product
        fields = []

# ----------- Product ViewSet -----------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related(
        "sizes", "colors", "tags"
    ).select_related(
        "category", "subcategory", "brand"
    ).all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = ProductFilter
    ordering_fields = [
        "created_at", "price", "rating", "review_count", "name"
    ]
    ordering = ["-created_at"]
    search_fields = [
        "name", "description", "brand__name", "tags__name"
    ]

    def list(self, request, *args, **kwargs):
        """
        Overridden to provide the filter metadata, price range, and total count
        in the response, similar to your Next.js API.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True) if page is not None else self.get_serializer(queryset, many=True)

        # Filter metadata
        categories = Category.objects.values_list("name", flat=True)
        subcategories = Subcategory.objects.values_list("name", flat=True)
        brands = Brand.objects.values_list("name", flat=True)
        colors = Color.objects.values_list("name", flat=True)
        sizes = Size.objects.values_list("name", flat=True)
        prices = Product.objects.values_list("price", flat=True)
        price_list = list(prices)
        price_range = {
            "min": min(price_list) if price_list else 0,
            "max": max(price_list) if price_list else 0,
        }

        # Handle limit safely
        limit = request.query_params.get("limit")
        if limit is not None:
            limit = int(limit)
        elif getattr(self, "paginator", None) and getattr(self.paginator, "page_size", None):
            limit = self.paginator.page_size
        else:
            limit = 12

        response_data = {
            "products": serializer.data,
            "total": queryset.count(),
            "page": int(request.query_params.get("page", 1)),
            "limit": limit,
            "totalPages": self.paginator.page.paginator.num_pages if page is not None and hasattr(self, "paginator") else 1,
            "filters": {
                "categories": list(categories),
                "subcategories": list(subcategories),
                "brands": list(brands),
                "colors": list(colors),
                "sizes": list(sizes),
                "priceRange": price_range,
            },
        }
        if page is not None:
            return self.get_paginated_response(response_data)
        return Response(response_data)

# ----------- Category ViewSet -----------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# ----------- Subcategory ViewSet -----------
class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

# ----------- Brand ViewSet -----------
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

# ----------- Size ViewSet -----------
class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer

# ----------- Color ViewSet -----------
class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

# ----------- Tag ViewSet -----------
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer