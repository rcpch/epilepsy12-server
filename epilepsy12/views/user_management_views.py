from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.urls import reverse
from django.contrib.gis.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail, BadHeaderError

from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.html import strip_tags

# 3rd party
from django_htmx.http import HttpResponseClientRedirect
import pandas as pd

# epilepsy12
from ..models import Epilepsy12User, Organisation, VisitActivity
from epilepsy12.forms_folder.epilepsy12_user_form import Epilepsy12UserAdminCreationForm
from ..general_functions import construct_confirm_email, match_in_choice_key
from ..common_view_functions import group_for_role
from ..decorator import (
    user_may_view_this_organisation,
    user_can_access_user,
    login_and_otp_required,
)
from ..constants import (
    RCPCH_AUDIT_TEAM_ROLES,
    AUDIT_CENTRE_ROLES,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
)

from epilepsy12.forms_folder.epilepsy12_user_form import (
    #     Epilepsy12UserCreationForm,
    Epilepsy12LoginForm,
)


# def epilepsy12_login(request):
#     """
#     Callback from the login form
#     """
#     if request.method == "POST":
#         form = Epilepsy12LoginForm(request, data=request.POST)

#         if form.is_valid():
#             email = form.cleaned_data.get("username")
#             password = form.cleaned_data.get("password")

#             user = authenticate(request, username=email, password=password)

#             if user is not None:
#                 if user.organisation_employer is not None:
#                     # select the first hospital in the list if no allocated employing hospital
#                     selected_organisation = Organisation.objects.get(
#                         name=user.organisation_employer
#                     )
#                 else:
#                     selected_organisation = Organisation.objects.first()
#                 if user.email_confirmed == False:
#                     user.email_confirmed = True
#                     user.save()
#                 login(request, user)
#                 last_logged_in = VisitActivity.objects.filter(
#                     activity=1, epilepsy12user=user
#                 ).order_by("-activity_datetime")[:2]
#                 if last_logged_in.count() > 1:
#                     messages.info(
#                         request,
#                         f"You are now logged in as {email}. You last logged in at {timezone.localtime(last_logged_in[1].activity_datetime).strftime('%H:%M %p on %A, %d %B %Y')} from {last_logged_in[1].ip_address}",
#                     )
#                 else:
#                     messages.info(
#                         request,
#                         f"You are now logged in as {email}. Welcome to Epilepsy12! This is your first time logging in ({timezone.localtime(last_logged_in[0].activity_datetime).strftime('%H:%M %p on %A, %d %B %Y')} from {last_logged_in[0].ip_address}).",
#                     )

#                     if request.user.organisation_employer is not None:
#                         # current user is affiliated with an existing organisation - set viewable trust to this
#                         selected_organisation = Organisation.objects.get(
#                             name=request.user.organisation_employer
#                         )
#                     else:
#                         # current user is a member of the RCPCH audit team and also not affiliated with a organisation
#                         # therefore set selected organisation to first of organisation on the list
#                         selected_organisation = Organisation.objects.order_by(
#                             "name"
#                         ).first()
#                 return redirect(
#                     "selected_organisation_summary",
#                     organisation_id=selected_organisation.pk,
#                 )
#             else:
#                 messages.error(request, "Invalid email or password.")
#         else:
#             messages.error(request, "Invalid email or password.")
#     form = Epilepsy12LoginForm()
#     return render(
#         request=request, template_name="registration/login.html", context={"form": form}
#     )


@login_and_otp_required()
@user_may_view_this_organisation()
def epilepsy12_user_list(request, organisation_id):
    """
    Returns the list of users for the selected organisations
    Currently this includes RCPCH staff who are not associated with a organisation, though this breaks the update/delete and cancel
    buttons.
    """

    # get currently selected organisation
    organisation = Organisation.objects.get(pk=organisation_id)

    sort_flag = None

    filter_term = request.GET.get("filtered_epilepsy12_user_list")

    # get all organisations which are in the same parent trust
    organisation_children = Organisation.objects.filter(trust=organisation.trust).all()

    if filter_term:
        filter_term_Q = (
            Q(first_name__icontains=filter_term)
            | Q(surname__icontains=filter_term)
            | Q(organisation_employer__name__icontains=filter_term)
            | Q(email__icontains=filter_term)
        )

        # filter_term is called if filtering by search box
        if request.user.view_preference == 0:
            # user has requested organisation level view
            basic_filter = Q(organisation_employer__name__icontains=organisation.name)
        elif request.user.view_preference == 1:
            # user has requested trust level view
            if organisation.country.boundary_identifier == "W92000004":
                parent_trust = organisation.organisation.local_health_board.name
            else:
                parent_trust = organisation.organisation.trust.name
            basic_filter = Q(organisation_employer__name__icontains=parent_trust)
        elif request.user.view_preference == 2:
            # user has requested national level view
            basic_filter = None

        if basic_filter:
            # the basic filter filters users based on the selected organisation view
            # the filter_term_Q filters based on what the user has put in the search box
            if (
                request.user.is_rcpch_staff
                or request.user.is_rcpch_audit_team_member
                or request.user.is_superuser
            ):
                # user is RCPCH or E12 audit staff so can see RCPCH staff also
                # who will not be affiliated with any organisation
                epilepsy12_user_list = (
                    Epilepsy12User.objects.filter(
                        basic_filter
                        | Q(organisation_employer__isnull=True) & filter_term_Q
                    )
                    .order_by("surname")
                    .all()
                )
            else:
                # These are non RCPCH staff / not superusers
                epilepsy12_user_list = (
                    Epilepsy12User.objects.filter(basic_filter & filter_term_Q)
                    .order_by("surname")
                    .all()
                )
        else:
            # national view
            epilepsy12_user_list = (
                Epilepsy12User.objects.filter(filter_term_Q).order_by("surname").all()
            )

    else:
        """
        Epilepsy12Users are filtered based on user preference (request.user.view_preference), where 0 is organisation level,
        1 is trust level and 2 is national level
        Only RCPCH audit staff have this final option.
        """
        if request.user.view_preference == 2:
            # this is an RCPCH audit team member requesting National level
            # No filter requirements - see all users, including those with no trust affiliation
            basic_filter = None

        elif request.user.view_preference == 1:
            # filters all primary Trust level centres, irrespective of if active or inactive
            if organisation.country.boundary_identifier == "W92000004":
                parent_trust = organisation.local_health_board.name
            else:
                parent_trust = organisation.trust.name

            basic_filter = Q(organisation_employer__trust__name__contains=parent_trust)

        elif request.user.view_preference == 0:
            # filters all primary centres at organisation level, irrespective of if active or inactive
            basic_filter = Q(organisation_employer__name__contains=organisation.name)
        else:
            raise Exception("No View Preference supplied")

        if (
            request.user.is_rcpch_staff
            or request.user.is_rcpch_audit_team_member
            or request.user.is_superuser
        ):
            if basic_filter:
                # organisational or trust view
                filtered_epilepsy12_users = (
                    Epilepsy12User.objects.filter(
                        basic_filter | Q(organisation_employer__isnull=True)
                    )
                    .order_by("surname")
                    .all()
                )
            else:
                # national view
                filtered_epilepsy12_users = (
                    Epilepsy12User.objects.filter().order_by("surname").all()
                )
        else:
            # not RCPCH staff or superusers
            if basic_filter:
                # organisation or trust view
                filtered_epilepsy12_users = (
                    Epilepsy12User.objects.filter(basic_filter)
                    .order_by("surname")
                    .all()
                )
            else:
                # national view
                filtered_epilepsy12_users = (
                    Epilepsy12User.objects.filter().order_by("surname").all()
                )

        if (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_name_up"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_name_up"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("surname").all()
            sort_flag = "sort_epilepsy12_users_by_name_up"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_name_down"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_name_down"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("-surname").all()
            sort_flag = "sort_epilepsy12_users_by_name_down"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_email_up"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_email_up"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("surname").all()
            sort_flag = "sort_epilepsy12_users_by_email_up"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_email_down"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_email_down"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("-surname").all()
            sort_flag = "sort_epilepsy12_users_by_email_down"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_role_up"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_role_up"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("role").all()
            sort_flag = "sort_epilepsy12_users_by_role_up"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_role_down"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_role_down"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("-role").all()
            sort_flag = "sort_epilepsy12_users_by_role_down"
        elif (
            request.htmx.trigger_name
            == "sort_epilepsy12_users_by_organisation_employer_up"
            or request.GET.get("sort_flag")
            == "sort_epilepsy12_users_by_organisation_employer_up"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                "organisation_employer"
            ).all()
            sort_flag = "sort_epilepsy12_users_by_organisation_employer_up"
        elif (
            request.htmx.trigger_name
            == "sort_epilepsy12_users_by_organisation_employer_down"
            or request.GET.get("sort_flag")
            == "sort_epilepsy12_users_by_organisation_employer_down"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                "-organisation_employer"
            ).all()
            sort_flag = "sort_epilepsy12_users_by_organisation_employer_down"
        else:
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("surname").all()

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
            (0, f"Organisation level ({organisation.name})"),
            (1, f"Trust level ({parent_trust})"),
            (2, "National level"),
        )
    else:
        rcpch_choices = (
            (0, f"Organisation level ({organisation.name})"),
            (1, f"Trust level ({parent_trust})"),
        )

    paginator = Paginator(epilepsy12_user_list, 10)
    page_number = request.GET.get("page", 1)
    epilepsy12_user_list = paginator.page(page_number)

    context = {
        "epilepsy12_user_list": epilepsy12_user_list,
        "rcpch_choices": rcpch_choices,
        "organisation": organisation,
        "organisation_children": organisation_children,
        "sort_flag": sort_flag,
    }

    if request.htmx:
        template_name = "registration/user_management/epilepsy12_user_table.html"
        return render(request=request, template_name=template_name, context=context)

    template_name = "registration/user_management/epilepsy12_user_list.html"

    return render(request=request, template_name=template_name, context=context)


@login_and_otp_required()
@user_may_view_this_organisation()
@permission_required("epilepsy12.add_epilepsy12user", raise_exception=True)
def create_epilepsy12_user(request, organisation_id, user_type, epilepsy12_user_id):
    """
    Creates an epilepsy12 user. It is called from epilepsy12 list of users
    If from the create epilepsy12 user button, the originating organisation is added to
    the saved user. If from the create rcpch-staff button, the originating organisation is removed.
    """
    organisation = Organisation.objects.get(pk=organisation_id)
    if user_type == "organisation-staff":
        admin_title = "Add Epilepsy12 User"
        prepopulated_data = {
            "organisation_employer": organisation,
        }
        form = Epilepsy12UserAdminCreationForm(
            rcpch_organisation=user_type, initial=prepopulated_data
        )
    elif user_type == "rcpch-staff":
        admin_title = "Add RCPCH Epilepsy12 staff member"
        form = Epilepsy12UserAdminCreationForm(
            rcpch_organisation=user_type, initial=None
        )

    if request.method == "POST":
        form = Epilepsy12UserAdminCreationForm(
            user_type,
            request.POST or None,
        )

        if form.is_valid():
            # success message - return to user list
            new_user = form.save(commit=False)
            new_user.set_unusable_password()
            new_user.is_active = True
            new_user.email_confirmed = False
            new_user.view_preference = 0
            new_user.save()

            new_group = group_for_role(new_user.role)
            new_user.groups.add(new_group)

            # user created - send email with reset link to new user
            subject = "Password Reset Requested"
            email = construct_confirm_email(request=request, user=new_user)
            try:
                send_mail(
                    subject=subject,
                    from_email="admin@epilepsy12.rcpch.tech",
                    recipient_list=[new_user.email],
                    fail_silently=False,
                    message=strip_tags(email),
                    html_message=email,
                )
            except BadHeaderError:
                return HttpResponse("Invalid header found.")

            messages.success(request, f"{new_user.email} account created successfully.")
            return redirect(
                "epilepsy12_user_list",
                organisation_id=organisation_id,
            )

    context = {
        "form": form,
        "organisation_id": organisation_id,
        "admin_title": admin_title,
        "user_type": user_type,
    }

    return render(
        request=request,
        template_name="registration/admin_create_user.html",
        context=context,
    )


@login_and_otp_required()
@user_may_view_this_organisation()
@user_can_access_user()
@permission_required("epilepsy12.change_epilepsy12user", raise_exception=True)
def edit_epilepsy12_user(request, organisation_id, epilepsy12_user_id):
    """
    Django model form to edit/update Epilepsy12user
    """

    organisation = Organisation.objects.get(pk=organisation_id)
    epilepsy12_user_to_edit = get_object_or_404(Epilepsy12User, pk=epilepsy12_user_id)
    can_edit = False
    if (
        request.user.is_rcpch_staff
        or request.user.organisation_employer == organisation
        or request.user.is_rcpch_audit_team_member
    ):
        can_edit = True
    if match_in_choice_key(AUDIT_CENTRE_ROLES, epilepsy12_user_to_edit.role):
        user_type = "organisation-staff"
    elif match_in_choice_key(RCPCH_AUDIT_TEAM_ROLES, epilepsy12_user_to_edit.role):
        user_type = "rcpch-staff"
    if can_edit:
        form = Epilepsy12UserAdminCreationForm(
            user_type,
            request.POST or None,
            instance=epilepsy12_user_to_edit,
        )
    else:
        return HttpResponseForbidden()

    if request.method == "POST":
        if "delete" in request.POST:
            epilepsy12_user_to_edit.delete()
            messages.success(
                request, f"{epilepsy12_user_to_edit.email} Deleted successfully."
            )
            redirect_url = reverse(
                "epilepsy12_user_list", kwargs={"organisation_id": organisation_id}
            )
            return redirect(redirect_url)
        if "cancel" in request.POST:
            redirect_url = reverse(
                "epilepsy12_user_list", kwargs={"organisation_id": organisation_id}
            )
            return redirect(redirect_url)
        if "resend" in request.POST:
            # send email with reset link to new user
            subject = "Password Reset Requested"
            email = construct_confirm_email(
                request=request, user=epilepsy12_user_to_edit
            )
            try:
                send_mail(
                    subject=subject,
                    from_email="admin@epilepsy12.rcpch.tech",
                    recipient_list=[epilepsy12_user_to_edit.email],
                    fail_silently=False,
                    message=strip_tags(email),
                    html_message=email,
                )
            except BadHeaderError:
                return HttpResponse("Invalid header found.")

            messages.success(
                request,
                f"Confirmation request sent to {epilepsy12_user_to_edit.email}.",
            )
            redirect_url = reverse(
                "epilepsy12_user_list",
                kwargs={
                    "organisation_id": organisation_id,
                },
            )
            return redirect(redirect_url)

        else:
            if form.is_valid():
                # this will not include the password which will be empty
                new_user = form.save()

                # update group
                new_group = group_for_role(new_user.role)
                new_user.groups.clear()
                new_user.groups.add(new_group)

                # adds success message
                messages.success(
                    request,
                    f"You have successfully updated {epilepsy12_user_to_edit}'s details",
                )

                # Save was successful, so redirect to another page
                redirect_url = reverse(
                    "epilepsy12_user_list", kwargs={"organisation_id": organisation_id, }
                )
                return redirect(redirect_url)

    template_name = "registration/admin_create_user.html"

    if epilepsy12_user_to_edit.is_rcpch_staff:
        admin_title = "Edit RCPCH Epilepsy12 staff member"
        user_type = "rcpch-staff"
    else:
        admin_title = "Edit Epilepsy12 User"
        user_type = "organisation-staff"

    return render(
        request,
        template_name,
        {
            "organisation_id": organisation_id,
            "form": form,
            "admin_title": admin_title,
            "user_type": user_type,
        },
    )


@login_and_otp_required()
@user_may_view_this_organisation()
@user_can_access_user()
@permission_required("epilepsy12.delete_epilepsy12user", raise_exception=True)
def delete_epilepsy12_user(request, organisation_id, epilepsy12_user_id):
    try:
        Epilepsy12User.objects.get(pk=epilepsy12_user_id).delete()
    except ValueError as error:
        messages.error(request, f"Delete User Unsuccessful: {error}")

    return HttpResponseClientRedirect(
        reverse(
            "epilepsy12_user_list",
            kwargs={
                "organisation_id": organisation_id,
            },
        )
    )


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "registration/password_reset.html"
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("index")


@login_and_otp_required()
@user_can_access_user()
def logs(request, organisation_id, epilepsy12_user_id):
    """
    returns logs for given organisation
    """
    organisation = Organisation.objects.get(pk=organisation_id)
    epilepsy12_user = Epilepsy12User.objects.get(pk=epilepsy12_user_id)

    activities = VisitActivity.objects.filter(epilepsy12user=epilepsy12_user).all()

    template_name = "epilepsy12/logs.html"
    context = {
        "epilepsy12_user": epilepsy12_user,
        "organisation": organisation,
        "activities": activities,
    }

    return render(request=request, template_name=template_name, context=context)


@login_and_otp_required()
@user_can_access_user()
def log_list(request, organisation_id, epilepsy12_user_id):
    """
    GET request to return log table
    """
    organisation = Organisation.objects.get(pk=organisation_id)
    epilepsy12_user = Epilepsy12User.objects.get(pk=epilepsy12_user_id)

    activities = VisitActivity.objects.filter(epilepsy12user=epilepsy12_user).all()

    template_name = "epilepsy12/logs.html"
    context = {
        "epilepsy12_user": epilepsy12_user,
        "organisation": organisation,
        "activities": activities,
    }

    return render(request=request, template_name=template_name, context=context)


@login_and_otp_required()
@user_may_view_this_organisation()
def all_epilepsy12_users_list(request, organisation_id):
    allowed_groups = [EPILEPSY12_AUDIT_TEAM_FULL_ACCESS]

    if not (
        request.user.is_superuser or request.user.groups.filter(name__in=allowed_groups)
    ):
        raise PermissionDenied()

    all_users = Epilepsy12User.objects.all().values(
        "id",
        "last_login",
        "first_name",
        "last_name",
        "email",
        "organisation_employer",
        "is_active",
        "is_staff",
        "is_superuser",
        "is_rcpch_audit_team_member",
        "is_rcpch_staff",
        "is_patient_or_carer",
        "date_joined",
        "role",
        "email_confirmed",
    )

    df = pd.DataFrame(all_users)

    # Convert DataFrame to CSV format
    csv_data = df.to_csv(index=False)

    # Create an HTTP response with the CSV data
    response = HttpResponse(csv_data, content_type="text/csv")

    response["Content-Disposition"] = 'attachment; filename="epilepsy12users.csv"'

    return response
