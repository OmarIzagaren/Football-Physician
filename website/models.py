from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.ForeignKey(User, null=True, on_delete= models.CASCADE)
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
