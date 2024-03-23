from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from xpoarena.serializers import BoothSerializer, GamesSerializer, ThemeSerializer, BoothCustomizationSerializer, OrganizationSerializer
from .models import Booth, Game, Theme, BoothCustomization, UserProfile
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.shortcuts import redirect
from django.shortcuts import HttpResponseRedirect
from allauth.socialaccount.models import SocialAccount
import logging
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse


# Get an instance of a logger
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_auth(request):
    if request.user.is_authenticated:
        # User is authenticated
        return JsonResponse({"authenticated": True})
    else:
        # User is not authenticated
        return JsonResponse({"authenticated": False})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_organization(request):
    data = request.data
    data['created_by'] = request.user.pk
    serializer = OrganizationSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_and_profile(request):
    user = request.user

    # Update User fields
    user.first_name = request.data.get('first_name', user.first_name)
    user.last_name = request.data.get('last_name', user.last_name)
    user.save()

    # Retrieve or initialize the user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Update non-file fields
    profile.role = request.data.get('role')
    profile.profile_picture_url = request.data.get('profile_picture_url', profile.profile_picture_url)
    
    # Handle file field separately
    if 'profile_picture' in request.FILES:
        profile.profile_picture = request.FILES['profile_picture']
    
    profile.save()

    return Response({"message": "User and profile updated successfully."})



@api_view(['GET'])
def user_details(request):
    if not request.user.is_authenticated:
        return Response({'error': 'User is not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    user_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'has_profile': False, 
    }

    # Check for social account information
    try:
        social_account = SocialAccount.objects.get(user=user, provider='google')
        user_data.update({
            'social_name': social_account.extra_data.get('name', ''),
            'email': social_account.extra_data.get('email', ''),
            'social_picture': social_account.extra_data.get('picture', ''),
        })
    except SocialAccount.DoesNotExist:
        # No action needed if there is no social account
        pass

    # Check if the user has a UserProfile
    try:
        UserProfile.objects.get(user=user)
        user_data['has_profile'] = True  # Update the flag if the UserProfile exists
    except UserProfile.DoesNotExist:
        # No action needed if there is no UserProfile
        pass
    
    return Response(user_data)


@api_view(['GET', 'POST', 'PATCH'])
@parser_classes([MultiPartParser, FormParser])  

def booth(request):
    if request.method == 'GET':
        if request.query_params:
            id = request.GET.get('id')
            object = Booth.objects.get(id=id)
            serializer = BoothSerializer(object)
            return Response(serializer.data)
        else:
            objects = Booth.objects.all()
            serializer = BoothSerializer(objects, many=True)
            return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data
        serializer = BoothSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PATCH'])
@parser_classes([MultiPartParser, FormParser])  
def update_booth(request, booth_id):
    if request.method == 'PATCH':
        data = request.data
        if not booth_id:
            return Response({"error": "No booth ID provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            booth_object = Booth.objects.get(id=booth_id)
        except Booth.DoesNotExist:
            return Response({"error": "Booth not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BoothSerializer(booth_object, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@parser_classes([MultiPartParser, FormParser])  
def update_game(request, title):
    if request.method == 'PATCH':
        data = request.data
        if not title:
            return Response({"error": "No game title provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            game_object = Game.objects.get(title=title)
        except Booth.DoesNotExist:
            return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GamesSerializer(game_object, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        try:
            game_object = Game.objects.get(title=title)
        except Game.DoesNotExist:
            return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)

        game_object.delete()
        return Response({"success": f"Booth {title} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        
@api_view(['GET', 'POST'])
def games(request):
    if request.method == 'GET':
        if request.query_params:
            id = request.GET.get('id', None)
            title = request.GET.get('title', None)

            if id is not None:
                objects = Game.objects.filter(booth_id = id)
                serializer = GamesSerializer(objects, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            if title is not None:
                object = Game.objects.get(title=title)
                serializer = GamesSerializer(object)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            objects = Game.objects.all()
            serializer = GamesSerializer(objects, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data
        serializer = GamesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
def theme(request):
    if request.method == 'POST':
        serializer = ThemeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        if 'name' in request.query_params:
            name = request.GET.get('name')
            object = Theme.objects.get(name=name)
            serializer = ThemeSerializer(object)
            return Response(serializer.data)
        elif 'id' in request.query_params:
            id = request.GET.get('id')
            object = Theme.objects.get(id=id)
            serializer = ThemeSerializer(object)
            return Response(serializer.data)

@api_view(['POST', 'GET'])
def customizedBooth(request):
    if request.method == 'POST':
        data = request.data
        serializer = BoothCustomizationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        if request.query_params:
            id = request.GET.get('id')
            object = BoothCustomization.objects.get(booth_id=id)
            serializer = BoothCustomizationSerializer(object)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        

@api_view(['PUT'])
def update_booth_customization(request, pk):
    try:
        booth_customization = BoothCustomization.objects.get(pk=pk)
    except BoothCustomization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = BoothCustomizationSerializer(booth_customization, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        try:
            UserProfile.objects.get(user=user)
            has_profile = True
        except UserProfile.DoesNotExist:
            has_profile = False
        return Response({"detail": "Login successful", "has_profile": has_profile}, status=200)
    else:
        return Response({"detail": "Invalid credentials"}, status=400)
    

@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password1 = request.data.get('password1')
    password2 = request.data.get('password2')

    if password1 != password2:
        return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate the password against Django's password validation settings
        validate_password(password1)

        # Create a new user. Note: You should handle more cases here, such as existing users.
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        return Response({"detail": "Signup successful"}, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        logger.error(f"Validation error during signup: {e.messages}")
        return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def google_login(request):
    google_login_url = '/accounts/google/login'
    return HttpResponseRedirect(google_login_url)