from xpoarena.views import *
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('booth/', booth),
    path('booth/<int:booth_id>', update_booth),
    path('games/<str:title>', update_game),
    path('games/', games),
    path('theme/', theme),
    path('customizedbooth/', customizedBooth),
    path('customizedbooth/<int:pk>/', update_booth_customization),
    path('login/', login_view, name='custom_login'),
    path('signup/', signup, name='custom_signup'),
    path('google_login/', google_login, name='google_login'),
    path('userdetails/', user_details, name='user_details'),
    path('setprofile/', update_user_and_profile, name='update_user_profile'),
    path('registerorganization/', register_organization, name='register_organization'),
    path('verify/', verify_auth, name='verify'),
    path('userinformation/', user_information, name='user_information'),
    path('usernames/', get_usernames, name='get_usernames'),
    path("updateuser/", update_user_details, name='update_user_details'),
    path("organization/", get_organization_details, name='get_organization_details'),
    path("updateorganization/", update_organization, name='update_organization'),
    path("getuser/", get_user_id_and_username, name='user_id'),
    path("updateuserprofilewithorganization/<int:user_id>/", update_user_profile_with_organization, name='update_organization'),
    path("getorganizationid/<int:user_id>/", get_organization_id_from_userprofile, name='get_organization'),
    path("userorganization/", get_user_organization_id, name='update_organization'),
    path("organizationbyid/<int:org_id>/", get_organization_details_by_id, name='organizationbyid'),
    path('joinorganization/', join_organization, name='join-organization'),
    path('updateorganizationinuserprofile/', update_organization_in_user_profile, name='update-organization-in-user-profile'),
    path('getdevelopers/', get_developers, name='get-developers'),
    path('removeuserfromorg/<int:user_id>/', remove_user_from_organization , name='remove-user-from-organization'),
    path('webhook/', csrf_exempt(stripe_webhook_view),
         name='stripe-webhook'),
   
    path('create-checkout-session/<int:pk>/',
         csrf_exempt(create_checkout_session), name='create-checkout-session'),
     
     path('getgamesbybooth/', get_games_by_booth_and_genre, name='get-gamesby-booth-and-genre'),

     path('authenticate/', authenticate_for_token, name='authenticate_for_token'),

     path('user/<str:username>/', get_user_role_by_username, name='get_user_role'),
     path('user/<str:username>/profile_picture/', get_user_profile_picture, name='get_user_profile_picture'),
     path('createevent/', create_event, name='create_event'),
     path('user/<str:username>/leadevents/', get_lead_events, name='get_lead_events'),
     path('user/<str:username>/devevents/', get_developer_events, name='get_developer_events'),
     path('getevents/', get_all_events, name='get_all_events'),
     path('getevent/<int:event_id>/', get_event_by_id, name='getevent_by_id'),
     path('conversations/', conversations_list, name='api_conversations_list'),
     path('conversations/<uuid:pk>/', conversations_detail, name="api_conversations_detail"),
     path('conversations/start/<int:user_id>/', conversations_start, name="api_conversations_start"),
     path('check-booth-association/<int:organization_id>/', check_booth_association, name='check-booth-association'),
     path('get-booth-organization/<int:booth_id>/', get_booth_organization, name='get_booth_organization'),
     path('games/<int:game_id>/feedbacks/', get_feedbacks, name='get_feedbacks'),
     path('games/<int:game_id>/feedbacks/create/',
         create_feedback, name='create_feedback'),
     path('feedbacks/<int:feedback_id>/update/',
         update_feedback, name='update_feedback'),
     path('feedbacks/<int:feedback_id>/delete/',
         delete_feedback, name='delete_feedback'),
     path('get-game-id/<str:title>/', get_game_id, name='get-game-id'),
     path('editevent/<int:pk>/', event_edit, name='editevent'),

     path('event/', get_event, name='get_event'),

    path('sponsorship/create/', create_sponsorship, name='create_sponsorship'),
    path('sponsorship/', get_sponsorships, name='get_sponsorships'),
    path('eventslanding/', get_events_for_landing, name='get_events_for_landing'),






]
