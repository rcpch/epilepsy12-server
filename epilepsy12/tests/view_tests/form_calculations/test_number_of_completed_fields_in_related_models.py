""" Tests for `number_of_completed_fields_in_related_models` fn.

MultiaxialDiagnosis
    - `Episode`
            for episode in Episodes:
                EXPECTED_SCORE += 5 (if at least one episode is epileptic)
                'seizure_onset_date'
                'seizure_onset_date_confidence'
                'episode_definition'
                'has_description_of_the_episode_or_episodes_been_gathered'
                'epilepsy_or_nonepilepsy_status'

                if episode.has_description_of_the_episode_or_episodes_been_gathered:
                    EXPECTED_SCORE += 1
                    description
                if episode.epilepsy_or_nonepilepsy_status == "E":
                    EXPECTED_SCORE += 1

                    if episode.epileptic_seizure_onset_type == "GO":
                        # 'generalised' onset: essential fields
                        # 'epileptic_generalised_onset'
                        EXPECTED_SCORE += 1
                    elif episode.epileptic_seizure_onset_type == "FO":
                        # focal onset
                        # minimum score is laterality
                        EXPECTED_SCORE += 1
                    else:
                        # either unclassified or unknown onset
                        # no further score
                        EXPECTED_SCORE += 0
                elif episode.epilepsy_or_nonepilepsy_status == "NE":
                    # nonepileptic seizure - essential fields:
                    # nonepileptic_seizure_unknown_onset
                    # nonepileptic_seizure_type
                    # AND ONE of behavioural/migraine/misc/paroxysmal/sleep related/syncope - essential fields:
                    # nonepileptic_seizure_behavioural or
                    # nonepileptic_seizure_migraine or
                    # nonepileptic_seizure_miscellaneous or
                    # nonepileptic_seizure_paroxysmal or
                    # nonepileptic_seizure_sleep
                    # nonepileptic_seizure_syncope
                    
                    if episode.nonepileptic_seizure_type == "Oth":
                        EXPECTED_SCORE += 2
                    else:
                        EXPECTED_SCORE += 3
                elif episode.epilepsy_or_nonepilepsy_status == "U":
                    # uncertain status
                    EXPECTED_SCORE += 0

    - `Syndrome`
        for syndrome in Syndromes:
            EXPECTED_SCORE += 2
            "syndrome_diagnosis_date"
            "syndrome__syndrome_name"

    - `Comorbidity`
        for comorbidity in Comorbidities:
            EXPECTED_SCORE += 2
            comorbidity_diagnosis_date"
            "comorbidity__comorbidityentity__conceptId"
Management
Registration
    
"""

# python imports
import pytest
from datetime import date
import random

# django imports
from django.urls import reverse

# E12 imports
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    Case,
    Registration,
    FirstPaediatricAssessment,
    EpilepsyContext,
    Assessment,
    Investigations,
    Management,
    MultiaxialDiagnosis,
    Episode,
)
from epilepsy12.common_view_functions.recalculate_form_generate_response import (
    number_of_completed_fields_in_related_models,
    completed_fields,
)
from epilepsy12.constants import (
    CHRONICITY,
    OPT_OUT_UNCERTAIN,
    SEVERITY,
    NEUROPSYCHIATRIC,
    EPILEPSY_DIAGNOSIS_STATUS,
    EPILEPSY_SEIZURE_TYPE,
    GENERALISED_SEIZURE_TYPE,
    NON_EPILEPSY_SEIZURE_TYPE,
    NON_EPILEPSY_SEIZURE_ONSET,
    NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS,
    DATE_ACCURACY,
    EPISODE_DEFINITION,
)


def get_random_answers_update_counter(answer_set: dict, counter: int):
    """Helper fn to return a random answer (None or valid value), and update counter of expected score.

    Args:
        answer_set (dict): current answer_set
        counter (int): current counter state

    Returns:
       answer_set (dict) : answer_set which can be provided to factory constructor
       counter (int): updated counter
    """

    for key, val in answer_set.items():
        answer = random.choice([None, val])
        answer_set[key] = answer

        # update counter
        if answer is not None:
            counter += 1

    return answer_set, counter


@pytest.mark.django_db
def test_related_model_fields_count_all_episode_fully_completed(
    e12_case_factory, e12_episode_factory, GOSH
):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=multiaxialdiagnosis) returns correct counter when all Episode fields have an answer.
    """

    CASE = e12_case_factory(
        first_name=f"temp_child_{GOSH.OrganisationName}",
        organisations__organisation=GOSH,
    )
    multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis
    return_value = number_of_completed_fields_in_related_models(multiaxial_diagnosis)
    assert (
        return_value == 0
    ), f"Empty episode, `number_of_completed_fields_in_related_models(multiaxial_diagnosis)` should return 0. Instead returned {return_value}"

    # Specific answer doesn't matter for these fields - just need an answer
    COMMON_FIELDS = {
        "seizure_onset_date": date(2023, 1, 1),
        "seizure_onset_date_confidence": DATE_ACCURACY[0][0],
        "episode_definition": EPISODE_DEFINITION[0][0],
        "has_description_of_the_episode_or_episodes_been_gathered": True,
        "description": "The seizure happened when child was watching TV",
    }

    EPILEPTIC_FOCAL_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[0][0],
        "focal_onset_left": True,
        "focal_onset_impaired_awareness": True,  # should not be counted!
    }
    EPILEPTIC_GENERALISED_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[1][0],
        "epileptic_generalised_onset": GENERALISED_SEIZURE_TYPE[0][0],
    }
    EPILEPTIC_UNKNOWN_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[2][0],
    }
    EPILEPTIC_UNCLASSIFIED_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[3][0],
    }
    NON_EPILEPTIC = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[1][0],
        "nonepileptic_seizure_type": NON_EPILEPSY_SEIZURE_TYPE[0][0],
        "nonepileptic_seizure_unknown_onset": NON_EPILEPSY_SEIZURE_ONSET[0][0],
        "nonepileptic_seizure_behavioural": NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS[0][
            0
        ],
    }
    UNCERTAIN = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[2][0],
    }

    # These are each answer sets which, combined with COMMON_FIELDS, will create a fully completed episode
    SEIZURE_TYPE_OPTIONS = [
        EPILEPTIC_FOCAL_ONSET,
        EPILEPTIC_GENERALISED_ONSET,
        EPILEPTIC_UNKNOWN_ONSET,
        EPILEPTIC_UNCLASSIFIED_ONSET,
        NON_EPILEPTIC,
        UNCERTAIN,
    ]

    # For each SEIZURE_TYPE_OPTION, create an Episode with COMMON_FIELDS and that SEIZURE_TYPE, make assertion
    factory_attributes = {**COMMON_FIELDS}
    for SEIZURE_TYPE in SEIZURE_TYPE_OPTIONS:
        episode = e12_episode_factory(
            multiaxial_diagnosis=multiaxial_diagnosis,
            **factory_attributes,
            **SEIZURE_TYPE,
        )

        return_value = number_of_completed_fields_in_related_models(
            multiaxial_diagnosis
        )

        expected_value = len(factory_attributes) + len(SEIZURE_TYPE)

        # DON'T COUNT OTHER RADIO BUTTONS FOR FOCAL ONSET
        if "focal_onset_impaired_awareness" in SEIZURE_TYPE:
            expected_value -= 1

        assert (
            return_value == expected_value
        ), f"Fully completed episodes run through `number_of_completed_fields_in_related_models(multiaxial_diagnosis)`. Expected {expected_value=} but received {return_value=}. Inserted Episode answer fields were: {factory_attributes}+{SEIZURE_TYPE}"

        # Reset for next seizure type
        episode.delete()


@pytest.mark.django_db
def test_related_model_fields_count_all_episode_random_answers(
    e12_case_factory, e12_episode_factory, GOSH
):
    """
    Simulating number_of_completed_fields_in_related_models(model_instance=multiaxialdiagnosis) returns correct counter when Episode fields' answers are randomly either valid value or None.
    """

    counter = 0

    # Specific answer doesn't matter for these fields - just need an answer
    COMMON_FIELDS = {
        "seizure_onset_date": date(2023, 1, 1),
        "seizure_onset_date_confidence": DATE_ACCURACY[0][0],
        "episode_definition": EPISODE_DEFINITION[0][0],
        "has_description_of_the_episode_or_episodes_been_gathered": True,
        "description": "The seizure happened when child was watching TV",
    }

    EPILEPTIC_FOCAL_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[0][0],
        "focal_onset_left": True,
        "focal_onset_impaired_awareness": True,  # should not be counted!
    }
    EPILEPTIC_GENERALISED_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[1][0],
        "epileptic_generalised_onset": GENERALISED_SEIZURE_TYPE[0][0],
    }
    EPILEPTIC_UNKNOWN_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[2][0],
    }
    EPILEPTIC_UNCLASSIFIED_ONSET = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[0][0],
        "epileptic_seizure_onset_type": EPILEPSY_SEIZURE_TYPE[3][0],
    }
    NON_EPILEPTIC = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[1][0],
        "nonepileptic_seizure_type": NON_EPILEPSY_SEIZURE_TYPE[0][0],
        "nonepileptic_seizure_unknown_onset": NON_EPILEPSY_SEIZURE_ONSET[0][0],
        "nonepileptic_seizure_behavioural": NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS[0][
            0
        ],
    }
    UNCERTAIN = {
        "epilepsy_or_nonepilepsy_status": EPILEPSY_DIAGNOSIS_STATUS[2][0],
    }

    SEIZURE_TYPE_OPTIONS = [
        EPILEPTIC_FOCAL_ONSET,
        EPILEPTIC_GENERALISED_ONSET,
        EPILEPTIC_UNKNOWN_ONSET,
        EPILEPTIC_UNCLASSIFIED_ONSET,
        NON_EPILEPTIC,
        UNCERTAIN,
    ]

    # Get random answer set for common fields
    COMMON_FIELDS, counter = get_random_answers_update_counter(
        answer_set=COMMON_FIELDS, counter=counter
    )

    # Create 5 randomly filled episodes, for each seizure type - ensures covers various different scenarios.
    for _ in range(5):
        for SEIZURE_TYPE in SEIZURE_TYPE_OPTIONS:
            SEIZURE_TYPE, expected_value = get_random_answers_update_counter(
                answer_set=SEIZURE_TYPE, counter=counter
            )

            # DON'T COUNT OTHER RADIO BUTTONS FOR FOCAL ONSET, regardless of answer
            if SEIZURE_TYPE.get("focal_onset_impaired_awareness") is not None:
                expected_value -= 1

            factory_attributes = {**COMMON_FIELDS, **SEIZURE_TYPE}

            # Need a case to make an episode
            CASE = e12_case_factory(
                first_name=f"temp_child_{GOSH.OrganisationName}",
                organisations__organisation=GOSH,
            )
            multiaxial_diagnosis = CASE.registration.multiaxialdiagnosis

            episode = e12_episode_factory(
                multiaxial_diagnosis=multiaxial_diagnosis,
                **factory_attributes,
            )

            return_value = number_of_completed_fields_in_related_models(
                multiaxial_diagnosis
            )

            assert (
                return_value == expected_value
            ), f"Randomly completed episodes run through `number_of_completed_fields_in_related_models(multiaxial_diagnosis)`. Expected {expected_value=} but received {return_value=}. Inserted Episode answer fields: {factory_attributes}+{SEIZURE_TYPE}"

            # Reset for next seizure type
            episode.delete()

