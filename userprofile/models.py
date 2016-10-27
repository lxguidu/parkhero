from django.db import models
from django.contrib.auth.models import User

from parking.models import ParkingLot

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User)

    avatar = models.CharField(max_length=100)
    id_card_number = models.CharField(max_length=20)
    nick_name = models.CharField(max_length=100)
    account_balance = models.IntegerField(default=0)
    payment_password = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username

class BankCard(models.Model):
    owner = models.ForeignKey(User)
    number = models.CharField(max_length = 20)
    binded = models.BooleanField(default=False)

    def __str__(self):
        return self.number

class Vehicle(models.Model):
    owner = models.ManyToManyField(User)
    plate_number = models.CharField(max_length=15)

    def __str__(self):
        return self.plate_number
class Comments(models.Model):
    owner = models.ForeignKey(User)
    comments = models.CharField(max_length=1000)
    created_time = models.DateTimeField(auto_now=True)

