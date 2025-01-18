"""
Tests the Registration model.

Tests:

    - [x] Test a valid Registration
    - [x] Test for DOFPA in the future
    - [x] Test for DOFPA before E12 began
    - [x] Test for DOFPA before the child's DOB

"""

# Standard imports
from datetime import date
from dateutil.relativedelta import relativedelta
from unittest.mock import patch

# Django imports
from django.core.exceptions import ValidationError
from django.urls import reverse

# Third party imports
import pytest

# RCPCH imports
from epilepsy12.models import Registration, Organisation, Epilepsy12User, Site
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_clinicial_audit_team_data,
    test_user_rcpch_audit_team_data,
)


@pytest.mark.django_db
def test_registration_custom_method_audit_submission_date_calculation(
    e12_case_factory,
):
    """
    Tests the `audit_submission_date_calculation` accurately calculates audit submission date, depending on different registration dates.

    This is always the second Tuesday of January, following 1 year after the first paediatric assessment.

    If registration date + 1 year IS the 2nd Tues of Jan, the submission date is the same as registration + 1 year.
    """

    first_paediatric_assessment_dates = [
        # (registration date, expected audit submission date)
        (date(2022, 11, 1), date(2024, 1, 9)),  # cohort 5
        (date(2022, 12, 31), date(2025, 1, 14)),  # cohort 6
        (date(2022, 1, 9), date(2024, 1, 9)),  # cohort 5
        (date(2022, 1, 10), date(2024, 1, 9)),  # cohort 5
        (date(2022, 1, 11), date(2024, 1, 9)),  # cohort 5
    ]

    for expected_input_output in first_paediatric_assessment_dates:
        registration = e12_case_factory(
            registration__first_paediatric_assessment_date=expected_input_output[0]
        ).registration

        assert registration.audit_submission_date == expected_input_output[1]


@pytest.mark.django_db
def test_registration_custom_method_first_paediatric_assessment_date_one_year_on(
    e12_case_factory,
):
    """
    Tests the `first_paediatric_assessment_date_one_year_on` accurately calculates one year on (registration close date).

    This is always 1 year after `first_paediatric_assessment_date`.
    """

    expected_inputs_outputs = [
        # (registration date, one year on date)
        (date(2022, 11, 1), date(2023, 11, 1)),  # cohort 5
        (date(2022, 12, 31), date(2023, 12, 31)),  # cohort 6
        (date(2022, 1, 9), date(2023, 1, 9)),  # cohort 5
        (date(2022, 1, 10), date(2023, 1, 10)),  # cohort 5
        (date(2022, 1, 11), date(2023, 1, 11)),  # cohort 5
    ]

    for expected_input_output in expected_inputs_outputs:
        registration = e12_case_factory(
            registration__first_paediatric_assessment_date=expected_input_output[0]
        ).registration

        assert (
            registration.completed_first_year_of_care_date == expected_input_output[1]
        )


@pytest.mark.django_db
def test_registration_cohort(
    e12_case_factory,
):
    """
    Tests cohort number is set accurately, dependent on first_paediatric_assessment_date.

    Cohorts are defined between 1st December year and 30th November in the subsequent year.

    Examples of cohort numbers:
        Cohort 4: 1 December 2020 - 30 November 2021
        Cohort 5: 1 December 2021 - 30 November 2022
        Cohort 6: 1 December 2022 - 30 November 2023
        Cohort 7: 1 December 2023 - 30 November 2024

    Dates which are too early (< 2020) should return `None`.
    """

    expected_inputs_outputs = [
        # (registration date, expected cohort)
        (date(2019, 11, 1), None),
        (date(2020, 11, 30), None),
        (date(2020, 12, 1), 4),
        (date(2021, 11, 30), 4),
        (date(2021, 12, 1), 5),
    ]

    for expected_input_output in expected_inputs_outputs:
        registration = e12_case_factory(
            registration__first_paediatric_assessment_date=expected_input_output[0]
        ).registration

        assert registration.cohort == expected_input_output[1]


@patch.object(Registration, "get_current_date", return_value=date(2022, 11, 30))
@pytest.mark.django_db
def test_registration_days_remaining_before_submission(
    mocked_get_current_date,
    e12_case_factory,
):
    """
    Tests `days_remaining_before_submission` property calculated properly.

    Calculated as submission date - current date, return number of days left days as an int.

    Test patches "today" - patches the example Registration instance's `.get_current_date`'s return value to always return 30 Nov 2022.

    NOTE: if `audit_submission_date` is before today, returns 0.
    """

    # submission date = 9/1/24, today = 30/11/22 405 days after today (30/11/22)
    registration = e12_case_factory(
        registration__first_paediatric_assessment_date=date(
            2022, 1, 10
        )  # cohort 5, submission date 9/1/24
    ).registration
    assert registration.days_remaining_before_submission == 405

    # submission date = 2023-01-10, 41 days after today
    registration = e12_case_factory(
        registration__first_paediatric_assessment_date=date(
            2021, 1, 1
        )  # cohort 4, submission 10/1/2023
    ).registration
    assert registration.days_remaining_before_submission == 41


@pytest.mark.xfail
@patch.object(Registration, "get_current_date", return_value=date(2023, 1, 1))
@pytest.mark.django_db
def test_registration_validate_dofpa_not_future(
    mocked_current_date,
    e12_case_factory,
):
    """
    # TODO - add validation

    Test related to ensuring model-level validation of inputted Date of First Paediatric Assessment (first_paediatric_assessment_date).

    Patches Registration's .get_current_date() method to always be 1 Jan 2023.

    """

    # Tests that dofpa (first_paediatric_assessment_date) can't be in the future (relative to today). Tries to create and save a Registration which is 30 days ahead of today.
    future_date = Registration.get_current_date() + relativedelta(days=30)
    with pytest.raises(ValidationError):
        e12_case_factory(registration__first_paediatric_assessment_date=future_date)


@pytest.mark.xfail
@pytest.mark.django_db
def test_registration_validate_dofpa_not_before_2009(e12_case_factory):
    """
    # TODO - add validation

    Tests related to ensuring model-level validation of inputted Date of First Paediatric Assessment (first_paediatric_assessment_date).

    """

    # Tests that dofpa (first_paediatric_assessment_date) can't be before E12 began in 2009.
    with pytest.raises(ValidationError):
        e12_case_factory(
            registration__first_paediatric_assessment_date=date(2007, 8, 9)
        )


@pytest.mark.xfail
@pytest.mark.django_db
def test_registration_validate_dofpa_not_before_child_dob(e12_case_factory):
    """
    # TODO - add validation

    Tests related to ensuring model-level validation of inputted Date of First Paediatric Assessment (first_paediatric_assessment_date).

    """
    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    # Tests that dofpa (first_paediatric_assessment_date) can't be before the child's DoB
    with pytest.raises(ValidationError):
        case = e12_case_factory(
            date_of_birth=date_of_birth,
            registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
        )


@pytest.mark.django_db
def test_registration_transfer_response(
    client, e12_case_factory, e12_site_factory, e12_user_factory
):
    """
    Tests that the `transfer_response` method works as expected.

    This method is used to transfer the primary site of care to a new site.
    In the process the existing site sets the `site_is_actively_involved_in_epilepsy_care` to False and a new site is create where it is set it to True.
    If the new site is already involved in epilepsy care, the `site_is_primary_centre_of_epilepsy_care` is set to True, and the existing responsibility is retained.
    The old site is retained in the database, but is no longer the primary site of care.

    the `transfer_response` method is called from the view when the new site approves the transfer request.
    It accepts the Organisation id of the new organisation, the case id and a string indicating the response of the new organisation.
    This string can be either 'accept' or 'reject'.
    """
    date_of_birth = date(2023, 1, 1)
    first_paediatric_assessment_date = date_of_birth + relativedelta(days=10)

    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    KCH = Organisation.objects.get(
        ods_code="RJZ01",
        trust__ods_code="RJZ",
    )

    # Create the Case instance and associate it with the Site
    case = e12_case_factory(
        date_of_birth=date_of_birth,
        registration__first_paediatric_assessment_date=first_paediatric_assessment_date,
    )
    # Create the Site instance and set the field - KCH is the primary site of care, but a transfer to GOSH is requested
    site = e12_site_factory(
        organisation=GOSH,
        case=case,
        active_transfer=True,
        transfer_origin_organisation=KCH,
        transfer_request_date=date.today(),
    )
    case.organisations.add(KCH)
    case.registration.kpi.organisation = KCH
    case.registration.kpi.save()

    # Verify the Site instance
    assert (
        site.site_is_primary_centre_of_epilepsy_care is True
    ), f"KCH is the primary site of care before the transfer, but the test is set up to transfer to {site.organisation}"
    assert (
        site.case == case
    ), f"The site is associated with the {case}, but should be associated with {site.case}"
    assert (
        site.organisation == GOSH
    ), f"The site is associated with {site.organisation}, but should be associated with {GOSH}"
    assert (
        site.active_transfer is True
    ), "The site has no active transfer request, but the test is set up to have an active transfer"
    assert (
        site.transfer_origin_organisation == KCH
    ), f"The site has a transfer request from {site.transfer_origin_organisation}, but should be from {KCH}"

    # Verify the organisation associated with the KPI associated with the Case instance's registration is KCH
    assert case.registration.kpi.organisation == KCH

    # Verify the Case instance
    case.refresh_from_db()
    assert case.organisations.filter(pk=KCH.pk).exists()

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

    client.force_login(test_user)

    # OTP ENABLE
    twofactor_signin(client, test_user=test_user)

    # GOSH now approves the transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": GOSH.pk,
                "case_id": case.id,
                "organisation_response": "accept",
            },
        )
    )

    assert response.status_code == 200

    # Verify the Site instance
    kch_site = Site.objects.get(
        organisation=KCH,
        case=case,
    )

    # KCH is no longer the primary site of care
    assert kch_site.site_is_primary_centre_of_epilepsy_care is False
    assert kch_site.site_is_actively_involved_in_epilepsy_care is False
    assert kch_site.case == case

    # GOSH is now the primary site of care
    new_site = Site.objects.get(
        organisation=GOSH,
        case=case,
    )
    assert new_site.site_is_primary_centre_of_epilepsy_care is True
    assert new_site.site_is_actively_involved_in_epilepsy_care is True
    assert new_site.case == case
    assert new_site.active_transfer is False
    assert new_site.transfer_origin_organisation is None
    assert new_site.transfer_request_date is None
    # Verify the organisation associated with the KPI associated with the Case instance's registration has changed to GOSH
    assert case.registration.kpi.organisation == GOSH
