from django.urls import path
from .views import facebook_sign_in, facebook_exchange_code_for_token

urlpatterns = [
    path('auth/facebook/', facebook_sign_in, name='facebook_sign_in'),
    path('facebook-exchange/', facebook_exchange_code_for_token, name='facebook_exchange_code_for_token'),
]
