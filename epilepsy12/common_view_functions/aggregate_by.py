from typing import Literal, Union
from datetime import date
import logging

# Django imports
from django.apps import apps
from django.contrib.gis.db.models import (
    Q,
    Count,
    When,
    Value,
    CharField,
    PositiveSmallIntegerField,
    Case as DJANGO_CASE,
)

# E12 imports
from epilepsy12.constants import ETHNICITIES, SEX_TYPE, EnumAbstractionLevel

# Logging setup
logger = logging.getLogger(__name__)

"""
Reporting
"""


def cases_aggregated_by_sex(selected_organisation):
    # aggregate queries on trust level cases

    Case = apps.get_model("epilepsy12", "Case")

    sex_long_list = [When(sex=k, then=Value(v)) for k, v in SEX_TYPE]

    cases_aggregated_by_sex = (
        Case.objects.filter(organisations=selected_organisation)
        .values("sex")
        .annotate(sex_display=DJANGO_CASE(*sex_long_list, output_field=CharField()))
        .values("sex_display")
        .annotate(sexes=Count("sex"))
        .order_by("sexes")
    )

    return cases_aggregated_by_sex


def cases_aggregated_by_deprivation_score(selected_organisation):
    # aggregate queries on trust level cases
    Case = apps.get_model("epilepsy12", "Case")

    cases_in_selected_organisation = Case.objects.filter(
        organisations__name__contains=selected_organisation
    )

    cases_aggregated_by_deprivation = (
        # Filter just Cases in selected org
        cases_in_selected_organisation
        # Get list of IMD quintiles
        .values("index_of_multiple_deprivation_quintile")
        # Converting 'None' to 6 in a new index_of_multiple_deprivation_quintile_display "column"
        .annotate(
            index_of_multiple_deprivation_quintile_display=DJANGO_CASE(
                When(index_of_multiple_deprivation_quintile=None, then=Value(6)),
                default="index_of_multiple_deprivation_quintile",
                output_field=PositiveSmallIntegerField(),
            )
        )
        # Keeps only the new column
        .values("index_of_multiple_deprivation_quintile_display")
        # Value count the new column
        .annotate(
            cases_aggregated_by_deprivation=Count(
                "index_of_multiple_deprivation_quintile_display"
            ),
        ).order_by("index_of_multiple_deprivation_quintile_display")
    )

    deprivation_quintile_str_map = {
        1: "1st quintile",
        2: "2nd quintile",
        3: "3rd quintile",
        4: "4th quintile",
        5: "5th quintile",
        6: "Not known",
    }

    for aggregate in cases_aggregated_by_deprivation:
        quintile = aggregate["index_of_multiple_deprivation_quintile_display"]

        str_map = deprivation_quintile_str_map.get(quintile)

        aggregate.update(
            {"index_of_multiple_deprivation_quintile_display_str": str_map}
        )

    return cases_aggregated_by_deprivation


def cases_aggregated_by_ethnicity(selected_organisation):
    # aggregate queries on trust level cases

    Case = apps.get_model("epilepsy12", "Case")

    ethnicity_long_list = [When(ethnicity=k, then=Value(v)) for k, v in ETHNICITIES]

    cases_aggregated_by_ethnicity = (
        Case.objects.filter(organisations__name__contains=selected_organisation)
        .values("ethnicity")
        .annotate(
            ethnicity_display=DJANGO_CASE(
                *ethnicity_long_list, output_field=CharField()
            )
        )
        .values("ethnicity_display")
        .annotate(ethnicities=Count("ethnicity"))
        .order_by("ethnicities")
    )

    return cases_aggregated_by_ethnicity


def get_abstraction_value_from(organisation, abstraction_level: EnumAbstractionLevel):
    """For the given abstraction level, will call getattr until the final object's value is returned.

    If attribute can't be found, default return is None. E.g. Welsh hospitals will not have an ICB Code.
    """
    if abstraction_level is EnumAbstractionLevel.NATIONAL:
        raise ValueError(
            "EnumAbstractionLevel.NATIONAL should not be used with this function."
        )

    return_object = organisation
    for attribute in abstraction_level.value.split("__"):
        return_object = getattr(return_object, attribute, None)
    return return_object


def get_filtered_cases_queryset_for(
    abstraction_level: EnumAbstractionLevel, organisation, cohort: int
):
    """Returns queryset of current audit filtered cases within the same abstraction level.

    Ensures the Case is filtered for an active, primary Site, and in the correct cohort.
    """

    cases_filter_key = f"organisations__{abstraction_level.value}"

    Case = apps.get_model("epilepsy12", "Case")

    # This should just be all cases so no filtering based on code
    if abstraction_level is EnumAbstractionLevel.NATIONAL:
        abstraction_filter = {}
    else:
        abstraction_key = get_abstraction_value_from(
            organisation, abstraction_level=abstraction_level
        )

        # Some organisations have null values for abstraction e.g. Welsh Orgs don't have ICBs; English orgs don't have  LHBs. Therefore, should return no Cases
        if abstraction_key is None:
            return Case.objects.none()

        abstraction_filter = {cases_filter_key: abstraction_key}

    cases = Case.objects.filter(
        **abstraction_filter,
        site__site_is_actively_involved_in_epilepsy_care=True,
        site__site_is_primary_centre_of_epilepsy_care=True,
        registration__cohort=cohort,
        registration__completed_first_year_of_care_date__lte=date.today(),
    )

    return cases


def calculate_kpi_value_counts_queryset(
    filtered_cases,
    abstraction_level: EnumAbstractionLevel,
    kpis: "list[str] | Literal['all']" = "all",
):
    """For the given filtered_cases queryset, for all KPIs, calculates the value counts, per abstraction level.

    Assumes the filtered_cases already have kpi scores calculated.

    Args
        `filtered_cases` (QuerySet[Case]) - filtered Cases, for which KPI model has already been updated

        `abstraction_level` (EnumAbstractionLevel) - specifies the abstraction level on which to return value counts. E.g. if EnumAbstractionLevel.ORGANISATION, each queryset in the return object will have 'organisation__ODSCode'.

        `kpis` (list[str] or Literal['all']) - Default 'all'. List of KPI model fields to perform aggregation on. If 'all', then all available fields on the KPI model, found using KPI.get_kpis() method, will be used.

    Returns `ValuesQuerySet[KPI, dict[str, any]]`.
    """

    # Get models
    KPI = apps.get_model("epilepsy12", "KPI")

    # Dict of kpi names
    kpi_names = KPI().get_kpis() if kpis == "all" else kpis

    # Initialise aggregation queries dict
    aggregate_queries = {}

    # for each kpi name, eg. 'ecg',
    # create aggregation query to calculate total passed, total eligible, total ineligble, incompelete
    for kpi_name in kpi_names:
        aggregate_queries.update(
            {
                f"{kpi_name}_passed": Count(
                    DJANGO_CASE(When(**{f"{kpi_name}": 1}, then=1))
                ),
                f"{kpi_name}_total_eligible": Count(
                    DJANGO_CASE(
                        When(Q(**{f"{kpi_name}": 1}) | Q(**{f"{kpi_name}": 0}), then=1)
                    )
                ),
                f"{kpi_name}_ineligible": Count(
                    DJANGO_CASE(When(**{f"{kpi_name}": 2}, then=1))
                ),
                f"{kpi_name}_incomplete": Count(
                    DJANGO_CASE(When(**{f"{kpi_name}": None}, then=1))
                ),
            }
        )

    # Perform aggregation
    if abstraction_level is EnumAbstractionLevel.NATIONAL:
        # NO NEED TO GROUPBY IF NATIONAL
        kpi_value_counts = KPI.objects.filter(
            registration__id__in=filtered_cases.values_list("registration")
        ).aggregate(**aggregate_queries)
    else:
        kpi_value_counts = (
            KPI.objects.filter(
                registration__id__in=filtered_cases.values_list("registration")
            )  # filter for KPIs associated with filtered cases
            .values(
                f"organisation__{abstraction_level.value}"
            )  # GROUPBY abstraction level
            .annotate(**aggregate_queries)  # AGGREGATE on each abstraction
            .order_by(
                f"organisation__{abstraction_level.value}"
            )  # To ensure order is always as expected
        )

    # WALES HAS NO TRUST, ICB, NHS ENGLAND REGION
    if (
        abstraction_level is EnumAbstractionLevel.ICB
        or abstraction_level is EnumAbstractionLevel.TRUST
        or abstraction_level is EnumAbstractionLevel.NHS_ENGLAND_REGION
    ):
        Case = apps.get_model("epilepsy12", "Case")
        welsh_cases = Case.objects.filter(
            organisations__country__boundary_identifier="W92000004",
            site__site_is_actively_involved_in_epilepsy_care=True,
            site__site_is_primary_centre_of_epilepsy_care=True,
        )

        # Filter out Welsh Cases from the value count
        kpi_value_counts = kpi_value_counts.exclude(
            registration__id__in=welsh_cases.values_list("registration")
        )

    # England HAS NO Local Health Boards
    if abstraction_level is EnumAbstractionLevel.LOCAL_HEALTH_BOARD:
        Case = apps.get_model("epilepsy12", "Case")
        english_cases = Case.objects.filter(
            organisations__country__boundary_identifier="E92000001",
            site__site_is_actively_involved_in_epilepsy_care=True,
            site__site_is_primary_centre_of_epilepsy_care=True,
        )

        # Filter out Welsh Cases from the value count
        kpi_value_counts = kpi_value_counts.exclude(
            registration__id__in=english_cases.values_list("registration")
        )

    return kpi_value_counts


def get_abstraction_model_from_level(
    enum_abstraction_level: EnumAbstractionLevel,
) -> dict:
    """Returns dict, for abstraction, of structure:

    {
        "kpi_aggregation_model": abstractionKPIAggregation model name (str),
        "abstraction_entity_model": that KPIAggregation's abstraction_relation entity model's name (str)
    }
    """
    abstraction_model_map = {
        EnumAbstractionLevel.ORGANISATION: {
            "kpi_aggregation_model": "OrganisationKPIAggregation",
            "abstraction_entity_model": "Organisation",
        },
        EnumAbstractionLevel.TRUST: {
            "kpi_aggregation_model": "TrustKPIAggregation",
            "abstraction_entity_model": "Trust",
        },
        EnumAbstractionLevel.LOCAL_HEALTH_BOARD: {
            "kpi_aggregation_model": "LocalHealthBoardKPIAggregation",
            "abstraction_entity_model": "LocalHealthBoard",
        },
        EnumAbstractionLevel.ICB: {
            "kpi_aggregation_model": "ICBKPIAggregation",
            "abstraction_entity_model": "IntegratedCareBoard",
        },
        EnumAbstractionLevel.NHS_ENGLAND_REGION: {
            "kpi_aggregation_model": "NHSEnglandRegionKPIAggregation",
            "abstraction_entity_model": "NHSEnglandRegion",
        },
        EnumAbstractionLevel.OPEN_UK: {
            "kpi_aggregation_model": "OpenUKKPIAggregation",
            "abstraction_entity_model": "OPENUKNetwork",
        },
        EnumAbstractionLevel.COUNTRY: {
            "kpi_aggregation_model": "CountryKPIAggregation",
            "abstraction_entity_model": "Country",
        },
        EnumAbstractionLevel.NATIONAL: {
            "kpi_aggregation_model": "NationalKPIAggregation",
            "abstraction_entity_model": "Country",
        },
    }
    return abstraction_model_map[enum_abstraction_level]


def update_kpi_aggregation_model(
    abstraction_level: EnumAbstractionLevel,
    kpi_value_counts,
    cohort: int,
    open_access=False,
) -> None:
    """Updates the relevant KPI Aggregation model, chosen via the `abstraction_level`. Takes output of `calculate_kpi_value_counts_queryset` to update model.

    Args:
        abstraction_level (EnumAbstractionLevel): chosen abstraction level
        kpi_value_counts (ValuesQuerySet[Model, Dict[str, Any]]): value counts of KPI scorings, grouped by abstraction
        cohort (int): cohort of aggregation
        open_access: boolean - whether publicly viewable or not. Defaults to False

        If open_access is true, a new KPI aggregation record is created, to store historical publications.
        If open_access is false, the existing KPI aggregation is updated
    """

    abstraction_level_models = get_abstraction_model_from_level(abstraction_level)

    # Get KPIAggregation model for the given abstraction level
    AbstractionKPIAggregationModel = apps.get_model(
        "epilepsy12", abstraction_level_models["kpi_aggregation_model"]
    )

    # Separate logic for national as no groupby key in aggregation value counts
    if abstraction_level is EnumAbstractionLevel.NATIONAL:
        NationalKPIAggregation = apps.get_model("epilepsy12", "NationalKPIAggregation")
        if open_access:
            # create a new record
            new_obj = NationalKPIAggregation.objects.create(
                **kpi_value_counts,
                **{
                    "cohort": cohort,
                    "open_access": open_access,
                },
            )
            logger.debug(f"created {new_obj}")

        else:
            new_obj, created = NationalKPIAggregation.objects.update_or_create(
                defaults={
                    "cohort": cohort,
                    "open_access": open_access,
                    **kpi_value_counts,
                },
                cohort=cohort,
                open_access=open_access,
            )

            if created:
                logger.debug(f"created {new_obj}")
            else:
                logger.debug(f"updated {new_obj}")

        return None

    for value_count in kpi_value_counts:
        ABSTRACTION_CODE = value_count.pop(f"organisation__{abstraction_level.value}")

        # Get the model field name for the given abstraction model. As the enum values are all with respect to Organisation, this split and grab last gets just that related model's related field.
        related_key_field = abstraction_level.value.split("__")[-1]

        # Get related entity model
        abstraction_entity_model = apps.get_model(
            "epilepsy12", abstraction_level_models["abstraction_entity_model"]
        )

        # Get instance of the related entity model to link with Aggregation model
        abstraction_relation_instance = abstraction_entity_model.objects.filter(
            **{f"{related_key_field}": ABSTRACTION_CODE}
        ).first()

        if open_access:
            # for public view: create a new record
            value_count["abstraction_relation"] = abstraction_relation_instance
            value_count["cohort"] = cohort
            value_count["open_access"] = open_access
            try:
                new_obj = AbstractionKPIAggregationModel.objects.create(**value_count)
                logger.debug(f"created {new_obj}")
            except Exception as error:
                logger.exception(
                    f"Can't save new KPIAggregations for {abstraction_level} for {abstraction_relation_instance}: {error}"
                )
                return

        else:
            # not for public view - create or update existing
            try:
                (
                    new_obj,
                    created,
                ) = AbstractionKPIAggregationModel.objects.update_or_create(
                    defaults={
                        "abstraction_relation": abstraction_relation_instance,
                        "cohort": cohort,
                        **value_count,
                    },
                    abstraction_relation=abstraction_relation_instance,
                    cohort=cohort,
                    open_access=open_access,
                )
            except Exception as error:
                logger.exception(
                    f"CLOSED VIEW: Can't update/save KPIAggregations for {abstraction_level} for {abstraction_relation_instance}: {error}"
                )
                return

            if created:
                logger.debug(f"created {new_obj}")
            else:
                logger.debug(f"updated {new_obj}")


# def aggregate_kpis_update_models_all_abstractions_for_organisation(
#     organisation,
#     cohort: int,
# ) -> None:
#     """
#     Aggregates all KPI data, for each level of EnumAbstractionLevel abstraction, updates the relevant AbstractionModel. Returns None.
#     """
#     for enum_abstraction_level in EnumAbstractionLevel:
#         filtered_cases = get_filtered_cases_queryset_for(
#             organisation=organisation,
#             abstraction_level=enum_abstraction_level,
#             cohort=cohort,
#         )

#         # For these Cases, calculate KPI value counts, grouped by specified abstraction level
#         kpi_value_counts = calculate_kpi_value_counts_queryset(
#             filtered_cases=filtered_cases,
#             abstraction_level=enum_abstraction_level,
#             kpis="all",
#         )

#         # Update the relevant abstraction's KPIAggregation model(s)
#         update_kpi_aggregation_model(
#             abstraction_level=enum_abstraction_level,
#             kpi_value_counts=kpi_value_counts,
#             cohort=cohort,
#         )


def update_all_kpi_agg_models(
    cohort: int,
    abstractions: Union[Literal["all"], list[EnumAbstractionLevel]] = "all",
    open_access=False,
) -> None:
    """
    Using all cases in a given cohort,
        for all abstraction levels | specified `abstractions`,
            aggregate kpi scores and update that abstraction's KPIAggregation model

    Args:
        `cohort` - cohort filter for Cases
        `abstraction` (optional, default='all') - specify abstraction level(s) to update. Provide list of EnumAbstractionLevel values if required.
    """
    if (abstractions != "all") and not isinstance(abstractions, list):
        raise ValueError(
            'Can only be string literal "all" or list of EnumAbstraction values'
        )

    if isinstance(abstractions, list):
        if not all(isinstance(item, EnumAbstractionLevel) for item in abstractions):
            raise ValueError(
                "If providing list, all items must be EnumAbstraction values"
            )

    Case = apps.get_model("epilepsy12", "Case")

    """
    filter all Cases at this Site where
    # site is actively involved in care
    # site is lead centre
    # matched for cohort
    # have completed a full year of epilepsy care
    """
    all_cases = Case.objects.filter(
        site__site_is_actively_involved_in_epilepsy_care=True,
        site__site_is_primary_centre_of_epilepsy_care=True,
        registration__cohort=cohort,
        registration__completed_first_year_of_care_date__lte=date.today(),
    )

    abstraction_levels = EnumAbstractionLevel if abstractions == "all" else abstractions

    for ABSTRACTION_LEVEL in abstraction_levels:

        kpi_value_counts = calculate_kpi_value_counts_queryset(
            filtered_cases=all_cases,
            abstraction_level=ABSTRACTION_LEVEL,
            kpis="all",
        )

        # Update all KPIAggregation models for abstraction
        update_kpi_aggregation_model(
            abstraction_level=ABSTRACTION_LEVEL,
            kpi_value_counts=kpi_value_counts,
            cohort=cohort,
            open_access=open_access,
        )


def get_all_kpi_aggregation_data_for_view(
    organisation,
    cohort: int,
    kpis: "list[str] | Literal['all']" = "all",
    open_access=False,
) -> dict:
    """
    Aggregates all KPI data, for each level of EnumAbstractionLevel abstraction, updates the relevant AbstractionModel and returns the KPI model as a dict.
    """
    ALL_DATA = {}
    for enum_abstraction_level in EnumAbstractionLevel:
        # For the given abstraction, get the {ABSTRACTION}KPIAggregation model
        abstraction_kpi_agg_model_name = get_abstraction_model_from_level(
            enum_abstraction_level
        )["kpi_aggregation_model"]
        abstraction_kpi_agg_model = apps.get_model(
            "epilepsy12", abstraction_kpi_agg_model_name
        )

        # Get THIS organisation instance's abstraction relation entity. All the enum values are with respect to Organisation, thus the first element of .split('__') is the related field.
        abstraction_relation_field_name = enum_abstraction_level.value.split("__")[0]

        if enum_abstraction_level is EnumAbstractionLevel.ORGANISATION:
            abstraction_relation = organisation
        else:
            abstraction_relation = getattr(
                organisation, f"{abstraction_relation_field_name}"
            )

        # NationalKPIAggregation model does not have abstraction relation field, so handle differently to the rest and skip rest of loop
        NationalKPIAggregation = apps.get_model("epilepsy12", "NationalKPIAggregation")
        if abstraction_kpi_agg_model == NationalKPIAggregation:
            if (
                abstraction_kpi_agg_model.objects.filter(
                    cohort=cohort, open_access=open_access
                )
                .order_by("-last_updated")
                .first()
                is None
            ):
                total_registered = 0
            else:
                total_registered = (
                    abstraction_kpi_agg_model.objects.filter(
                        cohort=cohort, open_access=open_access
                    )
                    .order_by("-last_updated")
                    .first()
                    .get_total_cases_included_in_aggregation()
                )

            ALL_DATA[f"{enum_abstraction_level.name}_KPIS"] = {
                "aggregation_model": abstraction_kpi_agg_model.objects.filter(
                    cohort=cohort, open_access=open_access
                )
                .order_by("-last_updated")
                .first(),
                "total_cases_registered": total_registered,
            }
            continue

        # Check if KPIAggregation model exists. If Organisation does not have any cases where that Organisation is primary care Site, then the KPIAgg will not exist.
        if abstraction_kpi_agg_model.objects.filter(
            abstraction_relation=abstraction_relation,
            cohort=cohort,
            open_access=open_access,
        ).exists():
            aggregation_model_instance = (
                abstraction_kpi_agg_model.objects.filter(
                    abstraction_relation=abstraction_relation,
                    cohort=cohort,
                    open_access=open_access,
                )
                .order_by("-last_updated")
                .first()
            )
            ALL_DATA[f"{enum_abstraction_level.name}_KPIS"] = {
                "aggregation_model": aggregation_model_instance,
                "total_cases_registered": aggregation_model_instance.get_total_cases_included_in_aggregation(),
            }
        else:
            filtered_cases = get_filtered_cases_queryset_for(
                organisation=organisation,
                abstraction_level=enum_abstraction_level,
                cohort=cohort,
            )

            ALL_DATA[f"{enum_abstraction_level.name}_KPIS"] = {
                "aggregation_model": None,
                "total_cases_registered": filtered_cases.count(),
            }

    return ALL_DATA


def _seed_all_aggregation_models() -> None:
    from epilepsy12.general_functions import (
        dates_for_cohort,
        cohort_number_from_first_paediatric_assessment_date,
    )

    Organisation = apps.get_model("epilepsy12", "Organisation")
    OrganisationKPIAggregation = apps.get_model(
        "epilepsy12", "OrganisationKPIAggregation"
    )

    Trust = apps.get_model("epilepsy12", "Trust")
    TrustKPIAggregation = apps.get_model("epilepsy12", "TrustKPIAggregation")

    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")
    LocalHealthBoardKPIAggregation = apps.get_model(
        "epilepsy12", "LocalHealthBoardKPIAggregation"
    )

    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    ICBKPIAggregation = apps.get_model("epilepsy12", "ICBKPIAggregation")

    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    NHSEnglandRegionKPIAggregation = apps.get_model(
        "epilepsy12", "NHSEnglandRegionKPIAggregation"
    )

    OPENUKNetwork = apps.get_model("epilepsy12", "OPENUKNetwork")
    OpenUKKPIAggregation = apps.get_model("epilepsy12", "OpenUKKPIAggregation")

    Country = apps.get_model("epilepsy12", "Country")
    CountryKPIAggregation = apps.get_model("epilepsy12", "CountryKPIAggregation")

    NationalKPIAggregation = apps.get_model("epilepsy12", "NationalKPIAggregation")

    current_cohort = cohort_number_from_first_paediatric_assessment_date(date.today())

    all_orgs = Organisation.objects.all().distinct()
    all_trusts = Trust.objects.all().distinct()
    all_local_health_boards = LocalHealthBoard.objects.all()
    all_icbs = IntegratedCareBoard.objects.all().distinct()
    all_nhs_regions = NHSEnglandRegion.objects.all().distinct()
    all_open_uks = OPENUKNetwork.objects.all().distinct()
    all_countries = Country.objects.all().distinct()

    all_entities = [
        all_orgs,
        all_trusts,
        all_local_health_boards,
        all_icbs,
        all_nhs_regions,
        all_open_uks,
        all_countries,
    ]
    all_agg_models = [
        OrganisationKPIAggregation,
        TrustKPIAggregation,
        LocalHealthBoardKPIAggregation,
        ICBKPIAggregation,
        NHSEnglandRegionKPIAggregation,
        OpenUKKPIAggregation,
        CountryKPIAggregation,
        NationalKPIAggregation,
    ]

    if len(all_entities) + 1 != len(all_agg_models):
        logger.error(
            f"Incorrect lengths for entities. KPIAggregations not seeded. {len(all_entities)+1=}{len(all_agg_models)=}"
        )
        return

    for entities, AggregationModel in zip(all_entities, all_agg_models):
        logger.info(f"Creating aggregations for {AggregationModel}")
        for entity in entities:
            if AggregationModel.objects.filter(
                abstraction_relation=entity,
                cohort=current_cohort,
            ).exists():
                logger.info(
                    f"AggregationModel for {entity} already exists. Skipping..."
                )
                continue

            new_agg_model = AggregationModel.objects.create(
                abstraction_relation=entity,
                cohort=current_cohort,
            )

            logger.info(f"Created {new_agg_model}")

    # National handled separately as it has no abstraction relation field
    if NationalKPIAggregation.objects.filter(
        cohort=current_cohort,
    ).exists():
        logger.info(f"NationalKPIAggregation for {entity} already exists. Skipping...")
    else:
        new_agg_model = NationalKPIAggregation.objects.create(
            cohort=current_cohort,
        )
        logger.info(f"Created {new_agg_model} (Cohort {current_cohort})")


def ___delete_and_recreate_all_kpi_aggregation_models():
    """WARNING: DESTRUCTIVE FUNCTION, only for use in local dev environments.

    This 'wipes clean' the KPIAggregation models - it first deletes all models, then it creates new, empty ones where values are none.

    Its purpose is for internal testing.
    """

    ALL_AGGREGATION_MODEL_NAMES = [
        "OrganisationKPIAggregation",
        "TrustKPIAggregation",
        "LocalHealthBoardKPIAggregation",
        "ICBKPIAggregation",
        "NHSEnglandRegionKPIAggregation",
        "OpenUKKPIAggregation",
        "CountryKPIAggregation",
        "NationalKPIAggregation",
    ]

    for aggregation_model_name in ALL_AGGREGATION_MODEL_NAMES:
        aggregation_model = apps.get_model("epilepsy12", aggregation_model_name)

        aggregation_model.objects.all().delete()

    _seed_all_aggregation_models()
