# python
from random import randint, choice
from datetime import date
from random import randint
import logging
from dateutil.relativedelta import relativedelta


from django.core.management.base import BaseCommand

# Logging setup
logger = logging.getLogger(__name__)

from ...general_functions import (
    cohort_number_from_first_paediatric_assessment_date,
    dates_for_cohort,
    return_random_postcode,
    random_date,
    add_epilepsy_cause_list_by_sctid,
)
from ...constants import (
    ETHNICITIES,
)
from ...models import Organisation, Case, Registration
from .create_groups import groups_seeder
from .create_e12_records import create_epilepsy12_record, create_registrations
from epilepsy12.tests.factories import E12CaseFactory
from epilepsy12.management.commands.old_pt_data_scripts import (
    insert_old_pt_data,
)
from epilepsy12.management.commands.user_scripts import insert_user_data
from epilepsy12.common_view_functions import _seed_all_aggregation_models


class Command(BaseCommand):
    help = "seed database with organisation trust data for testing and development."

    def add_arguments(self, parser):
        parser.add_argument("-m", "--mode", type=str, help="Mode")
        parser.add_argument(
            "-c",
            "--cases",
            nargs="?",
            type=int,
            help="Indicates the number of children to be created",
            default=50,
        )
        parser.add_argument(
            "-ct",
            "--cohort",
            nargs="?",
            type=int,
            help="Indicates the cohort to create children for. Note cannot be less than 4.",
            default=7,
        )
        parser.add_argument(
            "-fy",
            "--full_year",
            nargs="?",
            type=bool,
            help="Optional parameter. Set True if all cases must have completed a full year of care.",
            default=False,
        )
        parser.add_argument(
            "-sctids",
            "--snomedctids",
            nargs="+",
            help="List of SNOMED-CT ids to update the epilepsy causes with.",
            type=int,
        )

    def handle(self, *args, **options):
        if options["mode"] == "cases":
            cases = options["cases"]
            self.stdout.write("seeding with dummy case data...")
            run_dummy_cases_seed(cases=cases)

        elif options["mode"] == "seed_registrations":
            self.stdout.write(
                "register cases in audit and complete all fields with random answers..."
            )
            cohort = options["cohort"]
            completed_full_year = options["full_year"]
            run_registrations(cohort=cohort, full_year=completed_full_year)
            _seed_all_aggregation_models()
        elif options["mode"] == "seed_groups_and_permissions":
            self.stdout.write("setting up groups and permissions...")
            groups_seeder(run_create_groups=True)
        elif options["mode"] == "add_permissions_to_existing_groups":
            self.stdout.write("adding permissions to groups...")
            groups_seeder(add_permissions_to_existing_groups=True)
        elif options["mode"] == "upload_old_patient_data":
            self.stdout.write("Uploading old patient data.")
            insert_old_pt_data()
        elif options["mode"] == "upload_user_data":
            self.stdout.write("Uploading user data.")
            insert_user_data()
        elif options["mode"] == "add_new_epilepsy_causes":
            extra_concept_ids = options["snomedctids"]
            if not isinstance(extra_concept_ids, list):
                self.stdout.write("Must provide a list of SNOMED CT ID integers.")
                return
            add_epilepsy_cause_list_by_sctid(extra_concept_ids=extra_concept_ids)

        else:
            self.stdout.write("No options supplied...")


def run_dummy_cases_seed(verbose=True, cases=50):
    if verbose:
        print("\033[33m", f"Seeding {cases} fictional cases...", "\033[33m")
    # there should not be any cases yet, but sometimes seed gets run more than once
    if Case.objects.all().exists():
        if verbose:
            print("Cases already exist. Skipping this step...")
        return

    if cases is None or cases == 0:
        cases = 50

    different_organisations = [
        "RJZ01",
        "RGT01",
        "RBS25",
        "RQM01",
        "RCF22",
        "7A2AJ",
        "7A6BJ",
        "7A6AV",
    ]
    organisations_list = Organisation.objects.filter(
        ods_code__in=different_organisations
    ).order_by("name")
    for org in organisations_list:
        num_cases_to_seed_in_org = int(cases / len(different_organisations))
        print(f"Creating {num_cases_to_seed_in_org} Cases in {org}")

        # Create random attributes
        random_date = date(randint(2005, 2021), randint(1, 12), randint(1, 28))
        date_of_birth = random_date
        sex = randint(1, 2)
        seed_male = True if sex == 1 else False
        seed_female = True if sex == 2 else False
        random_ethnicity = randint(0, len(choice(ETHNICITIES)))
        ethnicity = ETHNICITIES[random_ethnicity][0]
        postcode = return_random_postcode(
            country_boundary_identifier=org.country.boundary_identifier
        )
        index_of_multiple_deprivation_quintile = randint(1, 5)

        E12CaseFactory.create_batch(
            num_cases_to_seed_in_org,
            locked=False,
            sex=sex,
            date_of_birth=date_of_birth,
            postcode=postcode,
            ethnicity=ethnicity,
            index_of_multiple_deprivation_quintile=index_of_multiple_deprivation_quintile,
            organisations__organisation=org,
            **{
                "seed_male": seed_male,
                "seed_female": seed_female,
            },
        )


def run_registrations(verbose=True, cohort=7, full_year=False):
    """
    Calling function to register all cases in Epilepsy12 and complete all fields with random answers
    """
    if verbose:
        print("\033[33m", "Registering fictional cases in Epilepsy12...", "\033[33m")

    create_registrations(verbose=verbose)

    complete_registrations(verbose=verbose, cohort=cohort, full_year=full_year)

    if not verbose:
        print(
            "run_registrations(verbose=False), no output, cases registered and completed."
        )


def complete_registrations(verbose=True, cohort=None, full_year=False):
    """
    Loop through the registrations and score all fields
    """
    if verbose:
        print(
            "\033[33m",
            "Completing all the Epilepsy12 fields for the fictional cases...",
            "\033[33m",
        )

    if cohort is None:
        current_cohort = cohort_number_from_first_paediatric_assessment_date(
            date.today()
        )
        current_cohort_data = dates_for_cohort(current_cohort)
    else:
        current_cohort_data = dates_for_cohort(cohort=cohort)

    for registration in Registration.objects.all():

        fpa_date = random_date(
            start=current_cohort_data["cohort_start_date"],
            end=current_cohort_data["cohort_end_date"],
        )

        if full_year:
            # this flag ensures any registrations include a full year of care
            if (
                current_cohort_data["cohort_start_date"] + relativedelta(years=1)
                > date.today()
            ):
                # It is not possible to generate registrations that are complete as they would be in the future
                logger.warning(
                    "It is not possible for registrations to be complete for this cohort as they would be in the future."
                )
            else:
                while fpa_date + relativedelta(years=1) >= date.today():
                    # regenerate any dates that cannot be complete
                    fpa_date = random_date(
                        start=current_cohort_data["cohort_start_date"],
                        end=current_cohort_data["cohort_end_date"],
                    )

        registration.first_paediatric_assessment_date = fpa_date
        registration.eligibility_criteria_met = True
        registration.save()

        create_epilepsy12_record(registration_instance=registration, verbose=verbose)


def image():
    return """

                                .^~^      ^777777!~:       ^!???7~:
                                ^JJJ:.:!^ 7#BGPPPGBGY:   !5BBGPPGBBY.
                                 :~!!?J~. !BBJ    YBB?  ?BB5~.  .~J^
                              .:~7?JJ?:   !BBY^~~!PBB~ .GBG:
                              .~!?JJJJ^   !BBGGGBBBY^  .PBG^
                                 ?J~~7?:  !BBJ.:?BB5^   ~GBG?^:^~JP7
                                :?:   .   !BBJ   ~PBG?.  :?PBBBBBG5!
                                ..::...     .::. ...:^::. .. .:^~~^:.
                                !GPGGGGPY7.   :!?JJJJ?7~..PGP:    !GGJ
                                7BBY~~!YBBY  !JJ?!^^^!??::GBG:    7BBJ
                                7BB?   .GBG.^JJ7.     .. .GBG!^^^^JBBJ
                                7BB577?5BBJ ~JJ!         .GBBGGGGGGBBJ
                                7BBGPPP5J~  :JJJ^.   .^^ .GBG^.::.?BBJ
                                7#B?         :7JJ?77?JJ?^:GBB:    7##Y
                                ~YY!           :~!77!!^. .JYJ.    ~YY7


                                           Epilepsy12 2022

                """
