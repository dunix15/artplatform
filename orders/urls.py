from django.urls import path

from .views import CancelOrderView


urlpatterns = [
    path("<order_id>/cancel", CancelOrderView.as_view()),
]
