from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Region(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    display_x = models.IntegerField()
    display_y = models.IntegerField()
    display_width = models.IntegerField()
    display_height = models.IntegerField()
    border_radius_top_left = models.BooleanField(default=False)
    border_radius_top_right = models.BooleanField(default=False)
    border_radius_bottom_right = models.BooleanField(default=False)
    border_radius_bottom_left = models.BooleanField(default=False)

    def get_display_x_end(self):
        return self.display_x + self.display_width

    def get_display_y_end(self):
        return self.display_y + self.display_height

    def __str__(self):
        return self.name


class LocationEntry(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=64,
        choices=(
            ("none", _("None")),
            ("lived", _("Lived")),
            ("stayed", _("Stayed")),
            ("walked", _("Walked")),
            ("passed through", _("Passed Through")),
        )
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['location', 'user'],
                                    name='location_and_user_uniq')
        ]

    def __str__(self):
        return self.location.name + " : " + self.get_status_display()
