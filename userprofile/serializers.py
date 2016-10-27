from rest_framework import serializers
from userprofile.models import UserProfile, BankCard, Vehicle, Comments

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar','id_card_number','nick_name','account_balance']
    # TODO refactor needed
    #kind = models.CharField(default='customer#base_info')
    #img = serializers.URLField()
    #id_card_number = serializers.CharField(max_length=20)
    #nick_name = serializers.CharField(max_length=100)
    #account_balance = serializers.FloatField(default=0)

class BankCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = ['number', 'binded']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['plate_number']

class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments

