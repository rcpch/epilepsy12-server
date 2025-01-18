# python imports
from dateutil.relativedelta import relativedelta

# django imports

# E12 imports


def calculate_age_at_first_paediatric_assessment_in_years(
    registration_instance,
) -> float:
    """
    Helper fn returns age in years as float
    """
    if registration_instance.first_paediatric_assessment_date is None:
        # in theory, this should never happen, but just in case
        return None
    if registration_instance.case.date_of_birth is None:
        return None
    age_at_first_paediatric_assessment_in_days = (
        registration_instance.first_paediatric_assessment_date
        - registration_instance.case.date_of_birth
    )

    return age_at_first_paediatric_assessment_in_days.days / 365.25
