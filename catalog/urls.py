# urls.py (in your app)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for ViewSets
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'sizes', views.SizeViewSet)
router.register(r'colors', views.ColorViewSet)
router.register(r'tags', views.TagViewSet)

urlpatterns = [
    # Include ViewSet routes (no 'api/' prefix since it's already in main urls.py)
    path('', include(router.urls)),

    # Custom endpoints
    path('filters/', views.filters_view, name='filters'),
    path('categories/all/', views.categories_view, name='categories-all'),
    path('brands/all/', views.brands_view, name='brands-all'),
    path('sizes/all/', views.sizes_view, name='sizes-all'),
    path('colors/all/', views.colors_view, name='colors-all'),
    path('tags/all/', views.tags_view, name='tags-all'),
]