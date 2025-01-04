# django
from django.contrib.gis.db import models

# 3rd party
from simple_history.models import HistoricalRecords

# RCPCH
from .help_text_mixin import HelpTextMixin
from .time_and_user_abstract_base_classes import *


class Comorbidity(
    TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin
):
    """
    This class records information on all mental health, behavioural and developmental comorbidities
    [This class replaces the MentalHealth and Neurodevelopmental tables, conflating options into one list]

    Detail
    The date of onset/diagnosis field has been actively removed as not found helpful
    """

    comorbidity_diagnosis_date = models.DateField(
        help_text={
            "label": "What is the date of diagnosis?",
            "reference": "What is the date of diagnosis?",
        },
        max_length=50,
        default=None,
        null=True,
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
        null=False,
        blank=False,
        related_name="comorbidities",
    )

    comorbidityentity = models.ForeignKey(
        to="epilepsy12.ComorbidityList",
        on_delete=models.PROTECT,
        help_text={
            "label": "What is the comorbidity?",
            "reference": "Paediatric neurodisability outpatient diagnosis simple reference set (999001751000000105), SNOMED-CT",
        },
        default=None,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Comorbidity"
        verbose_name_plural = "Comorbidities"
        ordering = ["multiaxial_diagnosis__registration__case", "comorbidityentity"]

    def __str__(self) -> str:
        return f"{self.comorbidityentity.preferredTerm} - {self.multiaxial_diagnosis.registration.case}"
