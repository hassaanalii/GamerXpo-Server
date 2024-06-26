from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from xpoarena.serializers import *
from .models import Booth, Game, Theme, BoothCustomization, UserProfile, Organization, PaymentHistory
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
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
import uuid
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from urllib.parse import unquote
from rest_framework.parsers import JSONParser




logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
API_URL = "http://localhost:8000"

def authenticate_for_token(request):
    user = request.user
    if user.is_authenticated:
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        # Redirect to your frontend with the token
        frontend_url = f"http://localhost:3000/signup/completeprofile/?access={access_token}&refresh={refresh}"
        return redirect(frontend_url)
    else:
        return redirect('login')
    
@api_view(['GET'])
def conversations_list(request):
    serializer = ConversationListSerializer(request.user.conversations.all(), many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def conversations_detail(request, pk):
    conversation = request.user.conversations.get(pk=pk)

    conversation_serializer = ConversationDetailSerializer(conversation, many=False)
    messages_serializer = ConversationMessageSerializer(conversation.messages.all(), many=True)

    return JsonResponse({
        'conversation': conversation_serializer.data,
        'messages': messages_serializer.data
        
    }, safe=False)


@api_view(['GET'])
def conversations_start(request, user_id):
    print(user_id)
    conversations = Conversation.objects.filter(users__in=[user_id]).filter(users__in=[request.user.id])

    if conversations.count() > 0:
        conversation = conversations.first()
        
        return JsonResponse({'success': True, 'conversation_id': conversation.id})
    else:
        user = User.objects.get(pk=user_id)
        conversation = Conversation.objects.create()
        conversation.users.add(request.user)
        conversation.users.add(user)

        return JsonResponse({'success': True, 'conversation_id': conversation.id})



@api_view(['POST'])
def create_sponsorship(request):
    try:
        print(request.data.get('event'))
        # Extract event ID from request data
        event_id = request.data.get('event')
        if not event_id:
            return Response({'error': 'Event ID must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the event based on the provided ID
        event = Event.objects.get(id=event_id)

        # Prepare data for the serializer
        sponsorship_data = {
            'event': event.id,
            'package': request.data.get('package'),
            'name': request.data.get('name'),
            'price': request.data.get('price'),
            'details': request.data.get('details'),
            'logo': request.FILES.get('logo')  # Handle file upload
        }

        # Serialize data
        serializer = SponsorshipSerializer(data=sponsorship_data)
        if serializer.is_valid():
            serializer.save()

            # Update the event sponsorship status based on the package type
            package_type = request.data.get('package')
            if package_type == 'Gold':
                event.gold_sponsor = True
            elif package_type == 'Silver':
                event.silver_sponsor = True
            elif package_type == 'Bronze':
                event.bronze_sponsor = True
            event.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
# or use [IsAuthenticated] if you want to limit access
@permission_classes([AllowAny])
def get_event(request):
    events = Event.objects.all()
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sponsorships(request):
    event_id = request.query_params.get('event_id')
    if event_id:
        sponsorships = Sponsorship.objects.filter(event__id=event_id)
    else:
        sponsorships = Sponsorship.objects.all()
    serializer = SponsorshipSerializer(sponsorships, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_events_for_landing(request):
    events = Event.objects.all()
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def event_edit(request, pk):
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return JsonResponse({'message': 'The event does not exist'}, status=404)

    if request.method == 'PATCH':
        data = JSONParser().parse(request)
        serializer = EventSerializer(event, data=data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_id(request, title):
    try:
        # Decode the URL-encoded title
        decoded_title = unquote(title)
        
        # Retrieve the game using the decoded title
        game = get_object_or_404(Game, title=decoded_title)
        
        # Return the game ID
        return Response({"game_id": game.id}, status=status.HTTP_200_OK)
    except Exception as e:
        # Catch any other exceptions
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_feedback(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    feedback_text = request.POST.get('feedback_text')

    data = {
        'game': game.id,
        'feedback_text': feedback_text,
        'submitted_by': request.user.id 
    }

    serializer = GameFeedbackSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feedbacks(request, game_id):
    feedbacks = GameFeedback.objects.filter(game_id=game_id).order_by('-created_at') 
    serializer = GameFeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
def update_feedback(request, feedback_id):
    feedback = get_object_or_404(
        GameFeedback, pk=feedback_id, submitted_by=request.user)
    serializer = GameFeedbackSerializer(
        feedback, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(
        GameFeedback, pk=feedback_id, submitted_by=request.user)
    feedback.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booth_organization(request, booth_id):
    try:
        # Get the booth object
        booth = get_object_or_404(Booth, id=booth_id)
        
        # Check if the booth has an associated organization
        organization_id = booth.organization.id if booth.organization else None
        
        # Return the response
        return Response({"organization_id": organization_id}, status=status.HTTP_200_OK)
    except Exception as e:
        # Catch any other exceptions
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_booth_association(request, organization_id):
    try:
        # Check if there is any Booth associated with the given organization_id
        is_associated = Booth.objects.filter(organization_id=organization_id).exists()

        # Return the response
        return Response({"is_associated": is_associated}, status=status.HTTP_200_OK)
    except Exception as e:
        # Catch any other exceptions
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_events(request):
    try:
        # Fetch all events with their associated organizations
        events = Event.objects.select_related('organization').all()

        # Serialize the event data
        serializer = EventSerializer(events, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # Catch any other exceptions
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_event_by_id(request, event_id):
    try:
        # Fetch the event by ID with its associated organization
        event = Event.objects.select_related('organization').get(id=event_id)

        # Serialize the event data
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        # Return an error if the event is not found
        return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Catch any other exceptions
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lead_events(request, username):
    try:
        # Find the user by username
        user = User.objects.get(username=username)
        print(user.id)

        # Retrieve the organization created by the user
        organization = Organization.objects.get(created_by=user.id)
        print(organization.id)

        # Fetch all events associated with this organization
        events = Event.objects.filter(organization=organization.id)
        print(events)

        # Serialize the event data, including sponsorships
        serializer = EventSerializer(events, many=True)
        print(serializer.data)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Organization.DoesNotExist:
        return Response({'error': 'No organization found for this user.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Catch any other exceptions
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_developer_events(request, username):
    try:
        # Find the user by username
        user = User.objects.get(username=username)
        print(user.id)

        user_profile = UserProfile.objects.get(user=user.id)
        print(user_profile.organization)
        if user_profile.organization is None:
            return Response({"message": "This developer is not associated with any organization."}, status=status.HTTP_200_OK)
      
        organization_id = user_profile.organization.id
        print(organization_id)
      
        
        # Fetch all events associated with this organization
        events = Event.objects.filter(organization=organization_id)
        print(events)

        # Serialize the event data
        serializer = EventSerializer(events, many=True)
        print(serializer.data)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Organization.DoesNotExist:
        return Response({'error': 'No organization found for this user.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Catch any other exceptions
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    user = request.user  # Retrieve the authenticated user
    try:
        # Get the organization where the current user is the creator
        organization = Organization.objects.get(created_by=user)
        room_id = str(uuid.uuid4())
        # Extract event data from request data
        event_data = {
            'eventName': request.data.get('eventName'),
            'description': request.data.get('description'),
            'dateOfEvent': request.data.get('dateOfEvent'),
            'startTime': request.data.get('startTime'),
            'endTime': request.data.get('endTime'),
            'image': request.FILES.get('image'),
            'room_id': room_id,
        }

        # Serialize data with custom serializer
        serializer = CreateEventSerializer(data=event_data, context={'organization_id': organization.id})
        if serializer.is_valid():
            event = serializer.save()  # Save if valid
            # Use the full EventSerializer to return the created event with organization details
            event_serializer = EventSerializer(event)
            return Response(event_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found for this user.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile_picture(request, username):
    try:
        # Retrieve the User object based on the username
        user = User.objects.get(username=username)

        # Retrieve the UserProfile object linked to the User
        user_profile = UserProfile.objects.get(user=user)

        # Check the profile_picture field
        if user_profile.profile_picture and hasattr(user_profile.profile_picture, 'url'):
            return Response({'profile_picture': request.build_absolute_uri(user_profile.profile_picture.url)})

        # If profile_picture is not set, check profile_picture_url
        if user_profile.profile_picture_url:
            if user_profile.profile_picture_url.lower() != "null":
                return Response({'profile_picture_url': user_profile.profile_picture_url})
            else:
                return Response({'message': 'No images'})

        # If both are empty or null
        return Response({'message': 'No images'})

    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'UserProfile not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_role_by_username(request, username):
    try:
        user = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user_id=user.id)
        
        # Return the Role field from the UserProfile
        return Response({'role': user_profile.role})
    except User.DoesNotExist:
        # If no User exists with the given username, return an error message
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        # If no UserProfile exists for the user, return an error message
        return Response({'error': 'UserProfile not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_games_by_booth_and_genre(request):
    booth_id = request.query_params.get('booth_id')
    genre = request.query_params.get('genre')
    
    if booth_id is None or genre is None:
        return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

    games = Game.objects.filter(booth_id=booth_id, genre=genre)
    serializer = GamesSerializer(games, many=True)
    
    return Response(serializer.data)

@api_view(['POST'])
def create_checkout_session(request, pk):
    try:
        game = Game.objects.get(id=pk)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(game.price * 100),
                        'product_data': {
                            'name': game.title,
                            'images': [game.image.url if game.image else None],
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "game_id": game.id
            },
            mode='payment',
            success_url=settings.SITE_URL + '?success=true',
            cancel_url=settings.SITE_URL + '?canceled=true',
        )
        return Response({'url': checkout_session.url})
    except Game.DoesNotExist:
        return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Something went wrong while creating Stripe session', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@method_decorator(csrf_exempt, name='dispatch')
@api_view(['POST'])
def stripe_webhook_view(request):
    if request.method == 'POST':
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_SECRET_WEBHOOK
            )
        except ValueError as e:
            return HttpResponse('Invalid payload', status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse('Invalid signature', status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_email = session['customer_details']['email']
            game_id = session['metadata']['game_id']
            game = Game.objects.get(id=game_id)
            print(customer_email)
            print(game_id)

            print(game)
            # Sending confirmation email
            send_mail(
                subject="Payment successful",
                message=f"Thank you for purchasing {game.title}! Here is your download link: {game.game_download_link}",
                recipient_list=[customer_email],
                from_email=settings.EMAIL_HOST_USER
            )

            # Create payment history
            PaymentHistory.objects.create(game=game, payment_status=True)

            return HttpResponse('Webhook handled', status=200)

        # Other webhook events...
        return HttpResponse('Webhook received', status=200)
    return HttpResponse('Method not allowed', status=405)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def remove_user_from_organization(request, user_id):
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        
        # Check if the requesting user is allowed to remove the user
        if request.user != user_profile.user and request.user != user_profile.organization.created_by:
            return Response({'error': 'You do not have permission to remove this user.'}, status=status.HTTP_403_FORBIDDEN)
        
        user_profile.organization_id = None
        user_profile.save()
        return Response({'message': 'User removed from the organization successfully.'})
    except UserProfile.DoesNotExist:
        return Response({'error': 'UserProfile not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_developers(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if not user_profile.organization_id:
            return Response({'error': 'This user does not belong to any organization.'}, status=400)

        developer_profiles = UserProfile.objects.filter(
            organization_id=user_profile.organization_id,
            role='Developer'
        ).select_related('user')  # Optimizes the query to fetch related User data

        serializer = MyUserProfileSerializer(developer_profiles, many=True)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({'error': 'UserProfile for the user does not exist.'}, status=404)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_organization_in_user_profile(request):
    organization_id = request.data.get('organization_id')
    if not organization_id:
        return Response({"error": "Organization ID is required."}, status=400)

    try:
        organization = Organization.objects.get(id=organization_id)
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.organization = organization
        user_profile.save()
        return Response({"message": "User profile updated successfully with new organization."})
    except Organization.DoesNotExist:
        return Response({"error": "Organization not found."}, status=404)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found."}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_organization(request):
    secret_key = request.data.get('secret_key')
    if not secret_key:
        return JsonResponse({"error": "Secret key is required."}, status=400)
    try:
        organization = Organization.objects.get(secret_key=secret_key)
        return JsonResponse({"organization_id": organization.id})
    except Organization.DoesNotExist:
        return JsonResponse({"error": "Invalid secret key."}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_details_by_id(request, org_id):
    # Retrieve the organization matching the provided ID
    organization = get_object_or_404(Organization, id=org_id)
    serializer = OrganizationSerializer(organization)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_organization_id(request):
    # Get the UserProfile of the currently authenticated user
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    # Return organization_id if it exists, otherwise return null
    organization_id = user_profile.organization_id if user_profile.organization else None
    return Response({'organization_id': organization_id})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_organization(request):
    try:
        organization = Organization.objects.get(created_by=request.user)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrganizationSerializer(organization, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_id_from_userprofile(request, user_id):
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        # Assuming the UserProfile model has an organization field that is a ForeignKey to Organization
        organization_id = user_profile.organization_id if user_profile.organization else None
        return Response({'organization_id': organization_id})
    except UserProfile.DoesNotExist:
        return Response({'error': 'UserProfile not found.'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_details(request):
    user = request.user
    try:
        # Assuming there's only one organization per user
        organization = Organization.objects.get(created_by=user)
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)
    except Organization.DoesNotExist:
        return Response({'error': 'No organization found for user.'}, status=404)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_profile_with_organization(request, user_id):
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        organization_id = request.data.get('organization')
        user_profile.organization_id = organization_id
        user_profile.save()
        return Response({"message": "UserProfile updated successfully."}, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user_details(request):
    try:
        user = request.user
        data = request.data

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.username = data.get('username', user.username)
        
        user.save()

        return Response({
            'message': 'User updated successfully',
            'data': {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_usernames(request):
    users = User.objects.all()
    usernames = [user.username for user in users]
    
    return JsonResponse({'usernames': usernames})



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
    secret_key = str(uuid.uuid4())
    data['secret_key'] = secret_key

    serializer = OrganizationSerializer(data=data)

    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response({**serializer.data}, status=status.HTTP_201_CREATED)
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
@permission_classes([IsAuthenticated])
def get_user_id_and_username(request):
    if request.user.is_authenticated:
        user_data = {
            'userId': request.user.id,
            'username': request.user.username,  # Adding the username to the response
        }
        return JsonResponse(user_data)
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_information(request):
    user = request.user
    user_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': None,
    }

    try:
        profile = user.profile
        user_data['profile_picture'] = profile.profile_picture.url if profile.profile_picture else None
        user_data['profile_picture_url'] = profile.profile_picture_url
        user_data['role'] = profile.role
    except UserProfile.DoesNotExist:
        # Handle case where user does not have a profile yet
        user_data['profile_picture'] = None
        user_data['profile_picture_url'] = None

    return JsonResponse(user_data)

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
        # Check if an 'id' parameter is provided in the query string
        id = request.GET.get('id')
        # Additionally, check for a 'query' parameter for filtering by name or any other field
        query = request.GET.get('query')

        if id:
            # Fetch a specific booth by id
            try:
                object = Booth.objects.get(id=id)
            except Booth.DoesNotExist:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = BoothSerializer(object)
            return Response(serializer.data)

        elif query:
            # Filter booths based on the provided query parameter
            objects = Booth.objects.filter(Q(name__icontains=query))
            serializer = BoothSerializer(objects, many=True)
            return Response(serializer.data)

        else:
            # Return all booths if no 'id' or 'query' parameter is provided
            objects = Booth.objects.all()
            serializer = BoothSerializer(objects, many=True)
            return Response(serializer.data)

    elif request.method == 'POST':
        # Handling POST request logic remains unchanged
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

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        try:
            UserProfile.objects.get(user=user)
            has_profile = True
        except UserProfile.DoesNotExist:
            has_profile = False

        return Response({
            "detail": "Login successful",
            "has_profile": has_profile,
            "access": str(access_token),
            "refresh": str(refresh)
        }, status=200)
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