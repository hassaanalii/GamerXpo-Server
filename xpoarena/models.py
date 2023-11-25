from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

def upload_to(instance, filename):
    return 'posts/{filename}'.format(filename=filename)

class Company(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Booth(models.Model):
    company = models.OneToOneField('Company', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    image = models.ImageField(_("Image"), upload_to=upload_to)
    created_at = models.DateTimeField(default=timezone.now)
   
    def __str__(self):
        return self.name
