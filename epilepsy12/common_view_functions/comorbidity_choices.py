from django.apps import apps
from ..constants import COLIN_EDIT_SNOMED_NEURODISABILITY_REFSET


def get_comorbidity_choices(multiaxial_diagnosis, comorbidity_id=None):
    """
    Returns list of comorbidities to populate dropdown lists
    Removes any items that have already been selected
    Accepts a multiaxial diagnosis instance
    """

    Comorbidity = apps.get_model("epilepsy12", "Comorbidity")
    ComorbidityList = apps.get_model("epilepsy12", "ComorbidityList")

    # Get all comorbidity entities that have been selected for this multiaxial diagnosis except the current one
    all_selected_comorbidityentities = (
        Comorbidity.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)
        .exclude(pk=comorbidity_id)
        .values_list("comorbidityentity", flat=True)
    )

    # Filter out None values from all_selected_comorbidityentities
    all_selected_comorbidityentities = [
        entity for entity in all_selected_comorbidityentities if entity is not None
    ]

    comorbidity_choices = (
        ComorbidityList.objects.all()
        .filter(preferredTerm__in=COLIN_EDIT_SNOMED_NEURODISABILITY_REFSET)
        .exclude(pk__in=all_selected_comorbidityentities)
        .order_by("preferredTerm")
    )

    return comorbidity_choices
