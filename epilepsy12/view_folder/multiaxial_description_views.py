from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from epilepsy12.models.desscribe import DESSCRIBE
from ..forms_folder import MultiaxialDescriptionForm

from epilepsy12.models.case import Case

from ..models import Registration
from ..general_functions import *


@login_required
def create_multiaxial_description(request, case_id):
    form = MultiaxialDescriptionForm(request.POST or None)
    case = Case.objects.get(id=case_id)
    registration = Registration.objects.filter(case=case_id).first()
    desscribe = DESSCRIBE.objects.filter(registration=registration).first()
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            registration = Registration.objects.filter(case=id)
            obj.registration = registration
            obj.save()
            return redirect('cases')
        else:
            print('not valid')

    context = {
        "desscribe": desscribe,
        "form": form,
        "registration": registration,
        "case_id": case_id,
        "case_name": case.first_name + " " + case.surname,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "multiaxial_description"
    }

    return render(request=request, template_name='epilepsy12/multiaxial_description.html', context=context)


@login_required
def update_multiaxial_description(request, case_id):
    # multiaxial_description_form = MultiaxialDescriptionForm.objects.filter(
    #     registration__case=id).first()
    registration = Registration.objects.filter(case=case_id).first()
    # form = MultiaxialDescriptionForm(instance=multiaxial_description_form)
    desscribe = DESSCRIBE.objects.filter(registration=registration).first()

    if request.method == "POST":
        if ('delete') in request.POST:
            # multiaxial_description.delete()
            return redirect('cases')
        # form = MultiaxialDescriptionForm(request.POST, instance=)
        # if form.is_valid:
        #     obj = form.save()
        #     obj.save()
        #     # messages.success(request, "You successfully updated the post")
        #     return redirect('cases')

    case = Case.objects.get(id=case_id)

    context = {
        "desscribe": desscribe,
        # "form": form,
        "case_id": case_id,
        "case_name": case.first_name + " " + case.surname,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "multiaxial_description"
    }

    return render(request=request, template_name='epilepsy12/multiaxial_description.html', context=context)


@login_required
def delete_multiaxial_description(request, id):
    # multiaxial_description = get_object_or_404(
    #     MultiaxialDescriptionForm, id=id)
    # multiaxial_description.delete()
    return redirect('cases')
