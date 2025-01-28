import pytest
import nhs_number

from django.urls import reverse

from epilepsy12.models import (
    Epilepsy12User,
    Case,
    Organisation
)
from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_LEAD_CLINICIAN,
    RCPCH_AUDIT_TEAM,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)


@pytest.mark.django_db
def test_jersey_patients_cant_have_nhs_number(client, seed_groups_fixture, seed_users_fixture):
    JERSEY = Organisation.objects.get(ods_code="RGT1W")

    test_user = Epilepsy12User.objects.filter(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        organisation_employer__id=JERSEY.id
    ).first()

    client.force_login(test_user)
    twofactor_signin(client, test_user=test_user)

    case_count_before = Case.objects.count()

    resp = client.post(
        reverse("create_case", kwargs={
            "organisation_id": test_user.organisation_employer.id
        }),
        {
            "first_name": "First",
            "surname": "Patient",
            "date_of_birth": "2008-03-20",
            "sex": 0,
            "postcode": "JE2 3WR",
            "nhs_number": nhs_number.generate(),
            "ethnicity": "A"
        }
    )

    messages = [str(message) for message in resp.context["messages"]]
    
    assert "It was not possible to save the case: unique_reference_number: This field is required." in messages
    assert Case.objects.count() == case_count_before


@pytest.mark.django_db
def test_mainland_patients_cant_have_urn(client, seed_groups_fixture, seed_users_fixture):
    KINGS = Organisation.objects.get(ods_code="RJZ01")

    test_user = Epilepsy12User.objects.filter(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        organisation_employer__id=KINGS.id
    ).first()

    client.force_login(test_user)
    twofactor_signin(client, test_user=test_user)

    case_count_before = Case.objects.count()

    resp = client.post(
        reverse("create_case", kwargs={
            "organisation_id": test_user.organisation_employer.id
        }),
        {
            "first_name": "First",
            "surname": "Patient",
            "date_of_birth": "2008-03-20",
            "sex": 0,
            "postcode": "WC1X 8SH",
            "unique_reference_number": "abcdef1234",
            "ethnicity": "A"
        }
    )

    messages = [str(message) for message in resp.context["messages"]]
    
    assert "It was not possible to save the case: nhs_number: This field is required." in messages
    assert Case.objects.count() == case_count_before


@pytest.mark.django_db
def test_mix_of_mainland_and_jersey_patients(client, seed_groups_fixture, seed_users_fixture):
    KINGS = Organisation.objects.get(ods_code="RJZ01")
    JERSEY = Organisation.objects.get(ods_code="RGT1W")

    test_user = Epilepsy12User.objects.filter(role=RCPCH_AUDIT_TEAM).first()

    client.force_login(test_user)
    twofactor_signin(client, test_user=test_user)

    case_count_before = Case.objects.count()

    client.post(
        reverse("create_case", kwargs={
            "organisation_id": KINGS.id
        }),
        {
            "first_name": "First",
            "surname": "Patient",
            "date_of_birth": "2008-03-20",
            "sex": 0,
            "postcode": "WC1X 8SH",
            "nhs_number": nhs_number.generate(),
            "ethnicity": "A"
        }
    )

    client.post(
        reverse("create_case", kwargs={
            "organisation_id": JERSEY.id
        }),
        {
            "first_name": "Second",
            "surname": "Patient",
            "date_of_birth": "2008-03-20",
            "sex": 0,
            "postcode": "JE2 3WR",
            "unique_reference_number": "abcdef1234",
            "ethnicity": "A"
        }
    )

    assert Case.objects.count() == (case_count_before + 2)


# https://github.com/rcpch/rcpch-audit-engine/issues/1190
@pytest.mark.django_db
def test_create_two_patients(client, seed_groups_fixture, seed_users_fixture):
    KINGS = Organisation.objects.get(ods_code="RJZ01")

    test_user = Epilepsy12User.objects.filter(
        role=AUDIT_CENTRE_LEAD_CLINICIAN,
        organisation_employer__id=KINGS.id
    ).first()

    client.force_login(test_user)
    twofactor_signin(client, test_user=test_user)

    case_count_before = Case.objects.count()

    resp = client.post(
        reverse("create_case", kwargs={
            "organisation_id": test_user.organisation_employer.id
        }),
        {
            "first_name": "First",
            "surname": "Patient",
            "date_of_birth": "2008-03-20",
            "sex": 0,
            "postcode": "WC1X 8SH",
            "nhs_number": nhs_number.generate(),
            "ethnicity": "A"
        }
    )

    assert Case.objects.count() == (case_count_before + 1)

    resp = client.post(
        reverse("create_case", kwargs={
            "organisation_id": test_user.organisation_employer.id
        }),
        {
            "first_name": "Second",
            "surname": "Patient",
            "date_of_birth": "2008-04-20",
            "sex": 0,
            "postcode": "WC1X 8SH",
            "nhs_number": nhs_number.generate(),
            "ethnicity": "A"
        }
    )

    assert Case.objects.count() == (case_count_before + 2)