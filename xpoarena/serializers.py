from rest_framework import serializers
from .models import Booth, Game, Theme

class BoothSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booth
        fields = ['id','company', 'name', 'description', 'image', 'created_at']

   
class GamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"
