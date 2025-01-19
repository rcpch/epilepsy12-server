"""
Tests the Assessment model
"""

# Standard imports
from datetime import date
from dateutil.relativedelta import relativedelta
import pytest
from unittest.mock import patch

# Third party imports
from django.core.exceptions import ValidationError

# RCPCH imports
from epilepsy12.models import Assessment, Organisation, Site
from epilepsy12.views.assessment_views import update_site_model

"""
- [x] Assessment.consultant_paediatrician_referral_date and Assessment.consultant_paediatrician_input_date are both None if Assessment.consultant_paediatrician_referral_made is False
- [x] Assessment.consultant_paediatrician_referral_date and Assessment.consultant_paediatrician_input_date cannot be in the future
- [x] Assessment.consultant_paediatrician_referral_date cannot be after Assessment.consultant_paediatrician_input_date
- [x] Neither Assessment.consultant_paediatrician_referral_date nor Assessment.consultant_paediatrician_input_date can be before Registration.first_paediatric_assessment_date or Case.date_of_birth
- [x] Assessment.paediatric_neurologist_input_date and Assessment.paediatric_neurologist_referral_date are both None if Assessment.paediatric_neurologist_referral_made is False
- [x] Assessment.paediatric_neurologist_input_date and Assessment.paediatric_neurologist_referral_date cannot be in the future
- [x] Assessment.paediatric_neurologist_input_date cannot be after Assessment.paediatric_neurologist_referral_date
- [x] Neither Assessment.paediatric_neurologist_input_date nor Assessment.paediatric_neurologist_referral_date can be before Registration.first_paediatric_assessment_date or Case.date_of_birth
- [x] Assessment.childrens_epilepsy_surgical_service_input_date and Assessment.childrens_epilepsy_surgical_service_referral_date are both None if Assessment.childrens_epilepsy_surgical_service_referral_made is False
- [x] Assessment.childrens_epilepsy_surgical_service_input_date and Assessment.childrens_epilepsy_surgical_service_referral_date cannot be in the future
- [x] Assessment.childrens_epilepsy_surgical_service_input_date cannot be after Assessment.childrens_epilepsy_surgical_service_referral_date
- [x] Neither Assessment.childrens_epilepsy_surgical_service_input_date nor Assessment.childrens_epilepsy_surgical_service_referral_date can be before Registration.first_paediatric_assessment_date or Case.date_of_birth
- [x] Assessment.epilepsy_specialist_nurse_input_date and Assessment.epilepsy_specialist_nurse_referral_date are both None if Assessment.epilepsy_specialist_nurse_referral_made is False
- [x] Assessment.epilepsy_specialist_nurse_input_date and Assessment.epilepsy_specialist_nurse_referral_date cannot be in the future
- [x] Assessment.epilepsy_specialist_nurse_input_date cannot be after Assessment.epilepsy_specialist_nurse_referral_date
- [x] Neither Assessment.epilepsy_specialist_nurse_input_date nor Assessment.epilepsy_specialist_nurse_referral_date can be before Registration.first_paediatric_assessment_date or Case.date_of_birth
"""


@pytest.mark.django_db
def test_validation_referral_date_and_input_date_both_none_when_referral_made_false(
    e12_case_factory,
):
    """
    Tests:
    - Assessment.consultant_paediatrician_referral_date and Assessment.consultant_paediatrician_input_date are both None if Assessment.consultant_paediatrician_referral_made is False.
    - Assessment.paediatric_neurologist_referral_date and Assessment.paediatric_neurologist_input_date are both None if Assessment.paediatric_neurologist_referral_made is False.
    - Assessment.childrens_epilepsy_surgical_service_referral_date and Assessment.childrens_epilepsy_surgical_service_input_date are both None if Assessment.childrens_epilepsy_surgical_service_referral_made is False.
    - Assessment.epilepsy_specialist_nurse_referral_date and Assessment.epilepsy_specialist_nurse_input_date are both None if Assessment.epilepsy_specialist_nurse_referral_made is False.
    """

    assessment = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_made=False,
        registration__assessment__paediatric_neurologist_referral_made=False,
        registration__assessment__childrens_epilepsy_surgical_service_referral_made=False,
        registration__assessment__epilepsy_specialist_nurse_referral_made=False,
    ).registration.assessment

    assert (assessment.consultant_paediatrician_referral_date is None) and (
        assessment.consultant_paediatrician_input_date is None
    )
    assert (assessment.paediatric_neurologist_referral_date is None) and (
        assessment.paediatric_neurologist_input_date is None
    )
    assert (assessment.childrens_epilepsy_surgical_service_referral_date is None) and (
        assessment.childrens_epilepsy_surgical_service_input_date is None
    )
    assert (assessment.epilepsy_specialist_nurse_referral_date is None) and (
        assessment.epilepsy_specialist_nurse_input_date is None
    )


@pytest.mark.xfail
@patch.object(Assessment, "get_current_date", return_value=date(2023, 10, 1))
@pytest.mark.django_db
def test_validation_referral_date_and_input_date_cant_be_future(
    mocked_get_current_date,
    e12_case_factory,
):
    """
    Tests:
    - Assessment.consultant_paediatrician_referral_date and Assessment.consultant_paediatrician_input_date cannot be in the future relative to today.
    - Assessment.paediatric_neurologist_referral_date and Assessment.paediatric_neurologist_input_date cannot be in the future relative to today.
    - Assessment.childrens_epilepsy_surgical_service_referral_date and Assessment.childrens_epilepsy_surgical_service_input_date cannot be in the future relative to today.
    - Assessment.epilepsy_specialist_nurse_referral_date and Assessment.epilepsy_specialist_nurse_input_date cannot be in the future relative to today.

    Patches .get_current_date method.
    """

    # try saving referral and input date which are 1 month ahead of patched today
    referral_date = date(2023, 11, 1)
    input_date = date(2023, 11, 1)

    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            registration__assessment__consultant_paediatrician_referral_date=referral_date,
            registration__assessment__consultant_paediatrician_input_date=input_date,
        ).registration.assessment
    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            registration__assessment__paediatric_neurologist_referral_date=referral_date,
            registration__assessment__paediatric_neurologist_input_date=input_date,
        ).registration.assessment
    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            registration__assessment__childrens_epilepsy_surgical_service_referral_date=referral_date,
            registration__assessment__childrens_epilepsy_surgical_service_input_date=input_date,
        ).registration.assessment
    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            registration__assessment__epilepsy_specialist_nurse_referral_date=referral_date,
            registration__assessment__epilepsy_specialist_nurse_input_date=input_date,
        ).registration.assessment


@pytest.mark.xfail
@pytest.mark.django_db
def test_validation_consultant_paediatrician_input_date_cant_be_after_referral_date(
    e12_case_factory,
):
    """
    - Tests Assessment.consultant_paediatrician_referral_date cannot be after Assessment.consultant_paediatrician_input_date.
    - Tests Assessment.paediatric_neurologist_referral_date cannot be after Assessment.paediatric_neurologist_input_date.
    - Tests Assessment.childrens_epilepsy_surgical_service_input_date cannot be after Assessment.childrens_epilepsy_surgical_service_referral_date.
    - Tests Assessment.epilepsy_specialist_nurse_input_date cannot be after Assessment.epilepsy_specialist_nurse_referral_date.

    """

    referral_date = date(2023, 1, 1)
    input_date = date(2023, 2, 1)

    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            registration__assessment__consultant_paediatrician_referral_date=referral_date,
            registration__assessment__consultant_paediatrician_input_date=input_date,
        ).registration.assessment
    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            registration__assessment__paediatric_neurologist_referral_date=referral_date,
            registration__assessment__paediatric_neurologist_input_date=input_date,
        ).registration.assessment
    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            registration__assessment__childrens_epilepsy_surgical_service_referral_date=referral_date,
            registration__assessment__childrens_epilepsy_surgical_service_input_date=input_date,
        ).registration.assessment
    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            registration__assessment__epilepsy_specialist_nurse_referral_date=referral_date,
            registration__assessment__epilepsy_specialist_nurse_input_date=input_date,
        ).registration.assessment


@pytest.mark.xfail
@pytest.mark.django_db
def test_validation_consultant_paediatrician_referral_date_nor_input_date_before_first_paediatric_assessment_date_or_dob(
    e12_case_factory,
):
    """
    Tests
    - neither Assessment.consultant_paediatrician_referral_date nor Assessment.consultant_paediatrician_input_date can be before Registration.first_paediatric_assessment_date or Case.date_of_birth
    - neither Assessment.paediatric_neurologist_referral_date nor Assessment.paediatric_neurologist_input_date can be before Registration.first_paediatric_assessment_date or Case.date_of_birth
    - neither Assessment.childrens_epilepsy_surgical_service_referral_date nor Assessment.childrens_epilepsy_surgical_service_input_date can be before Registration.first_paediatric_assessment_date or Case.date_of_birth
    - neither Assessment.epilepsy_specialist_nurse_referral_date nor Assessment.epilepsy_specialist_nurse_input_date can be before Registration.first_paediatric_assessment_date or Case.date_of_birth
    """

    date_of_birth = date(2020, 1, 1)
    first_paediatric_assessment_date = date(2022, 1, 1)
    referral_date = date_of_birth - relativedelta(
        days=1
    )  # one day before date of birth
    input_date = first_paediatric_assessment_date - relativedelta(
        days=1
    )  # one day before registration date

    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            date_of_birth=date_of_birth,
            first_paediatric_assessment_date=first_paediatric_assessment_date,
            registration__assessment__consultant_paediatrician_referral_date=referral_date,
            registration__assessment__consultant_paediatrician_input_date=input_date,
        ).registration.assessment
    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            date_of_birth=date_of_birth,
            first_paediatric_assessment_date=first_paediatric_assessment_date,
            registration__assessment__paediatric_neurologist_referral_date=referral_date,
            registration__assessment__paediatric_neurologist_input_date=input_date,
        ).registration.assessment
    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            date_of_birth=date_of_birth,
            first_paediatric_assessment_date=first_paediatric_assessment_date,
            registration__assessment__childrens_epilepsy_surgical_service_referral_date=referral_date,
            registration__assessment__childrens_epilepsy_surgical_service_input_date=input_date,
        ).registration.assessment
    with pytest.raises(ValidationError):
        assessment = e12_case_factory(
            date_of_birth=date_of_birth,
            first_paediatric_assessment_date=first_paediatric_assessment_date,
            registration__assessment__epilepsy_specialist_nurse_referral_date=referral_date,
            registration__assessment__epilepsy_specialist_nurse_input_date=input_date,
        ).registration.assessment


# The following tests check if the calculated wait times for each service are correct.
# They all use the same function (epilepsy12.general_functions.time_elapsed.stringify_time_elapsed)
# behind the scenes, so the tests are designed to cover the range of cases handled by the logic in that function.


@pytest.mark.xfail
@pytest.mark.django_db
def test_consultant_paediatrician_wait_only_one_date(e12_case_factory):
    """
    Tests for an error when only one date is supplied
    """
    # Create an Assessment object with referral and input dates for a consultant paediatrician
    assessment = e12_case_factory(
        registration__assessment__consultant_paediatrician_input_date=None
    ).registration.assessment

    # Only one date was supplied so an error should be raised
    with pytest.raises(ValueError):
        assessment.consultant_paediatrician_wait()


@pytest.mark.django_db
def test_consultant_paediatrician_wait_days(e12_case_factory):
    """
    Tests output when the wait is in days
    """
    assessment = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_date=date(
            2023, 1, 1
        ),
        registration__assessment__consultant_paediatrician_input_date=date(2023, 1, 3),
    ).registration.assessment

    # Check if the calculated wait time for the consultant paediatrician is correct
    assert assessment.consultant_paediatrician_wait() == 2


@pytest.mark.django_db
def test_consultant_paediatrician_wait_weeks(e12_case_factory):
    """
    Tests output when the wait is in weeks
    """
    referral_date = date(2023, 1, 1)
    input_date = referral_date + relativedelta(weeks=2)

    assessment = e12_case_factory(
        registration__assessment__consultant_paediatrician_referral_date=referral_date,
        registration__assessment__consultant_paediatrician_input_date=input_date,
    ).registration.assessment

    # Check if the calculated wait time for the consultant paediatrician is correct
    assert assessment.consultant_paediatrician_wait() == 14


@pytest.mark.django_db
def test_paediatric_neurologist_wait_months(e12_case_factory):
    """
    Tests output when the wait is in months
    """
    referral_date = date(2023, 1, 1)
    input_date = referral_date + relativedelta(months=4)

    assessment = e12_case_factory(
        registration__assessment__paediatric_neurologist_referral_date=referral_date,
        registration__assessment__paediatric_neurologist_input_date=input_date,
    ).registration.assessment

    # Check if the calculated wait time for the paediatric neurologist is correct
    assert assessment.paediatric_neurologist_wait() == 120


@pytest.mark.django_db
def test_childrens_epilepsy_surgery_wait_years(e12_case_factory):
    """
    Tests output when the wait is in years
    """
    referral_date = date(2023, 1, 1)
    input_date = referral_date + relativedelta(years=2, months=2)

    assessment = e12_case_factory(
        registration__assessment__childrens_epilepsy_surgical_service_referral_date=referral_date,
        registration__assessment__childrens_epilepsy_surgical_service_input_date=input_date,
    ).registration.assessment

    # Check if the calculated wait time for the children's epilepsy surgery service is correct
    assert assessment.childrens_epilepsy_surgery_wait() == 790


@pytest.mark.django_db
def test_epilepsy_nurse_specialist_wait_same_day(e12_case_factory):
    """
    Tests output when the wait is in 0 days (same day)
    """
    referral_date = date(2023, 1, 1)
    input_date = referral_date

    assessment = e12_case_factory(
        registration__assessment__epilepsy_specialist_nurse_referral_date=referral_date,
        registration__assessment__epilepsy_specialist_nurse_input_date=input_date,
    ).registration.assessment

    # Check if the calculated wait time for the epilepsy nurse specialist is correct
    assert assessment.epilepsy_nurse_specialist_wait() == 0


@pytest.mark.django_db
def test_allocate_general_paediatric_centre_to_case_same_organisation_as_lead(
    e12_case_factory, e12_site_factory
):
    """
    Tests the update_site_model function
    it accepts the following parameters:

    centre_role: str, selected_organisation, case, user, site_id=None

    centre_role is one of the following:
    - general_paediatric_centre
    - paediatric_neurology_centre
    - epilepsy_surgery_centre
    """
    # create a case object
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_input_date=None
    )

    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    ADDENBROOKES = Organisation.objects.get(ods_code="RGT01")  # Addenbrookes

    site = e12_site_factory(
        organisation=ADDENBROOKES,
        case=case,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_general_paediatric_centre=False,
    )

    # create a case object
    assessment = case.registration.assessment

    # create a user object
    user = assessment.registration.case.created_by

    # create an organisation object - this is the selected organisation and may not be the same as the site organisation
    selected_organisation = ADDENBROOKES

    site = Site.objects.get(
        organisation__ods_code="RGT01",
        case=case,
    )

    # ensure the site associated with the case is not a general paediatric centre
    assert site.organisation == ADDENBROOKES
    assert site.site_is_primary_centre_of_epilepsy_care is True
    assert site.site_is_actively_involved_in_epilepsy_care is True
    assert site.site_is_general_paediatric_centre is False

    # update the site model
    update_site_model(
        centre_role="general_paediatric_centre",
        selected_organisation=selected_organisation,
        case=case,
        user=user,
        site_id=site.id,
    )

    # check if the site model was updated
    site = Site.objects.get(
        organisation__ods_code="RGT01",
        case=case,
    )

    # check if the site model was updated
    assert site.organisation == ADDENBROOKES
    assert site.site_is_primary_centre_of_epilepsy_care is True
    assert site.site_is_actively_involved_in_epilepsy_care is True
    assert site.site_is_general_paediatric_centre is True
    assert site.case == case


@pytest.mark.django_db
def test_allocate_general_paediatric_centre_to_case_different_organisation_as_lead(
    e12_case_factory, e12_site_factory
):
    """
    Tests the update_site_model function
    it accepts the following parameters:

    centre_role: str, selected_organisation, case, user, site_id=None

    centre_role is one of the following:
    - general_paediatric_centre
    - paediatric_neurology_centre
    - epilepsy_surgery_centre
    """
    # create a case object
    case = e12_case_factory(
        registration__assessment__consultant_paediatrician_input_date=None
    )

    GOSH = Organisation.objects.get(
        ods_code="RP401",
        trust__ods_code="RP4",
    )

    ADDENBROOKES = Organisation.objects.get(ods_code="RGT01")  # Addenbrookes

    site = e12_site_factory(
        organisation=ADDENBROOKES,
        case=case,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_general_paediatric_centre=False,
    )

    # create a case object
    assessment = case.registration.assessment

    # create a user object
    user = assessment.registration.case.created_by

    # create an organisation object - this is the selected organisation and may not be the same as the site organisation
    selected_organisation = GOSH

    site = Site.objects.get(
        organisation=ADDENBROOKES,
        case=case,
    )

    # update the site model
    update_site_model(
        centre_role="general_paediatric_centre",
        selected_organisation=selected_organisation,
        case=case,
        user=user,
        site_id=site.id,
    )

    # check if the site model was updated
    addenbrookes_site = Site.objects.get(
        organisation=ADDENBROOKES,
        case=case,
    )

    gosh_site = Site.objects.get(
        organisation=GOSH,
        case=case,
    )

    # check if the site model was updated
    assert addenbrookes_site.organisation == ADDENBROOKES
    assert addenbrookes_site.site_is_primary_centre_of_epilepsy_care is True
    assert addenbrookes_site.site_is_actively_involved_in_epilepsy_care is True
    assert addenbrookes_site.site_is_general_paediatric_centre is False
    assert addenbrookes_site.case == case

    assert gosh_site.organisation == GOSH
    assert gosh_site.site_is_primary_centre_of_epilepsy_care is False
    assert gosh_site.site_is_actively_involved_in_epilepsy_care is True
    assert gosh_site.site_is_general_paediatric_centre is True
    assert gosh_site.case == case
