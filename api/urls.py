from xpoarena.views import booth, update_booth, games, theme, customizedBooth, update_booth_customization, update_game
from django.urls import path

urlpatterns = [
    path('booth/', booth),
    path('booth/<int:booth_id>', update_booth),
    path('games/<str:title>', update_game),
    path('games/', games),
    path('theme/', theme),
    path('customizedbooth/', customizedBooth),
    path('customizedbooth/<int:pk>/', update_booth_customization)


]