from xpoarena.views import booth, update_booth, games, theme, customizedBooth
from django.urls import path

urlpatterns = [
    path('booth/', booth),
    path('booth/<int:booth_id>', update_booth),
    path('games/', games),
    path('theme/', theme),
    path('customizedbooth/', customizedBooth)

]