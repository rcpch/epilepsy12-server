# Django Imports
from django.apps import apps

# Third party imports
import pandas as pd

# E12 Imports
from epilepsy12.constants import (
    LOCAL_HEALTH_BOARDS,
    INTEGRATED_CARE_BOARDS,
    NHS_ENGLAND_REGIONS,
    OPEN_UK_NETWORKS,
    OPEN_UK_NETWORKS_TRUSTS,
    INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES,
)
from epilepsy12.common_view_functions.aggregate_by import (
    create_KPI_aggregation_dataframe,
    create_reference_dataframe,
    create_kpi_report_row,
    get_kpi_aggregation_rows,
    create_totals_dataframe,
)
from epilepsy12.models import (
    Organisation,
    Trust,
    KPI,
    ICBKPIAggregation,
    OpenUKKPIAggregation,
    CountryKPIAggregation,
    LocalHealthBoardKPIAggregation,
    TrustKPIAggregation,
    NHSEnglandRegionKPIAggregation,
    NationalKPIAggregation,
)


def download_kpi_summary_as_csv(cohort):
    """
    Asynchronous task to pull data from KPIAggregation tables and store as dataframe for export as CSV
    Accepts cohort as optional param
    Output - 8 sheets of .xlsx structured as follows:
    - Country level
    - HBT level
    - ICB level
    - NHSregion_level
    - Network_level
    - National_level
    - Reference
    - National_comparison
    """

    # The summary only includes some measures
    measures = [
        KPI._meta.get_field("paediatrician_with_expertise_in_epilepsies"),
        KPI._meta.get_field("epilepsy_specialist_nurse"),
        KPI._meta.get_field("tertiary_input"),
        KPI._meta.get_field("epilepsy_surgery_referral"),
        KPI._meta.get_field("ecg"),
        KPI._meta.get_field("mri"),
        KPI._meta.get_field("assessment_of_mental_health_issues"),
        KPI._meta.get_field("mental_health_support"),
        KPI._meta.get_field("sodium_valproate"),
        KPI._meta.get_field("comprehensive_care_planning_agreement"),
        KPI._meta.get_field("comprehensive_care_planning_content"),
        KPI._meta.get_field("school_individual_healthcare_plan"),
    ]

    # Many trusts do not have organisations that participate in the audit
    # The list of trusts in the database includes all of them
    # The list of organisations however is curated to just those that participate
    trusts_from_organisations = Organisation.objects.values("trust").distinct()
    trusts_participating_in_the_audit = Trust.objects.filter(
        id__in=trusts_from_organisations
    ).values()

    # COUNTRY - SHEET 1
    # create a dataframe with a row for each measure of each country, and a column for each of ["Measure", "Percentage", "Numerator", "Denominator"]

    all_country_rows = get_kpi_aggregation_rows(
        CountryKPIAggregation, cohort, abstraction_key_field="name"
    )

    # Only England and Wales participate in the audit but we have entries in the country table for NI and Scotland
    # Even if a participating country doesn't have any data yet we'd still like to include a blank row for it
    # We keep a row for Wales as we need it later on for SHEET 4 - NHS Region level
    england_rows = [row for row in all_country_rows if row["key_field"] == "England"]
    wales_rows = [row for row in all_country_rows if row["key_field"] == "Wales"]

    country_df = create_KPI_aggregation_dataframe(
        england_rows + wales_rows, measures, title="Country"
    )

    # HBT (Trusts & Health Boards) - SHEET 2

    # Only in Wales
    local_health_board_rows = get_kpi_aggregation_rows(
        LocalHealthBoardKPIAggregation, cohort, abstraction_key_field="ods_code"
    )

    # Only in England
    trust_rows = get_kpi_aggregation_rows(
        TrustKPIAggregation, cohort, abstraction_key_field="ods_code"
    )

    # Only those trusts that participate in the audit
    ods_codes_for_trusts_participating_in_the_audit = [
        trust["ods_code"] for trust in trusts_participating_in_the_audit
    ]
    trust_rows = [
        row
        for row in trust_rows
        if row["key_field"] in ods_codes_for_trusts_participating_in_the_audit
    ]

    trust_hb_df = create_KPI_aggregation_dataframe(
        local_health_board_rows + trust_rows, measures, title="HBT"
    )

    # ICB (Integrated Care Board) - SHEET 3

    icb_rows = get_kpi_aggregation_rows(
        ICBKPIAggregation, cohort, abstraction_key_field="name"
    )

    icb_df = create_KPI_aggregation_dataframe(icb_rows, measures, title="ICB")

    # NHS region level - SHEET 4

    nhs_england_regional_rows = get_kpi_aggregation_rows(
        NHSEnglandRegionKPIAggregation, cohort, abstraction_key_field="name"
    )

    # Treat Wales as a single region
    region_rows = nhs_england_regional_rows + wales_rows

    region_df = create_KPI_aggregation_dataframe(
        region_rows,
        measures,
        title="NHSregion",
    )

    # NETWORKS - SHEET 5

    network_rows = get_kpi_aggregation_rows(
        OpenUKKPIAggregation, cohort, abstraction_key_field="boundary_identifier"
    )

    network_df = create_KPI_aggregation_dataframe(
        network_rows, measures, title="Network"
    )

    # NATIONAL - SHEET 6
    # create a dataframe with a row for each measure, and column for each of ["Measure", "Percentage", "Numerator", "Denominator"]
    # note rows are named ["1. Paediatrician with expertise","2. Epilepsy specialist nurse","3a. Tertiary involvement","3b. Epilepsy surgery referral","4. ECG","5. MRI","6. Assessment of mental health issues","7. Mental health support","8. Sodium valproate","9a. Comprehensive care planning agreement","9b. Comprehensive care planning content","10. School Individual Health Care Plan"]

    # NationalKPIAggregation has no abstraction relation to walk so add the key field manually
    national_rows = [
        row | {"key_field": "England and Wales"}
        for row in get_kpi_aggregation_rows(NationalKPIAggregation, cohort)
    ]

    national_df = create_KPI_aggregation_dataframe(national_rows, measures, title="uk")

    # REFERENCE - SHEET 7

    reference_df = create_reference_dataframe(
        trusts_participating_in_the_audit,
        LOCAL_HEALTH_BOARDS,
        OPEN_UK_NETWORKS_TRUSTS,
        INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES,
    )

    # TOTALS - SHEET 8
    trust_totals_df = create_totals_dataframe(
        cohort=cohort,
        abstraction_level="trust",
    )
    local_health_board_totals_df = create_totals_dataframe(
        cohort=cohort,
        abstraction_level="local_health_board",
    )
    icb_totals_df = create_totals_dataframe(
        cohort=cohort,
        abstraction_level="icb",
    )
    nhs_england_region_totals_df = create_totals_dataframe(
        cohort=cohort,
        abstraction_level="nhs_england_region",
    )
    openuk_network_totals_df = create_totals_dataframe(
        cohort=cohort,
        abstraction_level="open_uk",
    )
    country_totals_df = create_totals_dataframe(
        cohort=cohort,
        abstraction_level="country",
    )

    return (
        country_df,
        trust_hb_df,
        icb_df,
        region_df,
        network_df,
        national_df,
        reference_df,
        trust_totals_df,
        local_health_board_totals_df,
        icb_totals_df,
        nhs_england_region_totals_df,
        openuk_network_totals_df,
        country_totals_df,
    )
