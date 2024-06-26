from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class BoothSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()
    games_count = serializers.SerializerMethodField()

    class Meta:
        model = Booth
        fields = ['id', 'name', 'description', 'image', 'created_at', 'organization', 'organization_name', 'games_count']

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    def get_games_count(self, obj):
        # Count the number of games associated with the booth
        return obj.games.count()

   
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



class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['eventName', 'description', 'dateOfEvent', 'startTime', 'endTime', 'image', 'room_id']

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


class ConversationListSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ('id', 'users', 'modified_at')

class ConversationDetailSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ('id', 'users', 'modified_at',)


class ConversationMessageSerializer(serializers.ModelSerializer):
    sent_to = UserSerializer(many=False, read_only=True)
    created_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = ConversationMessage
        fields = ('id', 'body', 'sent_to', 'created_by',)

class GameFeedbackSerializer(serializers.ModelSerializer):
    submitted_by_username = serializers.SerializerMethodField()

    class Meta:
        model = GameFeedback
        fields = ['id', 'game', 'feedback_text', 'created_at', 'submitted_by', 'submitted_by_username']
        read_only_fields = ['created_at']

    def get_submitted_by_username(self, obj):
        return obj.submitted_by.username if obj.submitted_by else 'Anonymous'
    



class SponsorshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsorship
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()     
    sponsorships = SponsorshipSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = "__all__"