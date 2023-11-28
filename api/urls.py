from xpoarena.views import booth, update_booth
from django.urls import path

urlpatterns = [
    path('booth/', booth),
    path('booth/<int:booth_id>', update_booth),
]