# python imports
from dateutil.relativedelta import relativedelta

# django imports

# E12 imports
from epilepsy12.constants import KPI_SCORE


def score_kpi_1(registration_instance) -> int:
    """
    1. `paediatrician_with_expertise_in_epilepsies`

    % of children and young people with epilepsy, with input by a ‘consultant paediatrician with expertise in epilepsies’ within 2 weeks of initial referral

    Calculation Method

    Numerator = Number of children and young people  [diagnosed with epilepsy] at first year AND (who had [input from a paediatrician with expertise in epilepsy] OR a [input from a paediatric neurologist] within 2 weeks of initial referral. (initial referral to mean first paediatric assessment)

    Denominator = Number of and young people [diagnosed with epilepsy] at first year
    """

    assessment = registration_instance.assessment

    # set variables which check if date fields complete for either consultant or neurologist
    # It is important to use the dates only because the achieved fields were introduced later so it is possible that the achieved fields are not filled in but two dates are still present.
    all_consultant_paediatrician_date_fields_complete = (
        assessment.consultant_paediatrician_referral_date is not None
        and assessment.consultant_paediatrician_input_date is not None
    )

    all_consultant_paediatrician_date_fields_empty = (
        assessment.consultant_paediatrician_referral_date is None
        and assessment.consultant_paediatrician_input_date is None
    )

    some_consultant_paediatrician_date_fields_empty = (
        assessment.consultant_paediatrician_referral_date is None
        or assessment.consultant_paediatrician_input_date is None
    )

    all_paediatric_neurologist_date_fields_complete = (
        assessment.paediatric_neurologist_referral_date is not None
        and assessment.paediatric_neurologist_input_date is not None
    )

    all_paediatric_neurologist_date_fields_empty = (
        assessment.paediatric_neurologist_referral_date is None
        and assessment.paediatric_neurologist_input_date is None
    )
    some_paediatric_neurologist_date_fields_empty = (
        assessment.paediatric_neurologist_referral_date is None
        or assessment.paediatric_neurologist_input_date is None
    )
    did_pass = None

    # all all doubled date events
    if all_consultant_paediatrician_date_fields_complete:
        passed_metric = (
            assessment.consultant_paediatrician_input_date
            - assessment.consultant_paediatrician_referral_date
        ).days <= 14
        if passed_metric:
            return KPI_SCORE["PASS"]
        else:
            did_pass = False

    if all_paediatric_neurologist_date_fields_complete:
        passed_metric = (
            assessment.paediatric_neurologist_input_date
            - assessment.paediatric_neurologist_referral_date
        ).days <= 14
        if passed_metric:
            return KPI_SCORE["PASS"]
        else:
            did_pass = False

    # leaves options where some fields are empty
    if some_consultant_paediatrician_date_fields_empty:
        if (
            assessment.consultant_paediatrician_referral_made is False
            or assessment.consultant_paediatrician_input_achieved is False
        ):
            did_pass = False
    if some_paediatric_neurologist_date_fields_empty:
        if (
            assessment.paediatric_neurologist_referral_made is False
            or assessment.paediatric_neurologist_input_achieved is False
        ):
            did_pass = False

    if did_pass is False:
        return KPI_SCORE["FAIL"]
    else:
        return KPI_SCORE["NOT_SCORED"]
