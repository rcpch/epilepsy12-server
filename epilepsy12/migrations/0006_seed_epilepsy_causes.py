# Generated by Django 4.2 on 2023-04-24 11:46
import logging

from django.db import migrations

from ..general_functions import fetch_ecl, add_epilepsy_cause_list_by_sctid

# Logging setup
logger = logging.getLogger(__name__)


def seed_epilepsy_causes(apps, schema_editor):
    """
    This returns all the snomed ct definitions and codes for epilepsy causes.
    Should be run periodically to compare with value in database and update record if has changed
    """

    # Get models
    EpilepsyCause = apps.get_model("epilepsy12", "EpilepsyCause")

    logger.info("\033[33m Seeding all the epilepsy causes from SNOMED... \033[33m")
    if EpilepsyCause.objects.count() > 150:
        logger.info("Causes already exist. Skipping this step...")
        return
    index = 0
    ecl = "<< 363235000"
    # calls the rcpch deprivare server for a list of causes using ECL query language
    epilepsy_causes = fetch_ecl(ecl)
    for cause in epilepsy_causes:
        if EpilepsyCause.objects.filter(conceptId=cause["conceptId"]).exists():
            # duplicate conceptId
            pass
        else:
            new_cause = EpilepsyCause(
                conceptId=cause["conceptId"],
                term=cause["term"],
                preferredTerm=cause["preferredTerm"],
            )
            try:
                new_cause.save()
                index += 1
            except Exception as e:
                logger.info(f"Epilepsy cause {cause['preferredTerm']} not added. {e}")
    logger.info(f"{index} epilepsy causes added")

    """
    These are additional causes added after go live
    Added here now so that any development work where the database has been reseeded
    remains in sync with what is live
    """

    # Constitutional mismatch repair deficiency syndrome (CMMRD) - 764946008
    # Neonatal hypoglycaemia - 52767006
    # Hypoxic ischaemic encephalopathy - 703300001
    # Perinatal arterial ischaemic stroke - 722929005
    # Non-accidental injury to child - 158094009
    # Periventricular leukomalacia - 230769007
    # Neonatal cerebral haemorrhage - 261808007
    # Cornelia de Lange Syndrome (CdLS) - 40354009
    # Anoxic encephalopathy - 389098007
    # Congenital Melanocytic Naevus – 398696001
    # Megalencephalic leukoencephalopathy with subcortical cysts - 703536004
    # Cerebral ischemic stroke due to global hypoperfusion with watershed infarct - 788882003
    # Schizencephaly (disorder) - 253159001
    # Tetrasomy 12p syndrome (disorder) - 9527009
    # Klinefelter syndrome (disorder)	22053006
    # Hypothalamic neuronal hamartoma (disorder)	230791000
    # Traumatic brain injury (disorder)	127295002
    # Angelman syndrome (disorder)	76880004
    # Rett's disorder (disorder)	68618008
    # Neuronal ceroid lipofuscinosis (disorder)	42012007
    # UBE3A 722056009
    # GLUT1 445252005
    # SLC2A1 782911008
    # MECP2 702816000
    # SCN1A 230437002
    # STXBP1 768666006
    # CDKL5 773230003
    # KCNQ2 778001003
    # SCN2A 778002005
    # KCNT1 no code - NOTE THIS NEEDS ADDING TO THE DATABASE MANUALLY
    # ARX 725163002
    # FOXG1 702450004
    # PCDH19 888801000000105
    # GRIN2A 770431001
    # Dysembryoplastic neuroepithelial neoplasm of brain (disorder) 1196837008 - NOTE THIS DOES NOT EXIST IN CURRENT SNOMED TERMINOLOGY SERVER: ADD MANUALLY
    # Cavernous hemangioma (disorder) SCTID: 416824008
    # Chromosome 11p13 deletion syndrome (disorder) SCTID: 715215007
    # Cortical dysplasia (disorder) SCTID: 253153000
    # 2q23.3 Microdeletion Syndrome - NOTE THIS NEEDS ADDING TO THE DATABASE MANUALLY AS THERE IS NO SNOMED CODE
    # 14q32 deletion syndrome (disorder) SCTID: 879939002
    # 16p11.2 deletion syndrome is 699307007
    # 16p11.2 microduplication syndrome 765142003

    extra_concept_ids = [
        764946008,
        52767006,
        703300001,
        722929005,
        158094009,
        230769007,
        261808007,
        40354009,
        389098007,
        398696001,
        703536004,
        788882003,
        253159001,
        9527009,
        22053006,
        230791000,
        127295002,
        76880004,
        68618008,
        42012007,
        722056009,
        445252005,
        782911008,
        702816000,
        230437002,
        768666006,
        773230003,
        778001003,
        778002005,
        725163002,
        702450004,
        888801000000105,
        770431001,
        416824008,
        715215007,
        253153000,
        879939002,
        699307007,
        765142003,
    ]
    add_epilepsy_cause_list_by_sctid(extra_concept_ids=extra_concept_ids)


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0005_seed_organisations"),
    ]

    operations = [migrations.RunPython(seed_epilepsy_causes)]
