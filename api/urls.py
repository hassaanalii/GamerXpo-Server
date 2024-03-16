from xpoarena.views import booth, update_booth, games, theme, customizedBooth, update_booth_customization, update_game, login_view, signup, google_login
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
]