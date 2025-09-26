from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    CategoryViewSet,
    SubcategoryViewSet,
    BrandViewSet,
    SizeViewSet,
    ColorViewSet,
    TagViewSet,
    filters_view,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'subcategories', SubcategoryViewSet, basename='subcategory')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'sizes', SizeViewSet, basename='size')
router.register(r'colors', ColorViewSet, basename='color')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
  path('filters/', filters_view, name='filters'),
  path('', include(router.urls)),
]