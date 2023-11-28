from rest_framework import serializers
from .models import Booth

class BoothSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booth
        fields = ['id','company', 'name', 'description', 'image', 'created_at']

   
