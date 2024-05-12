import django.forms.widgets
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, ModelForm, TextInput
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from rest_framework import permissions, viewsets

from travelregistration.models import Location, Region, LocationEntry
from travelregistration.serializers import LocationSerializer, RegionSerializer, LocationEntrySerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]


class LocationEntryViewSet(viewsets.ModelViewSet):
    queryset = LocationEntry.objects.all()
    serializer_class = LocationEntrySerializer
    permission_classes = [permissions.IsAuthenticated]


@login_required
def homepage(request):
    all_locations = Location.objects.all().order_by('display_y')
    locations_entries = LocationEntry.objects.filter(user=request.user)
    context = {
        "locations": [{
            "location": location,
            "status": next(
                (location_entry.status for location_entry in locations_entries if location_entry.location.id == location.id),
                "none")
        } for location in all_locations],
        "max_x": max(location.display_x for location in all_locations),
        "max_y": max(location.display_y for location in all_locations)
    }

    template = loader.get_template("travelregistration/homepage.html")
    return HttpResponse(template.render(context, request))


class LocationEntryForm(ModelForm):
    class Meta:
        model = LocationEntry
        fields = ("status",)
        localized_fields = ('__all__',)


@login_required
def update_location(request, location_name):
    try:
        existing = LocationEntry.objects.get(location__name=location_name, user=request.user)
    except LocationEntry.DoesNotExist:
        existing = LocationEntry(location=Location.objects.get(name=location_name), user=request.user)

    if request.method == "POST":
        form = LocationEntryForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            form.save()
            return django.http.HttpResponseRedirect(reverse("homepage"))
    else:
        form = LocationEntryForm(instance=existing)
    return render(request, "update.html", {
        "form": form,
        "location": existing.location,
        "locationentry": existing,
    })
