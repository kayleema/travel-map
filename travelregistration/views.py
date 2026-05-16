import os
import platform
import socket
import time

import django
import django.forms.widgets
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.forms import ModelForm
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from rest_framework import permissions, viewsets

from travelregistration.healthcheck_calculations import _get_load_average, _get_system_memory, \
    _get_process_memory, _get_database_health
from travelregistration.models import Location, Region, LocationEntry
from travelregistration.serializers import LocationSerializer, RegionSerializer, LocationEntrySerializer

SHARE_MAP_SALT = "travelregistration.share_map"
PROCESS_START_TIME = time.time()


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


def health(request):
    now = timezone.now()
    database_health = _get_database_health()
    http_status = 200 if database_health["ok"] else 503
    return JsonResponse({
        "status": "ok" if database_health["ok"] else "degraded",
        "checked_at": now.isoformat(),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "load_average": _get_load_average(),
        "memory": {
            "system": _get_system_memory(),
            "process": _get_process_memory(),
        },
        "process": {
            "pid": os.getpid(),
            "uptime_seconds": round(time.time() - PROCESS_START_TIME, 2),
        },
        "database": database_health,
    }, status=http_status)


def _get_map_context(user, request=None, is_shared_map=False):
    all_locations = Location.objects.all().order_by('display_y')
    locations_entries = LocationEntry.objects.filter(user=user)
    context = {
        "locations": [{
            "location": location,
            "status": next(
                (location_entry.status for location_entry in locations_entries if
                 location_entry.location.id == location.id),
                "none")
        } for location in all_locations],
        "max_x": max(location.display_x for location in all_locations),
        "max_y": max(location.display_y for location in all_locations),
        "share_owner": user,
        "shared_map": is_shared_map,
    }
    if request and request.user.is_authenticated and request.user == user and not is_shared_map:
        share_token = signing.dumps(user.pk, salt=SHARE_MAP_SALT)
        context["share_url"] = request.build_absolute_uri(reverse("shared_map", args=[share_token]))
    return context


def homepage(request):
    if not request.user.is_authenticated:
        return render(request, "travelregistration/homepage.html")

    context = _get_map_context(request.user, request=request)

    template = loader.get_template("travelregistration/homepage.html")
    return HttpResponse(template.render(context, request))


def shared_map(request, share_token):
    try:
        user_id = signing.loads(share_token, salt=SHARE_MAP_SALT)
    except signing.BadSignature as exc:
        raise Http404("Shared map not found") from exc

    owner = get_object_or_404(get_user_model(), pk=user_id)
    return render(request, "travelregistration/homepage.html", _get_map_context(owner, is_shared_map=True))


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

def update_theme(request):
    theme = request.POST.get('theme', 'light')
    response = HttpResponseRedirect(request.POST.get('next', '/'))
    response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response
