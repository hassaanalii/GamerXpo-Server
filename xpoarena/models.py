from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
import uuid


def upload_to(instance, filename):
    return 'posts/{filename}'.format(filename=filename)

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class ConversationMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    body = models.TextField() 
    sent_to = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Company(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Booth(models.Model):
    organization = models.OneToOneField('Organization', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    image = models.ImageField(_("Image"), upload_to=upload_to)
    created_at = models.DateTimeField(default=timezone.now)
   
    def __str__(self):
        return self.name
    
class Game(models.Model):
    ACTION = 'Action'
    ADVENTURE = 'Adventure'
    PUZZLE = 'Puzzle'
    SPORTS = 'Sports'
    CASUAL = 'Casual'
    SHOOTING = 'Shooting'
    DRIVING = 'Driving'
    HORROR = 'Horror'

    GENRE_CHOICES = [
        (ACTION, 'Action'),
        (ADVENTURE, 'Adventure'),
        (PUZZLE, 'Puzzle'),
        (SPORTS, 'Sports'),
        (CASUAL, 'Causal'),
        (SHOOTING, 'Shooting'),
        (DRIVING, 'Driving'),
        (HORROR, 'Horror'),
    ]

    TECHNOLOGY_CHOICES = [
        ('HTML5', 'HTML5'),
        ('Unity', 'Unity'),
        ('Unreal Engine', 'Unreal Engine'),
        ('Cocos2d', 'Cocos2d'),
        ('Godot', 'Godot'),
    
    ]
    id = models.AutoField(primary_key=True)
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, related_name='games')
    title = models.CharField(max_length=255, unique=True)
    release_date = models.DateField()
    game_iframe_src = models.URLField(max_length=1000)
    genre = models.CharField(max_length=255, choices=GENRE_CHOICES, default='Adventure')
    game_description = models.TextField()
    image_url = models.URLField(max_length=1000)
    last_updated = models.DateField(auto_now=True)
    technology = models.CharField(max_length=50, choices=TECHNOLOGY_CHOICES, default='HTML5')
    system_requirements = models.TextField(null=True, blank=True)
    game_trailer = models.FileField(upload_to=upload_to, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    game_download_link = models.URLField(max_length=1000)
    image = models.ImageField(_("Image"), upload_to=upload_to, null=True, blank=True)




    def __str__(self):
        return self.title


class GameScreenshot(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='screenshots')
    screenshot = models.ImageField(_("Screenshot"), upload_to=upload_to, null=True, blank=True)

    def __str__(self):
        return f"{self.game.title} - Screenshot"
    
class Theme(models.Model):
    name = models.CharField(max_length=255, unique=True)
    theme_video = models.FileField(upload_to=upload_to, null=True, blank=True)
    font_name = models.CharField(max_length=255)
    font_color = models.CharField(max_length=10) 

    def __str__(self):
        return self.name

class BoothCustomization(models.Model):
    booth = models.OneToOneField(Booth, on_delete=models.CASCADE, related_name='customization')
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, blank=True, related_name='booths')
    background_color = models.CharField(max_length=7) 
    font_color = models.CharField(max_length=7)  

    def __str__(self):
        return f"Customizations for {self.booth.name}"
    

    
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    website_url = models.URLField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to=upload_to, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    founded_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    secret_key = models.CharField(max_length=100, unique=True)
    created_by = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Event(models.Model):
    eventName = models.CharField(max_length=255)
    description = models.TextField()
    dateOfEvent = models.DateField()
    startTime = models.TimeField()
    endTime = models.TimeField()
    image = models.ImageField(upload_to=upload_to)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    room_id = models.CharField(max_length=100, unique=True)

    gold_sponsor = models.BooleanField(default=False)
    silver_sponsor = models.BooleanField(default=False)
    bronze_sponsor = models.BooleanField(default=False)


    def __str__(self):
        return self.eventName
    


class Sponsorship(models.Model):
    SPONSORSHIP_CHOICES = [
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Bronze', 'Bronze')
    ]

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='sponsorships')
    package = models.CharField(max_length=10, choices=SPONSORSHIP_CHOICES)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.TextField()
    logo = models.ImageField(upload_to=upload_to)

    def _str_(self):
        return f"{self.package} Sponsorship for {self.event.eventName} by {self.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to=upload_to, blank=True, null=True)
    profile_picture_url = models.CharField(max_length=255, blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')


    def __str__(self):
        return f"{self.user.username}'s profile"




class PaymentHistory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    game = models.ForeignKey(
        Game, on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField()

    def __str__(self):
        return self.game.name


class GameFeedback(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    submitted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Feedback for {self.game.title} by {self.submitted_by.username if self.submitted_by else 'Anonymous'}"