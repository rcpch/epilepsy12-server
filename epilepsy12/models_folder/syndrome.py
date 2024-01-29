# python
from operator import itemgetter

# django
from django.contrib.gis.db import models

# 3rd party
from simple_history.models import HistoricalRecords

# rcpch
from .help_text_mixin import HelpTextMixin
from ..constants import SYNDROMES
from .time_and_user_abstract_base_classes import *


class Syndrome(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class stores information on syndromes
    One MultiaxialDescription can have multiple syndromes
    """

    syndrome_diagnosis_date = models.DateField(
        help_text={
            "label": "The date the syndrome diagnosis was made.",
            "reference": "The date the syndrome diagnosis was made.",
        },
        blank=True,
        default=None,
        null=True,
    )

    syndrome = models.ForeignKey(
        "epilepsy12.SyndromeList",
        help_text={
            "label": "The syndrome name.",
            "reference": "Methodology for classification and definition of epilepsy syndromes with list of syndromes: Report of the ILAE Task Force on Nosology and Definitions, Epilepsia 2017",
        },
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    # relationships

    multiaxial_diagnosis = models.ForeignKey(
        "epilepsy12.MultiaxialDiagnosis",
        on_delete=models.CASCADE,
        related_name="syndromes",
    )

    def __str__(self) -> str:
        return (
            f"{self.syndrome.syndrome_name} on {self.syndrome_diagnosis_date} for {self.multiaxial_diagnosis.registration.case}"
            if self.syndrome
            else f"Empty syndrome"
        )

    class Meta:
        verbose_name = "Syndrome"
        verbose_name_plural = "Syndromes"
        ordering = ["multiaxial_diagnosis__registration__case"]
