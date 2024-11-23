from django.contrib.gis.db import models


class JerseyBoundary(models.Model):
    gid_0 = models.CharField(max_length=10)
    country = models.CharField(max_length=10)
    geom = models.MultiPolygonField(srid=4326)

    class Meta:
        abstract = True


class Jersey(JerseyBoundary):
    class Meta:
        indexes = [models.Index(fields=["gid_0"])]
        verbose_name = "Jersey"
        verbose_name_plural = "Jersey"
        ordering = ("country",)

    def __str__(self) -> str:
        return self.country
