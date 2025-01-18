# python imports

# django imports
from django.contrib.gis.db.models import Q
from django.apps import apps

# E12 imports
# from epilepsy12.models import Syndrome
from epilepsy12.constants import (
    KPI_SCORE,
    EPILEPSY_SEIZURE_TYPE,
    EPILEPSY_DIAGNOSIS_STATUS,
)


def score_kpi_5(registration_instance, age_at_first_paediatric_assessment) -> int:
    """
    5. MRI

    Title: MRI within 6 weeks

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND who are NOT (JME OR JAE OR CAE OR Generalised tonic clonic seizures only OR self-limited epilepsy with centrotemporal spikes ~(SELECT)) AND who had an MRI within 6 weeks of referral.

    Denominator = Number of children and young people diagnosed with epilepsy at first year AND who are NOT (JME OR JAE OR CAE OR Generalised tonic clonic seizures only OR self-limited epilepsy with centrotemporal spikes ~(SELECT))
    """
    multiaxial_diagnosis = registration_instance.multiaxialdiagnosis
    investigations = registration_instance.investigations

    Syndrome = apps.get_model("epilepsy12", "Syndrome")

    # define eligibility criteria 1
    ineligible_syndrome_present = Syndrome.objects.filter(
        Q(multiaxial_diagnosis=multiaxial_diagnosis)
        &
        # ELECTROCLINICAL SYNDROMES: BECTS/JME/JAE/CAE currently not included
        Q(
            syndrome__syndrome_name__in=[
                "Self-limited epilepsy with centrotemporal spikes",  # 3
                "Juvenile myoclonic epilepsy",  # 18
                "Juvenile absence epilepsy",  # 17
                "Childhood absence epilepsy",  # 16
                "Epilepsy with generalized tonic–clonic seizures alone",  # 19
            ]
        )
    ).exists()

    # check eligibility criteria 1 & 2
    # 1 = none of the specified syndromes present
    if not (ineligible_syndrome_present):
        # not scored
        mri_dates_are_none = [
            (investigations.mri_brain_requested_date is None),
            (investigations.mri_brain_reported_date is None),
        ]

        if investigations.mri_indicated is not None:
            if any(mri_dates_are_none) and investigations.mri_indicated is True:
                return KPI_SCORE["FAIL"]
            elif investigations.mri_indicated is False:
                return KPI_SCORE["FAIL"]

        # eligible for this measure - score kpi
        if (
            investigations.mri_brain_requested_date is not None
            and investigations.mri_brain_reported_date is not None
        ):
            passing_criteria_met = (  # MRI performed within 6 weeks
                abs(
                    (
                        investigations.mri_brain_requested_date
                        - investigations.mri_brain_reported_date
                    ).days
                )
                <= 42
            )
        else:
            passing_criteria_met = 0

        if passing_criteria_met:
            return KPI_SCORE["PASS"]
        else:
            return KPI_SCORE["FAIL"]

    # ineligible
    else:
        return KPI_SCORE["INELIGIBLE"]
