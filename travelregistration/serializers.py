from django.contrib.auth.models import Group, User
from rest_framework import serializers

from travelregistration.models import Location, Region, LocationEntry


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class LocationEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationEntry
        fields = '__all__'
