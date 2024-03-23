from xpoarena.views import booth, update_booth, games, theme, customizedBooth, user_details, update_booth_customization, update_game, login_view, signup, google_login, update_user_and_profile, register_organization, verify_auth 
from django.urls import path

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
    path('verify/', verify_auth, name='verify')

]