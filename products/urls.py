from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('<int:product_id>/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path(
        '<int:product_id>/<str:variant_sku>/<slug:product_slug>/',
        views.ProductDetailView.as_view(),
        name='product-detail'
    ),
]
