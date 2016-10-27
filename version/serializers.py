from rest_framework import serializers
from version.models import AndroidAppVersion, AppPages

class AndroidAppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AndroidAppVersion

