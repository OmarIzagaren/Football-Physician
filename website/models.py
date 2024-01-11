from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    is_business_user= models.BooleanField(blank=True, null=True)
CustomUser._meta.get_field('user_permissions').remote_field.related_name = 'customuser_user_permissions'
CustomUser._meta.get_field('groups').remote_field.related_name = 'customuser_groups'


class Player(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete= models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length = 10)
    date_of_birth = models.DateField(null=True, blank=False)
    height = models.IntegerField()
    weight = models.IntegerField()
    country = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Injury(models.Model):
    player = models.ForeignKey(Player, null=True, on_delete= models.CASCADE)
    injury = models.CharField(max_length=50)
    injury_start_date = models.DateField()
    injury_end_date = models.DateField(null=True, blank=True)
    injury_age = models.IntegerField(blank=True)
    injured = models.BooleanField(default = False)
