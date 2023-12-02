from xpoarena.views import booth, update_booth, games
from django.urls import path

urlpatterns = [
    path('booth/', booth),
    path('booth/<int:booth_id>', update_booth),
    path('games/', games)
]