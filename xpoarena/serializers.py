from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


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



class BoothCustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoothCustomization
        fields = "__all__"

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'profile_picture', 'profile_picture_url']
        read_only_fields = ['user']

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        extra_kwargs = {
            'created_by': {'read_only': True},
        }

class EventSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()     
    class Meta:
        model = Event
        fields = "__all__"

class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['eventName', 'description', 'dateOfEvent', 'startTime', 'endTime', 'image']

    def create(self, validated_data):
        organization_id = self.context['organization_id']
        organization = Organization.objects.get(id=organization_id)
        event = Event.objects.create(organization=organization, **validated_data)
        return event


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username')

class MyUserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested serializer

    class Meta:
        model = UserProfile
        fields = ('user', 'profile_picture', 'profile_picture_url', 'role')