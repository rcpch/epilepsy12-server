"""
Measure 2 `epilepsy_specialist_nurse`
# - [x] Measure 2 passed (registration.kpi.epilepsy_specialist_nurse = 1) registration_instance.assessment.epilepsy_specialist_nurse_input_date <= first_paediatric_assessment_date + 1 year
# - [x] Measure 2 failed (registration.assessment.paediatrician_with_expertise_in_epilepsies = 0) if referral_made is False or input_date > first_paediatric_assessment_date + 1 year
# - [x] Measure 2 not_scored if incomplete (assessment.epilepsy_specialist_nurse_referral_made or assessment.epilepsy_specialist_nurse_input_date is None) NOTE: currently form cannot complete if both date fields are filled

- [x] epilepsy_specialist_nurse_referral_made - True -> epilepsy_specialist_nurse_referral_date - PROVIDED -> epilepsy_specialist_nurse_input_achieved - TRUE -> epilepsy_specialist_nurse_input_date - NOT WITHIN FIRST YEAR OF CARE -> FAIL
- [x] epilepsy_specialist_nurse_referral_made - True -> epilepsy_specialist_nurse_referral_date - PROVIDED -> (epilepsy_specialist_nurse_input_achieved - None) -> epilepsy_specialist_nurse_input_date - NOT WITHIN FIRST YEAR OF CARE -> FAIL (incomplete form but some users may have this as new field introduced late)
- [x] epilepsy_specialist_nurse_referral_made - False -> FAIL

- [x] epilepsy_specialist_nurse_referral_made - True -> epilepsy_specialist_nurse_referral_date - PROVIDED -> epilepsy_specialist_nurse_input_achieved - True -> epilepsy_specialist_nurse_input_date - WITHIN FIRST YEAR OF CARE -> PASS
- [x] epilepsy_specialist_nurse_referral_made - True -> epilepsy_specialist_nurse_referral_date - PROVIDED -> (epilepsy_specialist_nurse_input_achieved - None) -> epilepsy_specialist_nurse_input_date - WITHIN FIRST YEAR OF CARE -> PASS (incomplete form but some users may have this as new field introduced late)
- [x] epilepsy_specialist_nurse_referral_made - True -> epilepsy_specialist_nurse_referral_date - PROVIDED -> epilepsy_specialist_nurse_input_achieved - FALSE  (epilepsy_specialist_nurse_input_date NONE)-> PASS

- [x] epilepsy_specialist_nurse_referral_made - None -> NOT_SCORED
- [x] epilepsy_specialist_nurse_referral_made - True -> epilepsy_specialist_nurse_referral_date - None -> NOT_SCORED
- [x] epilepsy_specialist_nurse_referral_made - True -> epilepsy_specialist_nurse_referral_date - PROVIDED -> epilepsy_specialist_nurse_input_achieved - None -> epilepsy_specialist_nurse_input_date - None -> NOT_SCORED
- [x] epilepsy_specialist_nurse_referral_made - True -> epilepsy_specialist_nurse_referral_date - PROVIDED -> epilepsy_specialist_nurse_input_achieved - TRUE -> epilepsy_specialist_nurse_input_date - None -> NOT_SCORED

Test Measure 2 - % of children and young people with epilepsy, with input by epilepsy specialist nurse within the first year of care

Number of children and young people [diagnosed with epilepsy]
AND
who had input by an Epilepsy Specialist Nurse by first year (first_paediatric_assessment_date + 1 year)
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


@pytest.mark.parametrize(
    "epilepsy_specialist_nurse_referral_made,epilepsy_specialist_nurse_referral_date,epilepsy_specialist_nurse_input_achieved,epilepsy_specialist_nurse_input_date,expected_score",
    [
        (None, None, None, None, KPI_SCORE["NOT_SCORED"]),
        (True, None, None, None, KPI_SCORE["NOT_SCORED"]),
        (True, date(2023, 1, 1), None, None, KPI_SCORE["NOT_SCORED"]),
        (True, date(2023, 1, 1), True, None, KPI_SCORE["NOT_SCORED"]),
    ],
)
@pytest.mark.django_db
def test_measure_2_should_not_score(
    e12_case_factory,
    epilepsy_specialist_nurse_referral_made,
    epilepsy_specialist_nurse_referral_date,
    epilepsy_specialist_nurse_input_achieved,
    epilepsy_specialist_nurse_input_date,
    expected_score,
):
    """
    *NOT_SCORED*
    1)  ANY epilepsy_nurse field is none
    """
    case = e12_case_factory(
        registration__assessment__epilepsy_specialist_nurse_referral_made=epilepsy_specialist_nurse_referral_made,
        registration__assessment__epilepsy_specialist_nurse_referral_date=epilepsy_specialist_nurse_referral_date,
        registration__assessment__epilepsy_specialist_nurse_input_achieved=epilepsy_specialist_nurse_input_achieved,
        registration__assessment__epilepsy_specialist_nurse_input_date=epilepsy_specialist_nurse_input_date,
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).epilepsy_specialist_nurse

    assertion_message = "Following attributes are None but not scoring kpi as None:\n"
    if registration.assessment.epilepsy_specialist_nurse_referral_made is None:
        assertion_message += f"epilepsy_specialist_nurse_referral_made\n"
    if registration.assessment.epilepsy_specialist_nurse_referral_date is None:
        assertion_message += f"epilepsy_specialist_nurse_referral_date\n"
    if registration.assessment.epilepsy_specialist_nurse_input_achieved is None:
        assertion_message += f"epilepsy_specialist_nurse_input_achieved\n"
    if registration.assessment.epilepsy_specialist_nurse_input_date is None:
        assertion_message += f"epilepsy_specialist_nurse_input_date\n"

    assert kpi_score == expected_score, assertion_message


@pytest.mark.django_db
def test_measure_2_should_fail_no_referral(
    e12_case_factory,
):
    """
    *FAIL*
    1)  kpi.epilepsy_specialist_nurse_referral_made = False
    """
    case = e12_case_factory(
        registration__assessment__epilepsy_specialist_nurse_referral_made=False
    )

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    calculate_kpis(registration_instance=registration)

    kpi_score = KPI.objects.get(pk=registration.kpi.pk).epilepsy_specialist_nurse

    assert (
        kpi_score == KPI_SCORE["FAIL"]
    ), f"{registration.assessment.epilepsy_specialist_nurse_referral_made = } but measure is not failing"


@pytest.mark.django_db
def test_measure_2_should_fail_referral_after_1_yr(
    e12_case_factory,
):
    """
    *FAIL*
    1)  input_date > first_paediatric_assessment_date + 1 year
    """
    FIRST_PAEDIATRIC_ASSESSMENT_DATE = date(2023, 1, 1)
    REFERRAL_DATE = FIRST_PAEDIATRIC_ASSESSMENT_DATE
    INPUT_DATE = FIRST_PAEDIATRIC_ASSESSMENT_DATE + relativedelta(years=1, days=1)

    case_achieved_scored = e12_case_factory(
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__epilepsy_specialist_nurse_referral_made=True,
        registration__assessment__epilepsy_specialist_nurse_referral_date=REFERRAL_DATE,
        registration__assessment__epilepsy_specialist_nurse_input_achieved=True,
        registration__assessment__epilepsy_specialist_nurse_input_date=INPUT_DATE,
    )

    case_achieved_unscored = e12_case_factory(
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__epilepsy_specialist_nurse_referral_made=True,
        registration__assessment__epilepsy_specialist_nurse_referral_date=REFERRAL_DATE,
        registration__assessment__epilepsy_specialist_nurse_input_achieved=None,
        registration__assessment__epilepsy_specialist_nurse_input_date=INPUT_DATE,
    )

    # get registration for the saved case model
    registration_achieved_scored = Registration.objects.get(case=case_achieved_scored)
    registration_achieved_unscored = Registration.objects.get(
        case=case_achieved_unscored
    )

    calculate_kpis(registration_instance=registration_achieved_scored)
    calculate_kpis(registration_instance=registration_achieved_unscored)

    achieved_scored_kpi_score = KPI.objects.get(
        pk=registration_achieved_scored.kpi.pk
    ).epilepsy_specialist_nurse
    achieved_unscored_kpi_score = KPI.objects.get(
        pk=registration_achieved_unscored.kpi.pk
    ).epilepsy_specialist_nurse

    assert (
        achieved_scored_kpi_score == KPI_SCORE["FAIL"]
    ), f"ESN Referral made 1y1day after first_paediatric_assessment_date but measure is not failing (achieved field scored)"

    assert (
        achieved_unscored_kpi_score == KPI_SCORE["FAIL"]
    ), f"ESN Referral made 1y1day after first_paediatric_assessment_date but measure is not failing (achieved field unscored)"


@pytest.mark.django_db
def test_measure_2_should_pass_timely_input(
    e12_case_factory,
):
    """
    *PASS*
    1)  kpi.epilepsy_specialist_nurse_referral_made = True
        AND
        kpi.epilepsy_specialist_nurse_input_date <= registration.first_paediatric_assessment_date + 1 year
    """
    FIRST_PAEDIATRIC_ASSESSMENT_DATE = date(2023, 1, 1)
    PASSING_REFERRAL_DATE = FIRST_PAEDIATRIC_ASSESSMENT_DATE
    PASSING_INPUT_DATE = FIRST_PAEDIATRIC_ASSESSMENT_DATE + relativedelta(years=1)

    case_achieved_scored = e12_case_factory(
        registration__assessment__epilepsy_specialist_nurse_referral_made=True,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__epilepsy_specialist_nurse_referral_date=PASSING_REFERRAL_DATE,
        registration__assessment__epilepsy_specialist_nurse_input_achieved=True,
        registration__assessment__epilepsy_specialist_nurse_input_date=PASSING_INPUT_DATE,
    )

    case_achieved_unscored = e12_case_factory(
        registration__assessment__epilepsy_specialist_nurse_referral_made=True,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__epilepsy_specialist_nurse_referral_date=PASSING_REFERRAL_DATE,
        registration__assessment__epilepsy_specialist_nurse_input_achieved=None,
        registration__assessment__epilepsy_specialist_nurse_input_date=PASSING_INPUT_DATE,
    )

    case_achieved_false = e12_case_factory(
        registration__assessment__epilepsy_specialist_nurse_referral_made=True,
        registration__first_paediatric_assessment_date=FIRST_PAEDIATRIC_ASSESSMENT_DATE,
        registration__assessment__epilepsy_specialist_nurse_referral_date=PASSING_REFERRAL_DATE,
        registration__assessment__epilepsy_specialist_nurse_input_achieved=False,
        registration__assessment__epilepsy_specialist_nurse_input_date=None,
    )

    # get registration for the saved case model
    registration_achieved_scored = Registration.objects.get(case=case_achieved_scored)
    registration_achieved_unscored = Registration.objects.get(
        case=case_achieved_unscored
    )
    registration_achieved_false = Registration.objects.get(case=case_achieved_false)

    calculate_kpis(registration_instance=registration_achieved_scored)
    calculate_kpis(registration_instance=registration_achieved_unscored)
    calculate_kpis(registration_instance=registration_achieved_false)

    kpi_score_achieved_scored = KPI.objects.get(
        pk=registration_achieved_scored.kpi.pk
    ).epilepsy_specialist_nurse
    kpi_score_achieved_unscored = KPI.objects.get(
        pk=registration_achieved_unscored.kpi.pk
    ).epilepsy_specialist_nurse
    kpi_score_achieved_false = KPI.objects.get(
        pk=registration_achieved_false.kpi.pk
    ).epilepsy_specialist_nurse

    assert (
        kpi_score_achieved_scored == KPI_SCORE["PASS"]
    ), f"Seen by epilepsy nurse within {PASSING_INPUT_DATE - FIRST_PAEDIATRIC_ASSESSMENT_DATE} but measure is not passing (kpi_score_achieved_scored)"
    assert (
        kpi_score_achieved_unscored == KPI_SCORE["PASS"]
    ), f"Seen by epilepsy nurse within {PASSING_INPUT_DATE - FIRST_PAEDIATRIC_ASSESSMENT_DATE} but measure is not passing (kpi_score_achieved_unscored)"
    assert (
        kpi_score_achieved_false == KPI_SCORE["PASS"]
    ), f"Referred to epilepsy nurse on {PASSING_REFERRAL_DATE} and no second date but should pass as clinician declared seen date not achieved within the year. This should pass but measure is not passing"
