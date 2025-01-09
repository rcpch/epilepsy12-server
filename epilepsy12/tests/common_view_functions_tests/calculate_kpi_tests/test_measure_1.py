"""
Measure 1 - paediatrician_with_expertise_in_epilepsies

Test Measure 2 - % of children and young people with epilepsy, with input by a ‘consultant paediatrician with expertise in epilepsies’ within 2 weeks of initial referral

Number of children and young people [diagnosed with epilepsy] at first year 
AND (
    who had [input from a paediatrician with expertise in epilepsy] 
    OR 
    a [input from a paediatric neurologist] within 2 weeks of initial referral. (initial referral to mean first paediatric assessment)
    )
"""

# Standard imports
import pytest
from datetime import date
from dateutil.relativedelta import relativedelta

# Third party imports

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.models import (
    Registration,
    KPI,
)
from epilepsy12.constants import KPI_SCORE

REFERRAL_DATE = date(2023, 1, 1)
PASS_INPUT_DATE = REFERRAL_DATE + relativedelta(days=14)
FAIL_INPUT_DATE = REFERRAL_DATE + relativedelta(days=15)


@pytest.mark.parametrize(
    "consultant_paediatrician_referral_made,consultant_paediatrician_referral_date,consultant_paediatrician_input_date,paediatric_neurologist_referral_made,paediatric_neurologist_referral_date,paediatric_neurologist_input_date,expected_score",
    [
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            None,
            None,
            None,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist not involved
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            True,
            None,
            None,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist involved but not referred
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist involved,  referred but not seen
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist seen within 14 days
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist seen after 14 days - Note only one has to be seen within 14 days
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            False,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred but seen and referred within 14 days - Note only one has to be seen within 14 days
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            False,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred but seen after 14 days of referral. Note only one has to be seen within 14 days
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            False,
            None,
            FAIL_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred, no referral date but seen after 14 days of referral - Note only one has to be seen within 14 days
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            False,
            REFERRAL_DATE,
            None,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred but referral date made but not seen
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            None,
            REFERRAL_DATE,
            None,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist referral none with referral date but not seen
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            None,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Paediatrician seen within 14 days, neurologist referral none with no input date but seen
    ],
)
@pytest.mark.django_db
def test_measure_1_should_pass_seen_paediatrician(
    e12_case_factory,
    consultant_paediatrician_referral_made,
    consultant_paediatrician_referral_date,
    consultant_paediatrician_input_date,
    paediatric_neurologist_referral_made,
    paediatric_neurologist_referral_date,
    paediatric_neurologist_input_date,
    expected_score,
):
    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=consultant_paediatrician_referral_made,
        registration__assessment__consultant_paediatrician_referral_date=consultant_paediatrician_referral_date,
        registration__assessment__consultant_paediatrician_input_date=consultant_paediatrician_input_date,
        registration__assessment__paediatric_neurologist_referral_made=paediatric_neurologist_referral_made,
        registration__assessment__paediatric_neurologist_referral_date=paediatric_neurologist_referral_date,
        registration__assessment__paediatric_neurologist_input_date=paediatric_neurologist_input_date,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # ensure we get the updated database object, not the Python object
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).paediatrician_with_expertise_in_epilepsies

    assert (
        kpi_score == expected_score
    ), f"Patient saw a Paediatrician IN {PASS_INPUT_DATE - REFERRAL_DATE} after referral, but did not pass measure. measures - (paediatrician - referral_made: {consultant_paediatrician_referral_made}, referral date: {consultant_paediatrician_referral_date} input_date: {consultant_paediatrician_input_date}, neurologist - referral_made: {paediatric_neurologist_referral_made}, referral_date: {paediatric_neurologist_referral_date} input_date: {paediatric_neurologist_input_date}"


@pytest.mark.parametrize(
    "consultant_paediatrician_referral_made,consultant_paediatrician_referral_date,consultant_paediatrician_input_date,paediatric_neurologist_referral_made,paediatric_neurologist_referral_date,paediatric_neurologist_input_date,expected_score",
    [
        (
            None,
            None,
            None,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician not involved
        (
            True,
            None,
            None,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician involved but not referred
        (
            True,
            REFERRAL_DATE,
            None,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician involved but not referred
        (
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician seen within 14 days - both seen within 14 days so pass
        (
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician seen after 14 days - only one has to be seen within 14 days
        (
            False,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician not declared referred but seen and referred within 14 days: both seen within 14 days so pass
        (
            False,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician not declared referred but seen after 14 days of referral: only one has to be seen within 14 days
        (
            False,
            None,
            FAIL_INPUT_DATE,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician not declared referred, no referral date but seen after 14 days of referral
        (
            False,
            REFERRAL_DATE,
            None,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician not declared referred but referral date made but not seen
        (
            None,
            REFERRAL_DATE,
            None,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician referral none with referral date but not seen
        (
            None,
            None,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),  # Neurologist seen within 14 days, paediatrician referral none with no input date but seen
    ],
)
@pytest.mark.django_db
def test_measure_1_should_pass_seen_neurologist(
    e12_case_factory,
    consultant_paediatrician_referral_made,
    consultant_paediatrician_referral_date,
    consultant_paediatrician_input_date,
    paediatric_neurologist_referral_made,
    paediatric_neurologist_referral_date,
    paediatric_neurologist_input_date,
    expected_score,
):

    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=consultant_paediatrician_referral_made,
        registration__assessment__consultant_paediatrician_referral_date=consultant_paediatrician_referral_date,
        registration__assessment__consultant_paediatrician_input_date=consultant_paediatrician_input_date,
        registration__assessment__paediatric_neurologist_referral_made=paediatric_neurologist_referral_made,
        registration__assessment__paediatric_neurologist_referral_date=paediatric_neurologist_referral_date,
        registration__assessment__paediatric_neurologist_input_date=paediatric_neurologist_input_date,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # ensure we get the updated database object, not the Python object
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).paediatrician_with_expertise_in_epilepsies

    assert (
        kpi_score == expected_score
    ), f"Patient saw a Neurologist in {PASS_INPUT_DATE - REFERRAL_DATE} after referral, but did not pass measure: measures - (paediatrician - referral_made: {consultant_paediatrician_referral_made}, referral date: {consultant_paediatrician_referral_date} input_date: {consultant_paediatrician_input_date}, neurologist - referral_made: {paediatric_neurologist_referral_made}, referral_date: {paediatric_neurologist_referral_date} input_date: {paediatric_neurologist_input_date}"


@pytest.mark.parametrize(
    "consultant_paediatrician_referral_made,consultant_paediatrician_referral_date,consultant_paediatrician_input_date,paediatric_neurologist_referral_made,paediatric_neurologist_referral_date,paediatric_neurologist_input_date,expected_score",
    [
        (
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            None,
            None,
            None,
            KPI_SCORE["FAIL"],
        ),  # Paediatrician seen within 14 days, neurologist not involved
        (
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            True,
            None,
            None,
            KPI_SCORE["FAIL"],
        ),  # Paediatrician seen within 14 days, neurologist involved but not referred
        (
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["FAIL"],
        ),  # Paediatrician seen within 14 days, neurologist involved but not referred
        (
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            KPI_SCORE["FAIL"],
        ),  # Paediatrician not seen within 14 days, neurologist not seen within 14 days# Paediatrician not seen within 14 days, neurologist seen within 14 days
        (
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            False,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            KPI_SCORE["FAIL"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred but seen and referred within 14 days
        (
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            False,
            None,
            FAIL_INPUT_DATE,
            KPI_SCORE["FAIL"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred, no referral date but seen after 14 days of referral
        (
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            False,
            REFERRAL_DATE,
            None,
            KPI_SCORE["FAIL"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred but referral date made but not seen
        (
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            None,
            REFERRAL_DATE,
            None,
            KPI_SCORE["FAIL"],
        ),  # Paediatrician seen within 14 days, neurologist referral none with referral date but not seen
        (
            True,
            REFERRAL_DATE,
            FAIL_INPUT_DATE,
            None,
            None,
            FAIL_INPUT_DATE,
            KPI_SCORE["FAIL"],
        ),  # Paediatrician seen within 14 days, neurologist referral none with no input date but seen
    ],
)
@pytest.mark.django_db
def test_measure_1_should_fail_not_seen_paediatrician_or_neurologist_14_days_after_referral(
    e12_case_factory,
    consultant_paediatrician_referral_made,
    consultant_paediatrician_referral_date,
    consultant_paediatrician_input_date,
    paediatric_neurologist_referral_made,
    paediatric_neurologist_referral_date,
    paediatric_neurologist_input_date,
    expected_score,
):

    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=consultant_paediatrician_referral_made,
        registration__assessment__consultant_paediatrician_referral_date=consultant_paediatrician_referral_date,
        registration__assessment__consultant_paediatrician_input_date=consultant_paediatrician_input_date,
        registration__assessment__paediatric_neurologist_referral_made=paediatric_neurologist_referral_made,
        registration__assessment__paediatric_neurologist_referral_date=paediatric_neurologist_referral_date,
        registration__assessment__paediatric_neurologist_input_date=paediatric_neurologist_input_date,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # ensure we get the updated database object, not the Python object
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).paediatrician_with_expertise_in_epilepsies

    assert (
        kpi_score == expected_score
    ), f"Patient did not see a Paediatrician/Neurologist within 14 days of referral (seen after {FAIL_INPUT_DATE - REFERRAL_DATE}), but did not fail measure: measures - (paediatrician - referral_made: {consultant_paediatrician_referral_made}, referral date: {consultant_paediatrician_referral_date} input_date: {consultant_paediatrician_input_date}, neurologist - referral_made: {paediatric_neurologist_referral_made}, referral_date: {paediatric_neurologist_referral_date} input_date: {paediatric_neurologist_input_date}"


@pytest.mark.django_db
def test_measure_1_should_fail_no_doctor_involved(
    e12_case_factory,
):
    """
    *FAIL*
    1)  consultant_paediatrician_referral_made = False
        paediatric_neurologist_referral_made = False
    """

    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=False,
        registration__assessment__paediatric_neurologist_referral_made=False,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # ensure we get the updated database object, not the Python object
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).paediatrician_with_expertise_in_epilepsies

    assert (
        kpi_score == KPI_SCORE["FAIL"]
    ), f"Patient did not see a Paediatrician/Neurologist, but did not fail measure"


@pytest.mark.parametrize(
    "consultant_paediatrician_referral_made,consultant_paediatrician_referral_date,consultant_paediatrician_input_date,paediatric_neurologist_referral_made,paediatric_neurologist_referral_date,paediatric_neurologist_input_date,expected_score",
    [
        (
            True,
            REFERRAL_DATE,
            None,
            None,
            None,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist not involved
        (
            True,
            REFERRAL_DATE,
            None,
            True,
            None,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist involved but not referred
        (
            True,
            REFERRAL_DATE,
            None,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist involved but not referred
        (
            True,
            REFERRAL_DATE,
            None,
            False,
            None,
            FAIL_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred, no referral date but seen after 14 days of referral
        (
            True,
            REFERRAL_DATE,
            None,
            False,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred but referral date made but not seen
        (
            True,
            REFERRAL_DATE,
            None,
            None,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist referral none with referral date but not seen
        (
            True,
            REFERRAL_DATE,
            None,
            None,
            None,
            FAIL_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist referral none with no input date but seen
        (
            True,
            None,
            PASS_INPUT_DATE,
            None,
            None,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist not involved
        (
            True,
            None,
            PASS_INPUT_DATE,
            True,
            None,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist involved but not referred
        (
            True,
            None,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist involved but not referred
        (
            True,
            None,
            PASS_INPUT_DATE,
            False,
            None,
            FAIL_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred, no referral date but seen after 14 days of referral
        (
            True,
            None,
            PASS_INPUT_DATE,
            False,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist not declared referred but referral date made but not seen
        (
            True,
            None,
            PASS_INPUT_DATE,
            None,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist referral none with referral date but not seen
        (
            True,
            None,
            PASS_INPUT_DATE,
            None,
            None,
            FAIL_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Paediatrician seen within 14 days, neurologist referral none with no input date but seen
        (
            None,
            None,
            None,
            True,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician not involved
        (
            True,
            None,
            None,
            True,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician involved but not referred
        (
            True,
            REFERRAL_DATE,
            None,
            True,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician involved but not referred
        (
            False,
            None,
            FAIL_INPUT_DATE,
            True,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician not declared referred, no referral date but seen after 14 days of referral
        (
            False,
            REFERRAL_DATE,
            None,
            True,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician not declared referred but referral date made but not seen
        (
            None,
            REFERRAL_DATE,
            None,
            True,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician referral none with referral date but not seen
        (
            None,
            None,
            PASS_INPUT_DATE,
            True,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician referral none with no input date but seen
        (
            None,
            None,
            None,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician not involved
        (
            True,
            None,
            None,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician involved but not referred
        (
            True,
            REFERRAL_DATE,
            None,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician involved but not referred
        (
            False,
            None,
            FAIL_INPUT_DATE,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician not declared referred, no referral date but seen after 14 days of referral
        (
            False,
            REFERRAL_DATE,
            None,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician not declared referred but referral date made but not seen
        (
            None,
            REFERRAL_DATE,
            None,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician referral none with referral date but not seen
        (
            None,
            None,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            None,
            KPI_SCORE["NOT_SCORED"],
        ),  # Neurologist seen within 14 days, paediatrician referral none with no input date but seen
    ],
)
@pytest.mark.django_db
def test_measure_1_not_eligible(
    e12_case_factory,
    consultant_paediatrician_referral_made,
    consultant_paediatrician_referral_date,
    consultant_paediatrician_input_date,
    paediatric_neurologist_referral_made,
    paediatric_neurologist_referral_date,
    paediatric_neurologist_input_date,
    expected_score,
):
    """
    *NOT_SCORED*
    1)  consultant_paediatrician_referral_made = False
        paediatric_neurologist_referral_made = False
    """

    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=consultant_paediatrician_referral_made,
        registration__assessment__consultant_paediatrician_referral_date=consultant_paediatrician_referral_date,
        registration__assessment__consultant_paediatrician_input_date=consultant_paediatrician_input_date,
        registration__assessment__paediatric_neurologist_referral_made=paediatric_neurologist_referral_made,
        registration__assessment__paediatric_neurologist_referral_date=paediatric_neurologist_referral_date,
        registration__assessment__paediatric_neurologist_input_date=paediatric_neurologist_input_date,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    # ensure we get the updated database object, not the Python object
    kpi_score = KPI.objects.get(
        pk=registration.kpi.pk
    ).paediatrician_with_expertise_in_epilepsies

    assert (
        kpi_score == expected_score
    ), f"Patient (paediatrician - referral_made: {consultant_paediatrician_referral_made}, referral date: {consultant_paediatrician_referral_date} input_date: {consultant_paediatrician_input_date}, neurologist - referral_made: {paediatric_neurologist_referral_made}, referral_date: {paediatric_neurologist_referral_date} input_date: {paediatric_neurologist_input_date} did not have enough criteria to pass or fail measure , but did not return NOT_SCORED"
