from django.urls import path

from quotes.views import QuoteAPIView
from quotes.views import QuoteStatusAPIView


urlpatterns = [
    path("",QuoteAPIView.as_view(),name="quotes",),
    path("<int:quote_id>/",QuoteAPIView.as_view(),name="quote-detail",),
    path("<int:quote_id>/<str:new_status>/",QuoteStatusAPIView.as_view(),name="quote-status",),
]