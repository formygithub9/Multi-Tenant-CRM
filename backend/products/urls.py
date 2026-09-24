from django.urls import path

from products.views import ProductAPIView


urlpatterns = [
    path("",ProductAPIView.as_view(),name="products",),
    path("<int:product_id>/",ProductAPIView.as_view(),name="product-detail",),
]