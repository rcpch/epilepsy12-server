import pytest
import nhs_number

from django.urls import reverse

from epilepsy12.models import Epilepsy12User, Case
from epilepsy12.tests.UserDataClasses import (
    test_user_rcpch_audit_team_data,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)

# https://github.com/rcpch/rcpch-audit-engine/issues/1190
@pytest.mark.django_db
def test_create_two_patients(client, seed_groups_fixture, seed_users_fixture):
    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )

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