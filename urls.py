from django.urls import path
from .zarinpal import SendRequestView, VerifyView

urlpatterns =. [
    path('request/', SendRequestView.as_view(), name='request'),
    path('verify/', VerifyView.as_view(), name='verify'),
]
