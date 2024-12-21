"""
Contains functions related to updating the epilepsy causes list
"""

# Python imports
import csv
import json
import logging

# Django imports
from django.apps import apps

# Third party imports

# RCPCH imports
from .fetch_snomed import add_cause_by_sctid_to_database

# Logging setup
logger = logging.getLogger(__name__)


def dump_cause_list(format=["json", "csv", "markdown"]):
    """
    Function that dumps the epilepsy causes list in a specified format
    """
    EpilepsyCause = apps.get_model("epilepsy12", "EpilepsyCause")
    causes = (
        EpilepsyCause.objects.all()
        .order_by("preferredTerm")
        .values("conceptId", "term", "preferredTerm")
    )
    if "json" in format:
        with open("epilepsy_causes.json", "w") as json_file:
            json.dump(list(causes), json_file)
    if "csv" in format:
        with open("epilepsy_causes.csv", "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["conceptId", "term", "preferredTerm"])
            for cause in causes:
                writer.writerow(cause.values())
    if "markdown" in format:
        with open("epilepsy_causes.md", "w") as md_file:
            md_file.write("| conceptId | term | preferredTerm |\n")
            md_file.write("| --- | --- | --- |\n")
            for cause in causes:
                md_file.write(
                    f"| {cause['conceptId']} | {cause['term']} | {cause['preferredTerm']} |\n"
                )
    return {"success": True, "message": "Files created successfully"}


def add_epilepsy_causes_without_snomedct_ids(causes):
    """
    Add epilepsy causes without SNOMED CT IDs
    (not that if a SNOMED CT ID is provide, it will be used to fetch the concept, but the assumption is that the ID is not provided)

    :param causes: List of dictionaries with keys 'conceptId', 'term', and 'preferredTerm'
    """
    errors = []
    added_causes = []
    for cause in causes:
        concept_id = cause.get("conceptId")
        term = cause.get("term")
        preferred_term = cause.get("preferredTerm")
        if not term and not preferred_term:
            errors.append(
                {
                    "conceptId": concept_id,
                    "term": term,
                    "preferredTerm": preferred_term,
                    "error": "At least one of term and preferredTerm are required",
                }
            )
            continue
        if concept_id and not term and not preferred_term:
            try:
                add_cause_by_sctid_to_database(sct_id=concept_id)
                added_causes.append(
                    {
                        "concept_id": concept_id,
                        "preferredTerm": preferred_term,
                        "term": term,
                    }
                )
            except Exception as e:
                # this function checks for duplicates already
                errors.append(
                    {
                        "conceptId": concept_id,
                        "term": term,
                        "preferredTerm": preferred_term,
                        "error": f"Error: {e}",
                    }
                )
                continue
        # If term is not provided, use preferredTerm and vice versa
        if term and not preferred_term:
            preferred_term = term
        if preferred_term and not term:
            term = preferred_term

        EpilepsyCause = apps.get_model("epilepsy12", "EpilepsyCause")
        if EpilepsyCause.objects.filter(
            preferredTerm__icontains=preferred_term
        ).exists():
            return {"success": False, "message": "Duplicate conceptId"}
        new_cause = EpilepsyCause(
            conceptId=concept_id,
            term=term,
            preferredTerm=preferred_term,
        )
        try:
            new_cause.save()
            added_causes.append(
                {
                    "concept_id": concept_id,
                    "preferredTerm": preferred_term,
                    "term": term,
                }
            )
        except Exception as e:
            errors.append(
                {
                    "conceptId": concept_id,
                    "term": term,
                    "preferredTerm": preferred_term,
                    "error": f"Error: {e}",
                }
            )
            continue
    logger.info(f"{len(added_causes)} epilepsy causes added")
    for index, cause in enumerate(added_causes):
        logger.info(f"{index + 1}. {cause['preferredTerm']} added")
    for index, error in enumerate(errors):
        logger.error(
            f'{index+1}, {error["preferredTerm"]} ({error["conceptId"]}) not added. {error["error"]}'
        )
