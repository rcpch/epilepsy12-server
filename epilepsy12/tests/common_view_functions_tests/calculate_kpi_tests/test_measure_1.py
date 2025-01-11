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
    "consultant_paediatrician_referral_made,consultant_paediatrician_referral_date, consultant_paediatrician_input_achieved, consultant_paediatrician_input_date,paediatric_neurologist_referral_made,paediatric_neurologist_referral_date,paediatric_neurologist_input_achieved,paediatric_neurologist_input_date,expected_score",
    [
        (
            True,
            REFERRAL_DATE,
            True,
            PASS_INPUT_DATE,
            False,
            None,
            None,
            None,
            KPI_SCORE["PASS"],
        ),
        (
            True,
            REFERRAL_DATE,
            None,
            PASS_INPUT_DATE,
            False,
            None,
            None,
            None,
            KPI_SCORE["PASS"],
        ),
        (
            True,
            REFERRAL_DATE,
            True,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            True,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),
        (
            True,
            REFERRAL_DATE,
            True,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),
        (
            True,
            REFERRAL_DATE,
            True,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            True,
            FAIL_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),
        (
            True,
            REFERRAL_DATE,
            None,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            True,
            FAIL_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),
        (
            True,
            REFERRAL_DATE,
            True,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            None,
            FAIL_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),
        (
            True,
            REFERRAL_DATE,
            None,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            None,
            FAIL_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),
        (
            True,
            REFERRAL_DATE,
            True,
            PASS_INPUT_DATE,
            True,
            REFERRAL_DATE,
            True,
            None,
            KPI_SCORE["PASS"],
        ),
        (
            False,
            None,
            None,
            None,
            True,
            REFERRAL_DATE,
            True,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),
        (
            False,
            None,
            None,
            None,
            True,
            REFERRAL_DATE,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),
        (
            True,
            REFERRAL_DATE,
            None,
            None,
            True,
            REFERRAL_DATE,
            True,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),
        (
            True,
            REFERRAL_DATE,
            None,
            None,
            True,
            REFERRAL_DATE,
            None,
            PASS_INPUT_DATE,
            KPI_SCORE["PASS"],
        ),
    ],
)
@pytest.mark.django_db
def test_measure_1_should_pass_seen_paediatrician(
    e12_case_factory,
    consultant_paediatrician_referral_made,
    consultant_paediatrician_referral_date,
    consultant_paediatrician_input_achieved,
    consultant_paediatrician_input_date,
    paediatric_neurologist_referral_made,
    paediatric_neurologist_referral_date,
    paediatric_neurologist_input_achieved,
    paediatric_neurologist_input_date,
    expected_score,
):
    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=consultant_paediatrician_referral_made,
        registration__assessment__consultant_paediatrician_referral_date=consultant_paediatrician_referral_date,
        registration__assessment__consultant_paediatrician_input_achieved=consultant_paediatrician_input_achieved,
        registration__assessment__consultant_paediatrician_input_date=consultant_paediatrician_input_date,
        registration__assessment__paediatric_neurologist_referral_made=paediatric_neurologist_referral_made,
        registration__assessment__paediatric_neurologist_referral_date=paediatric_neurologist_referral_date,
        registration__assessment__paediatric_neurologist_input_achieved=paediatric_neurologist_input_achieved,
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
    ), f"Patient saw a Paediatrician IN {PASS_INPUT_DATE - REFERRAL_DATE} after referral, but did not pass measure.\nScores\npaediatrician\n- referral_made: {consultant_paediatrician_referral_made}\n- referral date: {consultant_paediatrician_referral_date}\n- achieved: {consultant_paediatrician_input_achieved}\n- input_date: {consultant_paediatrician_input_date},\n neurologist\n- referral_made: {paediatric_neurologist_referral_made}\n- referral_date: {paediatric_neurologist_referral_date}\n- achieved: {paediatric_neurologist_input_achieved}\n- input_date: {paediatric_neurologist_input_date})\n"


@pytest.mark.parametrize(
    "consultant_paediatrician_referral_made,consultant_paediatrician_referral_date, consultant_paediatrician_input_achieved, consultant_paediatrician_input_date,paediatric_neurologist_referral_made,paediatric_neurologist_referral_date,paediatric_neurologist_input_achieved,paediatric_neurologist_input_date,expected_score",
    [
        (
            None,  # consultant_paediatrician_referral_made
            None,  # consultant_paediatrician_referral_date
            False,  # consultant_paediatrician_input_achieved
            None,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician not involved
        (
            True,  # consultant_paediatrician_referral_made
            None,  # consultant_paediatrician_referral_date
            None,  # consultant_paediatrician_input_achieved
            None,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician involved but not referred
        (
            True,  # consultant_paediatrician_referral_made
            REFERRAL_DATE,  # consultant_paediatrician_referral_date
            False,  # consultant_paediatrician_input_achieved
            None,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician involved but not referred
        (
            True,  # consultant_paediatrician_referral_made
            REFERRAL_DATE,  # consultant_paediatrician_referral_date
            True,  # consultant_paediatrician_input_achieved
            PASS_INPUT_DATE,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician seen within 14 days - both seen within 14 days so pass
        (
            True,  # consultant_paediatrician_referral_made
            REFERRAL_DATE,  # consultant_paediatrician_referral_date
            True,  # consultant_paediatrician_input_achieved
            FAIL_INPUT_DATE,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician seen after 14 days - only one has to be seen within 14 days
        (
            False,  # consultant_paediatrician_referral_made
            REFERRAL_DATE,  # consultant_paediatrician_referral_date
            True,  # consultant_paediatrician_input_achieved
            PASS_INPUT_DATE,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician not declared referred but seen and referred within 14 days: both seen within 14 days so pass
        (
            False,  # consultant_paediatrician_referral_made
            REFERRAL_DATE,  # consultant_paediatrician_referral_date
            True,  # consultant_paediatrician_input_achieved
            FAIL_INPUT_DATE,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician not declared referred but seen after 14 days of referral: only one has to be seen within 14 days
        (
            False,  # consultant_paediatrician_referral_made
            None,  # consultant_paediatrician_referral_date
            True,  # consultant_paediatrician_input_achieved
            FAIL_INPUT_DATE,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician not declared referred, no referral date but seen after 14 days of referral
        (
            False,  # consultant_paediatrician_referral_made
            REFERRAL_DATE,  # consultant_paediatrician_referral_date
            False,  # consultant_paediatrician_input_achieved
            None,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician not declared referred but referral date made but not seen
        (
            None,  # consultant_paediatrician_referral_made
            REFERRAL_DATE,  # consultant_paediatrician_referral_date
            False,  # consultant_paediatrician_input_achieved
            None,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician referral none with referral date but not seen
        (
            None,  # consultant_paediatrician_referral_made
            None,  # consultant_paediatrician_referral_date
            True,  # consultant_paediatrician_input_achieved
            PASS_INPUT_DATE,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            PASS_INPUT_DATE,  # paediatric_neurologist_input_date
            KPI_SCORE["PASS"],  # expected_score
        ),  # Neurologist seen within 14 days, paediatrician referral none with no input date but seen
    ],
)
@pytest.mark.django_db
def test_measure_1_should_pass_seen_neurologist(
    e12_case_factory,
    consultant_paediatrician_referral_made,
    consultant_paediatrician_referral_date,
    consultant_paediatrician_input_achieved,
    consultant_paediatrician_input_date,
    paediatric_neurologist_referral_made,
    paediatric_neurologist_referral_date,
    paediatric_neurologist_input_achieved,
    paediatric_neurologist_input_date,
    expected_score,
):

    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=consultant_paediatrician_referral_made,
        registration__assessment__consultant_paediatrician_referral_date=consultant_paediatrician_referral_date,
        registration__assessment__consultant_paediatrician_input_achieved=consultant_paediatrician_input_achieved,
        registration__assessment__consultant_paediatrician_input_date=consultant_paediatrician_input_date,
        registration__assessment__paediatric_neurologist_referral_made=paediatric_neurologist_referral_made,
        registration__assessment__paediatric_neurologist_referral_date=paediatric_neurologist_referral_date,
        registration__assessment__paediatric_neurologist_input_achieved=paediatric_neurologist_input_achieved,
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
    ), f"Patient saw a Neurologist in {PASS_INPUT_DATE - REFERRAL_DATE} after referral, but did not pass measure\nScores\npaediatrician\n- referral_made: {consultant_paediatrician_referral_made}\n- referral date: {consultant_paediatrician_referral_date}\n- achieved: {consultant_paediatrician_input_achieved}\n- input_date: {consultant_paediatrician_input_date},\n neurologist\n- referral_made: {paediatric_neurologist_referral_made}\n- referral_date: {paediatric_neurologist_referral_date}\n- achieved: {paediatric_neurologist_input_achieved}\n- input_date: {paediatric_neurologist_input_date})\n"


@pytest.mark.parametrize(
    "consultant_paediatrician_referral_made,consultant_paediatrician_referral_date, consultant_paediatrician_input_achieved, consultant_paediatrician_input_date,paediatric_neurologist_referral_made,paediatric_neurologist_referral_date,paediatric_neurologist_input_achieved,paediatric_neurologist_input_date,expected_score",
    [
        (True, REFERRAL_DATE, False, None, False, None, None, None, KPI_SCORE["FAIL"]),
        (
            True,
            REFERRAL_DATE,
            True,
            FAIL_INPUT_DATE,
            False,
            None,
            None,
            None,
            KPI_SCORE["FAIL"],
        ),
        (
            True,
            REFERRAL_DATE,
            None,
            FAIL_INPUT_DATE,
            False,
            None,
            None,
            None,
            KPI_SCORE["FAIL"],
        ),
        (
            True,
            REFERRAL_DATE,
            None,
            FAIL_INPUT_DATE,
            True,
            REFERRAL_DATE,
            None,
            None,
            KPI_SCORE["FAIL"],
        ),
        (
            False,
            None,
            None,
            None,
            True,
            REFERRAL_DATE,
            True,
            FAIL_INPUT_DATE,
            KPI_SCORE["FAIL"],
        ),
        (
            False,
            None,
            None,
            None,
            True,
            REFERRAL_DATE,
            None,
            FAIL_INPUT_DATE,
            KPI_SCORE["FAIL"],
        ),
        (
            True,
            REFERRAL_DATE,
            None,
            None,
            True,
            REFERRAL_DATE,
            False,
            FAIL_INPUT_DATE,
            KPI_SCORE["FAIL"],
        ),
        (
            False,  # consultant_paediatrician_referral_made
            None,  # consultant_paediatrician_referral_date
            None,  # consultant_paediatrician_input_achieved
            None,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            REFERRAL_DATE,  # paediatric_neurologist_referral_date
            True,  # paediatric_neurologist_input_achieved
            None,  # paediatric_neurologist_input_date
            KPI_SCORE["FAIL"],  # expected_score
        ),  # Paediatrician never referred, neurologist referred, input achieved but no date
    ],
)
@pytest.mark.django_db
def test_measure_1_should_fail_not_seen_paediatrician_or_neurologist_14_days_after_referral(
    e12_case_factory,
    consultant_paediatrician_referral_made,
    consultant_paediatrician_referral_date,
    consultant_paediatrician_input_achieved,
    consultant_paediatrician_input_date,
    paediatric_neurologist_referral_made,
    paediatric_neurologist_referral_date,
    paediatric_neurologist_input_achieved,
    paediatric_neurologist_input_date,
    expected_score,
):

    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=consultant_paediatrician_referral_made,
        registration__assessment__consultant_paediatrician_referral_date=consultant_paediatrician_referral_date,
        registration__assessment__consultant_paediatrician_input_achieved=consultant_paediatrician_input_achieved,
        registration__assessment__consultant_paediatrician_input_date=consultant_paediatrician_input_date,
        registration__assessment__paediatric_neurologist_referral_made=paediatric_neurologist_referral_made,
        registration__assessment__paediatric_neurologist_referral_date=paediatric_neurologist_referral_date,
        registration__assessment__paediatric_neurologist_input_achieved=paediatric_neurologist_input_achieved,
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
    ), f"Patient did not see a Paediatrician/Neurologist within 14 days of referral (seen after {FAIL_INPUT_DATE - REFERRAL_DATE}), but did not fail measure\nScores\npaediatrician\n- referral_made: {consultant_paediatrician_referral_made}\n- referral date: {consultant_paediatrician_referral_date}\n- achieved: {consultant_paediatrician_input_achieved}\n- input_date: {consultant_paediatrician_input_date},\n neurologist\n- referral_made: {paediatric_neurologist_referral_made}\n- referral_date: {paediatric_neurologist_referral_date}\n- achieved: {paediatric_neurologist_input_achieved}\n- input_date: {paediatric_neurologist_input_date})\n"


@pytest.mark.django_db
def test_measure_1_should_fail_no_doctor_involved(
    e12_case_factory,
):

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
    ), f"Patient did not see a Paediatrician/Neurologist, but did not fail measure - no doctor involved in care"


@pytest.mark.parametrize(
    "consultant_paediatrician_referral_made,consultant_paediatrician_referral_date, consultant_paediatrician_input_achieved, consultant_paediatrician_input_date,paediatric_neurologist_referral_made,paediatric_neurologist_referral_date,paediatric_neurologist_input_achieved,paediatric_neurologist_input_date,expected_score",
    [
        (
            True,  # consultant_paediatrician_referral_made
            REFERRAL_DATE,  # consultant_paediatrician_referral_date
            None,  # consultant_paediatrician_input_achieved
            None,  # consultant_paediatrician_input_date
            None,  # paediatric_neurologist_referral_made
            None,  # paediatric_neurologist_referral_date
            None,  # paediatric_neurologist_input_achieved
            None,  # paediatric_neurologist_input_date
            KPI_SCORE["NOT_SCORED"],  # expected_score
        ),  # Paediatrician referred but no other dates
        (
            True,  # consultant_paediatrician_referral_made
            REFERRAL_DATE,  # consultant_paediatrician_referral_date
            True,  # consultant_paediatrician_input_achieved
            None,  # consultant_paediatrician_input_date
            True,  # paediatric_neurologist_referral_made
            None,  # paediatric_neurologist_referral_date
            None,  # paediatric_neurologist_input_achieved
            None,  # paediatric_neurologist_input_date
            KPI_SCORE["NOT_SCORED"],  # expected_score
        ),  # Paediatrician referred, input achieved but no other dates
    ],
)
@pytest.mark.django_db
def test_measure_1_not_scored(
    e12_case_factory,
    consultant_paediatrician_referral_made,
    consultant_paediatrician_referral_date,
    consultant_paediatrician_input_achieved,
    consultant_paediatrician_input_date,
    paediatric_neurologist_referral_made,
    paediatric_neurologist_referral_date,
    paediatric_neurologist_input_achieved,
    paediatric_neurologist_input_date,
    expected_score,
):
    # creates a case with all audit values filled
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=consultant_paediatrician_referral_made,
        registration__assessment__consultant_paediatrician_referral_date=consultant_paediatrician_referral_date,
        registration__assessment__consultant_paediatrician_input_achieved=consultant_paediatrician_input_achieved,
        registration__assessment__consultant_paediatrician_input_date=consultant_paediatrician_input_date,
        registration__assessment__paediatric_neurologist_referral_made=paediatric_neurologist_referral_made,
        registration__assessment__paediatric_neurologist_referral_date=paediatric_neurologist_referral_date,
        registration__assessment__paediatric_neurologist_input_achieved=paediatric_neurologist_input_achieved,
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
    ), f"Patient did not have enough criteria to pass or fail measure, but did not return NOT_SCORED\nScores\npaediatrician\n- referral_made: {consultant_paediatrician_referral_made}\n- referral date: {consultant_paediatrician_referral_date}\n- achieved: {consultant_paediatrician_input_achieved}\n- input_date: {consultant_paediatrician_input_date},\n neurologist\n- referral_made: {paediatric_neurologist_referral_made}\n- referral_date: {paediatric_neurologist_referral_date}\n- achieved: {paediatric_neurologist_input_achieved}\n- input_date: {paediatric_neurologist_input_date})\n"


"""
PASSES
- [ ] Paediatrician seen withing 14 days, no neurology input or referral
Paediatrician
- consultant_paediatrician_referral_made               True
- consultant_paediatrician_referral_date                 REFERRAL_DATE
- consultant_paediatrician_input_achieved             True
- consultant_paediatrician_input_date                     PASS_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                   False
- paediatric_neurologist_referral_date                     None
- paediatric_neurologist_input_achieved                 None
- paediatric_neurologist_input_date                         None
# (True, REFERRAL_DATE, True, PASS_INPUT_DATE, False, None, None, None, KPI_SCORE["PASS"])

- [ ] Paediatrician seen withing 14 days (input achieved None as before introduced), no neurology input or referral
Paediatrician                                                               True
- consultant_paediatrician_referral_made               REFERRAL_DATE
- consultant_paediatrician_input_achieved             None
- consultant_paediatrician_input_date                     PASS_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                  False
- paediatric_neurologist_referral_date                    None
- paediatric_neurologist_input_achieved                None
- paediatric_neurologist_input_date                        None
# (True, REFERRAL_DATE, None, PASS_INPUT_DATE, False, None, None, None, KPI_SCORE["PASS"])

- [ ] Paediatrician seen within 14 days, neurologist referred and seen in 14 days
Paediatrician
- consultant_paediatrician_referral_made              True
- paediatric_neurologist_referral_date                    REFERRAL_DATE
- consultant_paediatrician_input_achieved             True
- consultant_paediatrician_input_date                   PASS_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                   True
- paediatric_neurologist_referral_date                      REFERRAL_DATE
- paediatric_neurologist_input_achieved                   True
- paediatric_neurologist_input_date                         PASS_INPUT_DATE
# (True, REFERRAL_DATE, True, PASS_INPUT_DATE, True, REFERRAL_DATE, True, PASS_INPUT_DATE, KPI_SCORE["PASS"]))

- [ ] Paediatrician seen within 14 days, neurologist referred and seen in 14 days (input achieved None as before introduced)
Paediatrician
- consultant_paediatrician_referral_made                True
- paediatric_neurologist_referral_date                   REFERRAL_DATE
- consultant_paediatrician_input_achieved           True
- consultant_paediatrician_input_date                   PASS_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                      REFERRAL_DATE
- paediatric_neurologist_input_achieved                 None
- paediatric_neurologist_input_date                         PASS_INPUT_DATE
# (True, REFERRAL_DATE, True, PASS_INPUT_DATE, True, REFERRAL_DATE, None, PASS_INPUT_DATE, KPI_SCORE["PASS"]))

- [ ] Paediatrician seen within 14 days, neurologist referred but not seen in 14 days 
Paediatrician
- consultant_paediatrician_referral_made                True
- paediatric_neurologist_referral_date                   REFERRAL_DATE
- consultant_paediatrician_input_achieved           True
- consultant_paediatrician_input_date                   PASS_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                      REFERRAL_DATE
- paediatric_neurologist_input_achieved                 True
- paediatric_neurologist_input_date                         FAIL_INPUT_DATE
# (True, REFERRAL_DATE, True, PASS_INPUT_DATE, True, REFERRAL_DATE, True, FAIL_INPUT_DATE, KPI_SCORE["PASS"]))

- [ ] Paediatrician seen within 14 days (input achieved None as before introduced), neurologist referred but not seen in 14 days 
Paediatrician
- consultant_paediatrician_referral_made                True
- paediatric_neurologist_referral_date                   REFERRAL_DATE
- consultant_paediatrician_input_achieved           None
- consultant_paediatrician_input_date                   PASS_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                      REFERRAL_DATE
- paediatric_neurologist_input_achieved                 True
- paediatric_neurologist_input_date                         FAIL_INPUT_DATE
# (True,REFERRAL_DATE,None,PASS_INPUT_DATE,True,REFERRAL_DATE,True,FAIL_INPUT_DATE, KPI_SCORE["PASS"]))

- [ ] Paediatrician seen within 14 days, neurologist referred but not seen in 14 days (input achieved None as before introduced)
Paediatrician
- consultant_paediatrician_referral_made                True
- paediatric_neurologist_referral_date                   REFERRAL_DATE
- consultant_paediatrician_input_achieved           True
- consultant_paediatrician_input_date                   PASS_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                      REFERRAL_DATE
- paediatric_neurologist_input_achieved                 None
- paediatric_neurologist_input_date                         FAIL_INPUT_DATE
# (True, REFERRAL_DATE, True, PASS_INPUT_DATE, True, REFERRAL_DATE, None, FAIL_INPUT_DATE, KPI_SCORE["PASS"]))

- [ ] Paediatrician seen within 14 days (input achieved None as before introduced), neurologist referred but not seen in 14 days (input achieved None as before introduced)
Paediatrician
- consultant_paediatrician_referral_made                True
- paediatric_neurologist_referral_date                   REFERRAL_DATE
- consultant_paediatrician_input_achieved           None
- consultant_paediatrician_input_date                   PASS_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                      REFERRAL_DATE
- paediatric_neurologist_input_achieved                 None
- paediatric_neurologist_input_date                         FAIL_INPUT_DATE
# (True, REFERRAL_DATE, None, PASS_INPUT_DATE, True, REFERRAL_DATE, None, FAIL_INPUT_DATE, KPI_SCORE["PASS"]))

- [ ] Paediatrician seen within 14 days, neurologist incomplete
Paediatrician
- consultant_paediatrician_referral_made                True
- paediatric_neurologist_referral_date                   REFERRAL_DATE
- consultant_paediatrician_input_achieved           True
- consultant_paediatrician_input_date                   PASS_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                      REFERRAL_DATE
- paediatric_neurologist_input_achieved                 True
- paediatric_neurologist_input_date                         None
# (True, REFERRAL_DATE, True, PASS_INPUT_DATE, True, REFERRAL_DATE, True, None, KPI_SCORE["PASS"]))

- [ ] Paediatrician not seen, neurologist seen within 14 days
Paediatrician
- consultant_paediatrician_referral_made             False
- paediatric_neurologist_referral_date                   None
- consultant_paediatrician_input_achieved           None
- consultant_paediatrician_input_date                   None
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                     REFERRAL_DATE
- paediatric_neurologist_input_achieved                 True
- paediatric_neurologist_input_date                         PASS_INPUT_DATE
# (False,None,None,None,True,REFERRAL_DATE,True,PASS_INPUT_DATE, KPI_SCORE["PASS"])

- [ ] Paediatrician not seen, neurologist seen within 14 days (input achieved None as before introduced)
Paediatrician
- consultant_paediatrician_referral_made             False
- paediatric_neurologist_referral_date                   None
- consultant_paediatrician_input_achieved           None
- consultant_paediatrician_input_date                   None
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                     REFERRAL_DATE
- paediatric_neurologist_input_achieved                 None
- paediatric_neurologist_input_date                         PASS_INPUT_DATE
# (False,None,None,None,True,REFERRAL_DATE,None,PASS_INPUT_DATE, KPI_SCORE["PASS"])

- [ ] Paediatrician incomplete, neurologist seen within 14 days
Paediatrician
- consultant_paediatrician_referral_made              True
- paediatric_neurologist_referral_date                   REFERRAL_DATE
- consultant_paediatrician_input_achieved           None
- consultant_paediatrician_input_date                   None
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                    REFERRAL_DATE
- paediatric_neurologist_input_achieved                True
- paediatric_neurologist_input_date                         PASS_INPUT_DATE     
# (True,REFERRAL_DATE,None,None,True,REFERRAL_DATE,True,PASS_INPUT_DATE, KPI_SCORE["PASS"]))

- [ ] Paediatrician incomplete, neurologist seen within 14 days (input achieved None as before introduced)
Paediatrician
- consultant_paediatrician_referral_made              True
- paediatric_neurologist_referral_date                   REFERRAL_DATE
- consultant_paediatrician_input_achieved           None
- consultant_paediatrician_input_date                   None
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                    REFERRAL_DATE
- paediatric_neurologist_input_achieved                None
- paediatric_neurologist_input_date                        PASS_INPUT_DATE
# (True, REFERRAL_DATE, None, None, True, REFERRAL_DATE, None, PASS_INPUT_DATE, KPI_SCORE["PASS"]))

(True, REFERRAL_DATE, True, PASS_INPUT_DATE, False, None, None, None, KPI_SCORE["PASS"]),
(True, REFERRAL_DATE, None, PASS_INPUT_DATE, False, None, None, None, KPI_SCORE["PASS"]),
(True, REFERRAL_DATE, True, PASS_INPUT_DATE, True, REFERRAL_DATE, True, PASS_INPUT_DATE, KPI_SCORE["PASS"])),
(True, REFERRAL_DATE, True, PASS_INPUT_DATE, True, REFERRAL_DATE, None, PASS_INPUT_DATE, KPI_SCORE["PASS"])),
(True, REFERRAL_DATE, True, PASS_INPUT_DATE, True, REFERRAL_DATE, True, FAIL_INPUT_DATE, KPI_SCORE["PASS"])),
(True,REFERRAL_DATE,None,PASS_INPUT_DATE,True,REFERRAL_DATE,True,FAIL_INPUT_DATE, KPI_SCORE["PASS"])),
(True, REFERRAL_DATE, True, PASS_INPUT_DATE, True, REFERRAL_DATE, None, FAIL_INPUT_DATE, KPI_SCORE["PASS"])),
(True, REFERRAL_DATE, None, PASS_INPUT_DATE, True, REFERRAL_DATE, None, FAIL_INPUT_DATE, KPI_SCORE["PASS"])),
(True, REFERRAL_DATE, True, PASS_INPUT_DATE, True, REFERRAL_DATE, True, None, KPI_SCORE["PASS"])),
(False,None,None,None,True,REFERRAL_DATE,True,PASS_INPUT_DATE, KPI_SCORE["PASS"]),
(False,None,None,None,True,REFERRAL_DATE,None,PASS_INPUT_DATE, KPI_SCORE["PASS"]),
(True,REFERRAL_DATE,None,None,True,REFERRAL_DATE,True,PASS_INPUT_DATE, KPI_SCORE["PASS"])),
(True, REFERRAL_DATE, None, None, True, REFERRAL_DATE, None, PASS_INPUT_DATE, KPI_SCORE["PASS"])),
"""


"""
FAILS

- [ ] Paediatrician not referred, no neurology input or referral
Paediatrician
- consultant_paediatrician_referral_made               False
- consultant_paediatrician_referral_date                 None
- consultant_paediatrician_input_achieved             None
- consultant_paediatrician_input_date                     None
Neurologist
- paediatric_neurologist_referral_made                   False
- paediatric_neurologist_referral_date                     None
- paediatric_neurologist_input_achieved                 None
- paediatric_neurologist_input_date                         None
# (True, REFERRAL_DATE, False, None, False, None, None, None, KPI_SCORE["FAIL"])

- [ ] Paediatrician not seen within 14 days, no neurology input or referral
Paediatrician
- consultant_paediatrician_referral_made               True
- consultant_paediatrician_referral_date                 REFERRAL_DATE
- consultant_paediatrician_input_achieved             True
- consultant_paediatrician_input_date                     FAIL_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                  False
- paediatric_neurologist_referral_date                     None
- paediatric_neurologist_input_achieved                 None
- paediatric_neurologist_input_date                         None
# (True,REFERRAL_DATE,True,FAIL_INPUT_DATE,False,None,None,None)

- [ ] Paediatrician not seen within 14 days (Input achieved none as before introduced), no neurology input or referral
Paediatrician
- consultant_paediatrician_referral_made               True
- consultant_paediatrician_referral_date                 REFERRAL_DATE
- consultant_paediatrician_input_achieved             None
- consultant_paediatrician_input_date                     FAIL_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                  False
- paediatric_neurologist_referral_date                     None
- paediatric_neurologist_input_achieved                 None
- paediatric_neurologist_input_date                         None
# (True,REFERRAL_DATE,None,FAIL_INPUT_DATE,False,None,None,None)

- [ ] Paediatrician not seen within 14 days, neurology incomplete
Paediatrician
- consultant_paediatrician_referral_made               True
- consultant_paediatrician_referral_date                 REFERRAL_DATE
- consultant_paediatrician_input_achieved             None
- consultant_paediatrician_input_date                     FAIL_INPUT_DATE
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                     REFERRAL_DATE
- paediatric_neurologist_input_achieved                 None
- paediatric_neurologist_input_date                         None
# (True,REFERRAL_DATE,None,FAIL_INPUT_DATE,rue,REFERRAL_DATE,None,None)

- [ ] Paediatrician not referred, neurology seen but no input within 14 days
Paediatrician
- consultant_paediatrician_referral_made               False
- consultant_paediatrician_referral_date                 None
- consultant_paediatrician_input_achieved             None
- consultant_paediatrician_input_date                     None
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                     REFERRAL_DATE
- paediatric_neurologist_input_achieved                 True
- paediatric_neurologist_input_date                         FAIL_INPUT_DATE
# (False,None,None,None,True, REFERRAL_DATE,True,FAIL_INPUT_DATE)

- [ ] Paediatrician not referred, neurology seen but no input within 14 days (input achieved None as before introduced)
Paediatrician
- consultant_paediatrician_referral_made               False
- consultant_paediatrician_referral_date                 None
- consultant_paediatrician_input_achieved             None
- consultant_paediatrician_input_date                     None
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                     REFERRAL_DATE
- paediatric_neurologist_input_achieved                 None
- paediatric_neurologist_input_date                         FAIL_INPUT_DATE
# (False,None,None,None,True, REFERRAL_DATE,None,FAIL_INPUT_DATE)

- [ ] Paediatrician incomplete, neurology seen but no input within 14 days
Paediatrician
- consultant_paediatrician_referral_made               True
- consultant_paediatrician_referral_date                 REFERRAL_DATE
- consultant_paediatrician_input_achieved             None
- consultant_paediatrician_input_date                     None
Neurologist
- paediatric_neurologist_referral_made                  True
- paediatric_neurologist_referral_date                     REFERRAL_DATE
- paediatric_neurologist_input_achieved                 FALSE
- paediatric_neurologist_input_date                         FAIL_INPUT_DATE
# (True,REFERRAL_DATE,None,None,True,REFERRAL_DATE,FALSE,FAIL_INPUT_DATE)

(True, REFERRAL_DATE, False, None, False, None, None, None, KPI_SCORE["FAIL"]),
(True,REFERRAL_DATE,True,FAIL_INPUT_DATE,False,None,None,None,KPI_SCORE["FAIL"]),
(True,REFERRAL_DATE,None,FAIL_INPUT_DATE,False,None,None,None,KPI_SCORE["FAIL"]),
(True,REFERRAL_DATE,None,FAIL_INPUT_DATE,rue,REFERRAL_DATE,None,None,KPI_SCORE["FAIL"]),
(False,None,None,None,True, REFERRAL_DATE,True,FAIL_INPUT_DATE,KPI_SCORE["FAIL"]),
(False,None,None,None,True, REFERRAL_DATE,None,FAIL_INPUT_DATE,KPI_SCORE["FAIL"]),
(True,REFERRAL_DATE,None,None,True,REFERRAL_DATE,FALSE,FAIL_INPUT_DATE,KPI_SCORE["FAIL"]),
"""
