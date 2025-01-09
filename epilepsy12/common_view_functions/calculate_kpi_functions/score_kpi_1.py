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

    # never saw a consultant OR neurologist!
    if (assessment.consultant_paediatrician_referral_made == False) and (
        assessment.paediatric_neurologist_referral_made == False
    ):
        return KPI_SCORE["FAIL"]

    # check all fields complete for either consultant or neurologist
    all_consultant_paediatrician_date_fields_complete = (
        assessment.consultant_paediatrician_referral_date is not None
    ) and (assessment.consultant_paediatrician_input_date is not None)
    all_paediatric_neurologist_date_fields_complete = (
        assessment.paediatric_neurologist_referral_date is not None
    ) and (assessment.paediatric_neurologist_input_date is not None)

    # incomplete
    if (not all_consultant_paediatrician_date_fields_complete) and (
        not all_paediatric_neurologist_date_fields_complete
    ):
        return KPI_SCORE["NOT_SCORED"]

    # score KPI
    did_pass_paediatrician = None
    did_pass_neurologist = None
    if all_consultant_paediatrician_date_fields_complete:
        passed_metric = (
            assessment.consultant_paediatrician_input_date
            - assessment.consultant_paediatrician_referral_date
        ).days <= 14
        if passed_metric:
            did_pass_paediatrician = True
        else:
            did_pass_paediatrician = False

    if all_paediatric_neurologist_date_fields_complete:
        passed_metric = (
            assessment.paediatric_neurologist_input_date
            - assessment.paediatric_neurologist_referral_date
        ).days <= 14
        if passed_metric:
            did_pass_neurologist = True
        else:
            did_pass_neurologist = False

    if did_pass_paediatrician or did_pass_neurologist:
        return KPI_SCORE["PASS"]
    elif did_pass_paediatrician is False or did_pass_neurologist:
        return KPI_SCORE["FAIL"]
    else:
        return KPI_SCORE["NOT_SCORED"]
