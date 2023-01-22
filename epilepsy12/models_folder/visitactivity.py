# django
from django.db import models
from django.utils import timezone


class VisitActivity(models.Model):
    SUCCESSFUL_LOGIN = 1
    UNSUCCESSFUL_LOGIN = 2
    LOGOUT = 3

    ACTIVITY = (
        (SUCCESSFUL_LOGIN, 'SUCCESSFUL_LOGIN'),
        (UNSUCCESSFUL_LOGIN, 'UNSUCCESSFUL_LOGIN'),
        (LOGOUT, 'LOGOUT')
    )

    activity_datetime = models.DateTimeField(
        auto_created=True,
        default=timezone.now()
    )

    activity = models.PositiveSmallIntegerField(
        choices=ACTIVITY,
        default=1
    )

    ip_address = models.CharField(
        max_length=250,
        blank=True,
        null=True
    )

    epilepsy12user = models.ForeignKey(
        "epilepsy12.Epilepsy12User",
        on_delete=models.CASCADE
    )
