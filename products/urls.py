from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('<str:sku>/<slug:product_slug>/', views.ProductVariantDetailView.as_view(), name='product-variant-detail'),
]
