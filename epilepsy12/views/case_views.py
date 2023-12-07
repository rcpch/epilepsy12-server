# python imports
from datetime import datetime

# django imports
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib.gis.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import DatabaseError

# third party imports
from django_htmx.http import trigger_client_event, HttpResponseClientRedirect

# RCPCH imports
from epilepsy12.forms import CaseForm
from epilepsy12.models import Organisation, Site, Case, AuditProgress, Epilepsy12User
from ..constants import (
    UNKNOWN_POSTCODES_NO_SPACES,
)
from ..decorator import (
    user_may_view_this_organisation,
    user_may_view_this_child,
    login_and_otp_required,
)

from django.conf import settings

from ..general_functions import construct_transfer_epilepsy12_site_outcome_email
from ..tasks import asynchronously_send_email_to_recipients


@login_and_otp_required()
@user_may_view_this_organisation()
def case_list(request, organisation_id):
    """
    Returns a list of all children registered under the user's service.
    Path is protected to those logged in only
    Params:
    request.user

    If the user is a clinician / centre lead, only the children under their care are seen (whether registered or not)
    If the user is an audit administrator, they have can view all cases in the audit, but cannot edit
    If the user is a superuser, they can view and edit all cases in the audit (but with great power comes great responsibility)

    """

    sort_flag = None

    filter_term = request.GET.get("filtered_case_list")

    # get currently selected organisation
    organisation = Organisation.objects.get(pk=organisation_id)

    # get all organisations which are in the same parent trust
    organisation_children = Organisation.objects.filter(trust=organisation.trust).all()

    if filter_term:
        # filter_term is called if filtering by search box
        if request.user.view_preference == 0:
            # user has requested organisation level view
            all_cases = (
                Case.objects.filter(
                    Q(site__organisation__name__contains=organisation.name)
                    & Q(site__site_is_primary_centre_of_epilepsy_care=True)
                    & Q(site__site_is_actively_involved_in_epilepsy_care=True)
                    & (
                        Q(first_name__icontains=filter_term)
                        | Q(surname__icontains=filter_term)
                        | Q(nhs_number__icontains=filter_term)
                    )
                )
                .order_by("surname")
                .all()
            )
        elif request.user.view_preference == 1:
            # user has requested trust level view
            all_cases = (
                Case.objects.filter(
                    Q(
                        site__organisation__trust__ods_code__contains=organisation.trust__ods_code
                    )
                    & Q(site__site_is_primary_centre_of_epilepsy_care=True)
                    & Q(site__site_is_actively_involved_in_epilepsy_care=True)
                    & (
                        Q(first_name__icontains=filter_term)
                        | Q(surname__icontains=filter_term)
                        | Q(nhs_number__icontains=filter_term)
                    )
                )
                .order_by("surname")
                .all()
            )
        elif request.user.view_preference == 2:
            # user has requested national level view
            all_cases = (
                Case.objects.filter(
                    Q(site__site_is_primary_centre_of_epilepsy_care=True)
                    & Q(site__site_is_actively_involved_in_epilepsy_care=True)
                    & (
                        Q(first_name__icontains=filter_term)
                        | Q(surname__icontains=filter_term)
                        | Q(nhs_number__icontains=filter_term)
                    )
                )
                .order_by("surname")
                .all()
            )

    else:
        """
        Cases are filtered based on user preference (request.user.view_preference), where 0 is organisation level,
        1 is trust level and 2 is national level
        Only RCPCH audit staff have this final option.
        """

        if request.user.view_preference == 2:
            # this is an RCPCH audit team member requesting National level
            filtered_cases = Case.objects.all()
        elif request.user.view_preference == 1:
            # filters all primary Trust level centres, irrespective of if active or inactive
            filtered_cases = Case.objects.filter(
                organisations__trust__name__contains=organisation.trust.name,
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
            )
        else:
            # filters all primary centres at organisation level, irrespective of if active or inactive
            filtered_cases = Case.objects.filter(
                organisations__name__contains=organisation.name,
                site__site_is_primary_centre_of_epilepsy_care=True,
                site__site_is_actively_involved_in_epilepsy_care=True,
            )

        if (
            request.htmx.trigger_name == "sort_by_nhs_number_up"
            or request.GET.get("sort_flag") == "sort_by_nhs_number_up"
        ):
            all_cases = filtered_cases.order_by("nhs_number").all()
            sort_flag = "sort_by_nhs_number_up"
        elif (
            request.htmx.trigger_name == "sort_by_nhs_number_down"
            or request.GET.get("sort_flag") == "sort_by_nhs_number_down"
        ):
            all_cases = filtered_cases.order_by("-nhs_number").all()
            sort_flag = "sort_by_nhs_number_down"
        elif (
            request.htmx.trigger_name == "sort_by_ethnicity_up"
            or request.GET.get("sort_flag") == "sort_by_ethnicity_up"
        ):
            all_cases = filtered_cases.order_by("ethnicity").all()
            sort_flag = "sort_by_ethnicity_up"
        elif (
            request.htmx.trigger_name == "sort_by_ethnicity_down"
            or request.GET.get("sort_flag") == "sort_by_ethnicity_down"
        ):
            all_cases = filtered_cases.order_by("-ethnicity").all()
            sort_flag = "sort_by_ethnicity_down"
        elif (
            request.htmx.trigger_name == "sort_by_sex_up"
            or request.GET.get("sort_flag") == "sort_by_sex_up"
        ):
            all_cases = filtered_cases.order_by("sex").all()
            sort_flag = "sort_by_sex_up"
        elif (
            request.htmx.trigger_name == "sort_by_sex_down"
            or request.GET.get("sort_flag") == "sort_by_sex_down"
        ):
            all_cases = filtered_cases.order_by("-sex").all()
            sort_flag = "sort_by_sex_down"
        elif (
            request.htmx.trigger_name == "sort_by_name_up"
            or request.GET.get("sort_flag") == "sort_by_name_up"
        ):
            all_cases = filtered_cases.order_by("surname").all()
            sort_flag = "sort_by_name_up"
        elif (
            request.htmx.trigger_name == "sort_by_name_down"
            or request.GET.get("sort_flag") == "sort_by_name_down"
        ):
            all_cases = filtered_cases.order_by("-surname").all()
            sort_flag = "sort_by_name_down"
        elif (
            request.htmx.trigger_name == "sort_by_id_up"
            or request.GET.get("sort_flag") == "sort_by_id_up"
        ):
            all_cases = filtered_cases.order_by("id").all()
            sort_flag = "sort_by_id_up"
        elif (
            request.htmx.trigger_name == "sort_by_id_down"
            or request.GET.get("sort_flag") == "sort_by_id_down"
        ):
            all_cases = filtered_cases.order_by("-id").all()
            sort_flag = "sort_by_id_down"
        elif (
            request.htmx.trigger_name == "sort_by_deadline_up"
            or request.GET.get("sort_flag") == "sort_by_deadline_up"
        ):
            all_cases = filtered_cases.order_by(
                "registration__audit_submission_date"
            ).all()
            sort_flag = "sort_by_deadline_up"
        elif (
            request.htmx.trigger_name == "sort_by_deadline_down"
            or request.GET.get("sort_flag") == "sort_by_deadline_down"
        ):
            all_cases = filtered_cases.order_by(
                "-registration__audit_submission_date"
            ).all()
            sort_flag = "sort_by_deadline_down"
        elif (
            request.htmx.trigger_name == "sort_by_cohort_up"
            or request.GET.get("sort_flag") == "sort_by_cohort_up"
        ):
            all_cases = filtered_cases.order_by("registration__cohort").all()
            sort_flag = "sort_by_cohort_up"
        elif (
            request.htmx.trigger_name == "sort_by_cohort_down"
            or request.GET.get("sort_flag") == "sort_by_cohort_down"
        ):
            all_cases = filtered_cases.order_by("-registration__cohort").all()
            sort_flag = "sort_by_cohort_down"
        elif (
            request.htmx.trigger_name == "sort_by_days_remaining_up"
            or request.GET.get("sort_flag") == "sort_by_days_remaining_up"
        ):
            all_cases = filtered_cases.order_by(
                "registration__days_remaining_before_submission"
            ).all()
            sort_flag = "sort_by_days_remaining_before_submission_up"
        elif (
            request.htmx.trigger_name == "sort_by_days_remaining_before_submission_down"
            or request.GET.get("sort_flag")
            == "sort_by_days_remaining_before_submission_down"
        ):
            all_cases = filtered_cases.order_by(
                "-registration__days_remaining_before_submission"
            ).all()
            sort_flag = "sort_by_days_remaining_before_submission_down"
        else:
            all_cases = filtered_cases.order_by("surname").all()

    registered_cases = all_cases.filter(
        ~Q(registration__isnull=True)
        & Q(site__site_is_primary_centre_of_epilepsy_care=True)
        & Q(site__site_is_actively_involved_in_epilepsy_care=True)
    ).all()

    cases_in_transfer = registered_cases.filter(site__active_transfer=True)

    paginator = Paginator(all_cases, 10)
    page_number = request.GET.get("page", 1)
    case_list = paginator.page(page_number)

    case_count = all_cases.count()
    registered_count = registered_cases.count()

    if organisation.country.boundary_identifier == "W92000004":
        parent_trust = organisation.local_health_board.name
    else:
        parent_trust = organisation.trust.name

    if (
        request.user.is_rcpch_audit_team_member
        or request.user.is_rcpch_staff
        or request.user.is_superuser
    ):
        rcpch_choices = (
            (0, "Organisation level"),
            (1, "Trust level"),
            (2, "National level"),
        )
    else:
        rcpch_choices = (
            (0, "Organisation level"),
            (1, "Trust level"),
        )

    context = {
        "case_list": case_list,
        "total_cases": case_count,
        "total_registrations": registered_count,
        "sort_flag": sort_flag,
        "organisation": organisation,
        "organisation_children": organisation_children,
        "rcpch_choices": rcpch_choices,
        "organisation_id": organisation_id,
        "cases_in_transfer": cases_in_transfer,
    }
    if request.htmx:
        return render(
            request=request,
            template_name="epilepsy12/partials/case_table.html",
            context=context,
        )

    template_name = "epilepsy12/cases/cases.html"
    return render(request, template_name, context)


@login_and_otp_required()
@user_may_view_this_organisation()
def case_statistics(request, organisation_id):
    """
    GET request from cases template to update stats on toggle between RCPCH view and Organisation level
    """

    organisation = Organisation.objects.get(pk=organisation_id)

    if request.user.view_preference == 2:
        # user requesting National level - return all cases in the UK
        total_cases = Case.objects.all()
    elif request.user.view_preference == 1:
        # user requesting Trust level - return all cases in the same trust
        total_cases = Case.objects.filter(
            Q(organisations__trust__name__contains=organisation.trust.name)
        )
    elif request.user.view_preference == 0:
        # user requesting Trust level - return all cases in the same organisation
        total_cases = Case.objects.filter(
            Q(organisations__name__contains=organisation.name)
        )

    registered_cases = total_cases.filter(
        ~Q(registration__isnull=True),
    ).all()

    context = {
        "total_cases": total_cases.count(),
        "total_registrations": registered_cases.count(),
        "organisation": organisation,
    }

    response = render(
        request,
        template_name="epilepsy12/partials/cases/case_statistics.html",
        context=context,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required(
    "epilepsy12.can_transfer_epilepsy12_lead_centre", raise_exception=True
)
def transfer_response(request, organisation_id, case_id, organisation_response):
    """
    POST callback from case table on click of accept/reject buttons against transfer request
    Updates associated Site instance and redirects back to case table
    """

    case = Case.objects.get(pk=case_id)
    site = Site.objects.get(case=case, active_transfer=True)
    # prepare email response to requesting organisation clinical lead
    email = construct_transfer_epilepsy12_site_outcome_email(
        request=request,
        target_organisation=Organisation.objects.get(pk=organisation_id),
        outcome=f"{organisation_response}ed",
    )
    origin_organisation = site.transfer_origin_organisation
    if organisation_response == "reject":
        # reset the child back to the orgin organisation
        site.active_transfer = False
        site.organisation = site.transfer_origin_organisation
        site.transfer_origin_organisation = None
        site.transfer_request_date = None
    elif organisation_response == "accept":
        site.active_transfer = False
        site.transfer_origin_organisation = None
        site.transfer_request_date = None
    else:
        raise Exception("No organisation response supplied")

    try:
        site.save()
    except:
        raise DatabaseError

    # send email asynchronously to lead clinician(s) of origin organisation notifying them of outcome
    outcome = f"{organisation_response.upper()}ED"
    if Epilepsy12User.objects.filter(
        (
            Q(organisation_employer=origin_organisation)
            & Q(is_active=True)
            & Q(role=1)  # Audit Centre Lead Clinician
        )
    ).exists():
        recipients = list(
            Epilepsy12User.objects.filter(
                (
                    Q(organisation_employer=origin_organisation)
                    & Q(is_active=True)
                    & Q(role=1)  # Audit Centre Lead Clinician
                )
            ).values_list("email", flat=True)
        )
        subject = f"Epilepsy12 Lead Site Transfer {outcome}"
    else:
        recipients = [settings.SITE_CONTACT_EMAIL]
        subject = f"Epilepsy12 Lead Site Transfer {outcome}  - NO LEAD CLINICIAN"

    asynchronously_send_email_to_recipients.delay(
        recipients=recipients, subject=subject, message=email
    )

    return HttpResponseClientRedirect(
        reverse("cases", kwargs={"organisation_id": organisation_id})
    )


@login_and_otp_required()
@user_may_view_this_child()
@permission_required(
    "epilepsy12.change_case",
)
def case_submit(request, organisation_id, case_id):
    """
    POST request callback from submit button in case_list partial.
    Disables further editing of case information. Case considered submitted
    There is a specific permission both for locking and unlocking which is tested in this function
    """
    case = Case.objects.get(pk=case_id)
    if case.locked is True and request.user.has_perm(
        "epilepsy12.can_unlock_child_case_data_from_editing"
    ):
        case.locked = False
    elif case.locked is False and request.user.has_perm(
        "epilepsy12.can_lock_child_case_data_from_editing"
    ):
        case.locked = True
    else:
        raise PermissionDenied()
    case.save()

    return HttpResponseClientRedirect(
        reverse("cases", kwargs={"organisation_id": organisation_id})
    )


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.view_case")
def case_performance_summary(request, case_id):
    case = Case.objects.get(pk=case_id)
    site = Site.objects.filter(
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        case=case,
    ).get()
    organisation_id = site.organisation.pk

    context = {
        "case": case,
        "case_id": case.pk,
        "active_template": "case_performance_summary",
        "audit_progress": case.registration.audit_progress,
        "organisation_id": organisation_id,
    }

    template = "epilepsy12/case_performance_summary.html"

    response = render(request=request, template_name=template, context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response, name="registration_active", params={}
    )  # reloads the form to show the active steps

    return response


"""
Case function based views - class based views not chosen as need to accept organisation_id also in URL
"""


@login_and_otp_required()
@user_may_view_this_organisation()
@permission_required("epilepsy12.add_case")
def create_case(request, organisation_id):
    """
    Django function based - returns django form to create a new case, or saves a new case if a
    POST request. The only instance where htmx not used.
    """
    organisation = Organisation.objects.filter(pk=organisation_id).get()

    # set select boxes for situations when postcode unknown
    country_choice = ("ZZ993CZ", "Address unspecified - England")
    if organisation.country.boundary_identifier == "W92000004":
        country_choice = ("ZZ993GZ", "Address unspecified - Wales")

    choices = (
        ("ZZ993WZ", "Address unknown"),
        country_choice,
        ("ZZ993VZ", "No fixed abode"),
    )
    form = CaseForm(request.POST or None)

    template_name = "epilepsy12/cases/case.html"

    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_at = datetime.now()
            organisation = Organisation.objects.get(pk=organisation_id)
            # save the new child
            obj.save()
            # allocate the child to the organisation supplied as primary E12 centre
            Site.objects.create(
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_primary_centre_of_epilepsy_care=True,
                organisation=organisation,
                case=obj,
            )
            messages.success(request, "You successfully created the case")
            return redirect("cases", organisation_id=organisation_id)
        else:
            messages.error(
                request=request, message="It was not possible to save the case"
            )
            print("Invalid data")
            print(form.errors)

    context = {
        "organisation_id": organisation_id,
        "organisation": organisation,
        "form": form,
        "choices": choices,
        "child_has_unknown_postcode": False,
    }
    return render(request=request, template_name=template_name, context=context)


@login_and_otp_required()
@user_may_view_this_child()
@user_may_view_this_organisation()
@permission_required("epilepsy12.change_case", raise_exception=True)
def update_case(request, organisation_id, case_id):
    """
    Django function based view. Receives POST request to update view or delete
    """
    case = get_object_or_404(Case, pk=case_id)
    form = CaseForm(instance=case)

    organisation = Organisation.objects.filter(pk=organisation_id).get()

    # set select boxes for situations when postcode unknown
    country_choice = ("ZZ993CZ", "Address unspecified - England")
    if organisation.country.boundary_identifier == "W92000004":
        country_choice = ("ZZ993GZ", "Address unspecified - Wales")

    choices = (
        ("ZZ993WZ", "Address unknown"),
        country_choice,
        ("ZZ993VZ", "No fixed abode"),
    )

    if request.htmx:
        if not request.user.has_perm("epilepsy12.delete_case"):
            raise PermissionDenied()
        messages.success(request, f"You successfully deleted {case}'s details")
        case.delete()
        url = reverse("cases", kwargs={"organisation_id": organisation_id})
        return HttpResponseClientRedirect(redirect_to=url, status=200)

    if request.method == "POST":
        form = CaseForm(request.POST, instance=case)
        if form.is_valid():
            obj = form.save()
            if case.locked != obj.locked:
                # locked status has changed
                if form.locked:
                    obj.locked_by = request.user
                    obj.locked_at = datetime.now()
                else:
                    obj.locked_by = None
                    obj.locked_at = None
            obj.updated_at = (timezone.now(),)
            obj.updated_by = request.user
            obj.save()
            messages.success(request, f"You successfully updated {case}'s details")
            return redirect("cases", organisation_id=organisation_id)

    child_has_unknown_postcode = False
    test_positive = None
    if case.postcode in UNKNOWN_POSTCODES_NO_SPACES:
        child_has_unknown_postcode = True
        test_positive = case.postcode

    context = {
        "organisation_id": organisation_id,
        "organisation": organisation,
        "form": form,
        "case": case,
        "child_has_unknown_postcode": child_has_unknown_postcode,
        "test_positive": test_positive,
        "choices": choices,
    }

    return render(
        request=request, template_name="epilepsy12/cases/case.html", context=context
    )


@login_and_otp_required()
@user_may_view_this_organisation()
@permission_required("epilepsy12.change_case", raise_exception=True)
def unknown_postcode(request, organisation_id):
    """
    POST call back from single choice multiple select if postcode does not exist
    """
    test_positive = request.htmx.trigger_name

    organisation = Organisation.objects.get(pk=organisation_id)
    # set select boxes for situations when postcode unknown
    country_choice = ("ZZ993CZ", "Address unspecified - England")
    if organisation.country.boundary_identifier == "W92000004":
        country_choice = ("ZZ993GZ", "Address unspecified - Wales")

    choices = (
        ("ZZ993WZ", "Address unknown"),
        country_choice,
        ("ZZ993VZ", "No fixed abode"),
    )

    template_name = "epilepsy12/cases/unknown_postcode.html"
    context = {
        "choices": choices,
        "organisation_id": organisation_id,
        "test_positive": test_positive,
        "hide_completion_fields": True,
        "enabled": True,
    }
    return render(request=request, template_name=template_name, context=context)


@login_and_otp_required()
@user_may_view_this_child()
@permission_required(
    "epilepsy12.can_opt_out_child_from_inclusion_in_audit", raise_exception=True
)
def opt_out(request, organisation_id, case_id):
    """
    This child has opted out of Epilepsy12
    Their unique E12 ID will be retained but all associated fields will be set to None, and associated records deleted except their
    leading trust will be retained but set to inactive.
    """

    case = Case.objects.get(pk=case_id)
    messages.info(
        request,
        f"All data on {case} has been permanently removed from Epilepsy12. The Epilepsy12 unique identifier has been preserved to contribute to annual totals.",
    )
    case.nhs_number = None
    case.first_name = None
    case.surname = None
    case.sex = None
    case.date_of_birth = None
    case.postcode = None
    case.ethnicity = None
    case.locked = True

    case.save()

    # delete all related records - this should cascade to all tables
    if hasattr(case, "registration"):
        case.registration.delete()

    # delete all related sites except the primary centre of care, which becomes inactive
    all_sites = case.site.all()
    for site in all_sites:
        if site.site_is_primary_centre_of_epilepsy_care:
            site.site_is_actively_involved_in_epilepsy_care = False
            site.save()
        else:
            Site.objects.get(pk=site.pk).delete()

    return HttpResponseClientRedirect(
        reverse("cases", kwargs={"organisation_id": organisation_id})
    )


@login_and_otp_required()
@user_may_view_this_child()
@permission_required(
    "epilepsy12.can_consent_to_audit_participation", raise_exception=True
)
def consent(request, case_id):
    case = Case.objects.get(pk=case_id)
    site = Site.objects.filter(
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        case=case,
    ).get()
    organisation_id = site.organisation.pk

    context = {
        "case": case,
        "case_id": case.pk,
        "active_template": "consent",
        "audit_progress": case.registration.audit_progress,
        "organisation_id": organisation_id,
    }

    template = "epilepsy12/consent.html"

    response = render(request=request, template_name=template, context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response, name="registration_active", params={}
    )  # reloads the form to show the active steps

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required(
    "epilepsy12.can_consent_to_audit_participation", raise_exception=True
)
def consent_confirmation(request, case_id, consent_type):
    """
    POST request on click of confirm button in patient_confirmation.html template
    params: consent_type is one of 'consent', 'denied'
    """
    case = Case.objects.get(pk=case_id)
    site = Site.objects.filter(
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        case=case,
    ).get()
    organisation_id = site.organisation.pk
    has_error = False

    if consent_type == "consent":
        AuditProgress.objects.filter(pk=case.registration.audit_progress.pk).update(
            consent_patient_confirmed=True
        )
        case = Case.objects.get(pk=case_id)
    elif consent_type == "denied":
        AuditProgress.objects.filter(pk=case.registration.audit_progress.pk).update(
            consent_patient_confirmed=False
        )
        case = Case.objects.get(pk=case_id)
    else:
        # an error occurred
        has_error = True
        AuditProgress.objects.filter(pk=case.registration.audit_progress.pk).update(
            consent_patient_confirmed=None
        )
        case = Case.objects.get(pk=case_id)

    context = {
        "case": case,
        "case_id": case.pk,
        "active_template": "consent",
        "audit_progress": case.registration.audit_progress,
        "organisation_id": organisation_id,
        "has_error": has_error,
    }

    template = "epilepsy12/forms/consent_form.html"

    response = render(request=request, template_name=template, context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response, name="registration_active", params={}
    )  # reloads the form to show the active steps

    return response
