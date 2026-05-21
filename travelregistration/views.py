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
from django.utils.translation import get_language
from rest_framework import permissions, viewsets

from travelregistration.healthcheck_calculations import _get_load_average, _get_system_memory, \
    _get_process_memory, _get_database_health
from travelregistration.models import Location, Region, LocationEntry, Map
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


def _get_map_context(map_obj, user, request=None, is_shared_map=False):
    all_locations = Location.objects.filter(region__map=map_obj).order_by('display_y')
    locations_entries = LocationEntry.objects.filter(user=user)
    context = {
        "map": map_obj,
        "map_slug": map_obj.slug,
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
    context["visited_count"] = sum(1 for loc in context["locations"] if loc["status"] != "none")
    context["total_count"] = len(context["locations"])
    lang = get_language() or 'en'
    context["map_name_localized"] = map_obj.name if lang.startswith('ja') else map_obj.name_en
    if request and request.user.is_authenticated and request.user == user and not is_shared_map:
        share_token = signing.dumps({"user": user.pk, "map": map_obj.pk}, salt=SHARE_MAP_SALT)
        share_url = request.build_absolute_uri(reverse("shared_map", args=[share_token]))
        theme = request.COOKIES.get('theme', 'light')
        context["share_url"] = f"{share_url}?theme={theme}"
    return context


def maps_list(request):
    all_maps = Map.objects.all()
    if request.user.is_authenticated:
        entries = LocationEntry.objects.filter(user=request.user).select_related('location__region__map')
        entry_counts = {}
        for entry in entries:
            map_pk = entry.location.region.map_id
            entry_counts[map_pk] = entry_counts.get(map_pk, 0) + 1
        location_counts = {}
        for loc in Location.objects.select_related('region__map'):
            if loc.region is None:
                continue
            map_pk = loc.region.map_id
            location_counts[map_pk] = location_counts.get(map_pk, 0) + 1
        maps_with_progress = [
            {
                "map": m,
                "total": location_counts.get(m.pk, 0),
                "visited": entry_counts.get(m.pk, 0),
            }
            for m in all_maps
        ]
    else:
        maps_with_progress = [{"map": m, "total": None, "visited": None} for m in all_maps]
    return render(request, "travelregistration/maps_list.html", {"maps": maps_with_progress})


def map_detail(request, map_slug):
    map_obj = get_object_or_404(Map, slug=map_slug)
    if not request.user.is_authenticated:
        lang = get_language() or 'en'
        return render(request, "travelregistration/map_detail.html", {
            "map": map_obj,
            "map_slug": map_slug,
            "map_name_localized": map_obj.name if lang.startswith('ja') else map_obj.name_en,
        })

    context = _get_map_context(map_obj, request.user, request=request)
    template = loader.get_template("travelregistration/map_detail.html")
    return HttpResponse(template.render(context, request))


_VALID_THEMES = {'light', 'dark', 'parchment', 'sakura', 'hacker', 'neon'}


def shared_map(request, share_token):
    try:
        data = signing.loads(share_token, salt=SHARE_MAP_SALT)
    except signing.BadSignature as exc:
        raise Http404("Shared map not found") from exc

    theme = request.GET.get('theme')
    if theme in _VALID_THEMES:
        response = HttpResponseRedirect(request.path)
        response.set_cookie('theme', theme, max_age=60 * 60 * 24 * 365)
        return response

    owner = get_object_or_404(get_user_model(), pk=data["user"])
    map_obj = get_object_or_404(Map, pk=data["map"])
    return render(request, "travelregistration/map_detail.html", _get_map_context(map_obj, owner, is_shared_map=True))


class LocationEntryForm(ModelForm):
    class Meta:
        model = LocationEntry
        fields = ("status",)
        localized_fields = ('__all__',)


@login_required
def update_location(request, map_slug, location_name):
    map_obj = get_object_or_404(Map, slug=map_slug)
    try:
        existing = LocationEntry.objects.get(
            location__name=location_name,
            location__region__map=map_obj,
            user=request.user,
        )
    except LocationEntry.DoesNotExist:
        existing = LocationEntry(
            location=get_object_or_404(Location, name=location_name, region__map=map_obj),
            user=request.user,
        )

    if request.method == "POST":
        form = LocationEntryForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("map_detail", args=[map_slug]))
    else:
        form = LocationEntryForm(instance=existing)
    return render(request, "update.html", {
        "form": form,
        "location": existing.location,
        "locationentry": existing,
        "map_slug": map_slug,
    })

def update_theme(request):
    theme = request.POST.get('theme', 'light')
    response = HttpResponseRedirect(request.POST.get('next', '/'))
    response.set_cookie('theme', theme, max_age=60*60*24*365)
    return response
