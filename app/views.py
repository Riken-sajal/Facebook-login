import requests
import random
from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import urlencode
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile
from django.utils import timezone
from django.urls import reverse

User = get_user_model()

def facebook_sign_in(request):
    facebook_auth_url = "https://www.facebook.com/v12.0/dialog/oauth"

    if 'localhost' in request.get_host():
        redirect_uri = 'http://localhost:5173/API/facebook-auth-receiver/'  # Update this to match your frontend
    else:
        redirect_uri = request.build_absolute_uri(reverse('facebook_exchange_code_for_token'))

    params = {
        "client_id": settings.SOCIAL_AUTH_FACEBOOK_KEY,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "email",
    }
    
    return redirect(f"{facebook_auth_url}?{urlencode(params)}")

@csrf_exempt
def facebook_exchange_code_for_token(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "Authorization code is missing"}, status=400)

    token_url = "https://graph.facebook.com/v12.0/oauth/access_token"
    
    if 'localhost' in request.get_host():
        redirect_uri = 'http://localhost:5173/API/facebook-auth-receiver/'
    else:
        redirect_uri = request.build_absolute_uri(reverse('facebook_exchange_code_for_token'))

    data = {
        "code": code,
        "client_id": settings.SOCIAL_AUTH_FACEBOOK_KEY,
        "client_secret": settings.SOCIAL_AUTH_FACEBOOK_SECRET,
        "redirect_uri": redirect_uri,
    }

    # Get tokens from Facebook
    token_response = requests.get(token_url, params=data)
    if token_response.status_code != 200:
        return JsonResponse({"error": "Failed to retrieve tokens from Facebook"}, status=400)

    token_response_data = token_response.json()
    access_token = token_response_data.get('access_token')

    if not access_token:
        return JsonResponse({"error": "Access token is missing"}, status=400)

    # Get user info from Facebook API
    user_info_url = f"https://graph.facebook.com/me?access_token={access_token}&fields=id,name,email,picture"
    user_info_response = requests.get(user_info_url)

    if user_info_response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch user info from Facebook"}, status=400)

    user_data = user_info_response.json()
    
    # Get or create the user
    user = User.objects.filter(email=user_data['email']).first()
    if not user:
        username = user_data['name'] + str(random.randint(100000, 99999999999))
        user = User.objects.create(email=user_data['email'], username=username, password=username + "@1234")
    
    # Generate tokens for the user
    refresh = RefreshToken.for_user(user)
    
    # Get user profile information
    try:
        profile = Profile.objects.get(user=user)
        user_name = profile.user.username
        userid = profile.user.id
        pic = request.build_absolute_uri(profile.profile_pic.url)
    except Profile.DoesNotExist:
        user_name = user.username
        userid = user.id
        pic = None

    # Mark user as verified
    user.profile.is_verified = True
    user.profile.save()

    # Update last login time
    user.last_login = timezone.now()
    user.save()

    # Return the response with tokens and user info
    return JsonResponse({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        "user": {
            "user_id": userid,
            'username': user_name,
            'pic': pic,
        }
    }, status=200)
