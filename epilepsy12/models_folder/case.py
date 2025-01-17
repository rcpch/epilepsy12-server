# python
import logging
from datetime import date

# django
from django.contrib.gis.db import models
from django.contrib.gis.db.models import CharField, DateField, PointField
from django.contrib.gis.geos import Point
from django.conf import settings

# 3rd party
from simple_history.models import HistoricalRecords

# epilepsy12
from .help_text_mixin import HelpTextMixin
from ..constants import (
    SEX_TYPE,
    ETHNICITIES,
    UNKNOWN_POSTCODES_NO_SPACES,
    CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING,
    CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT,
    CAN_CONSENT_TO_AUDIT_PARTICIPATION,
)
from ..general_functions import (
    imd_for_postcode,
    coordinates_for_postcode,
    stringify_time_elapsed,
)
from .time_and_user_abstract_base_classes import *

# Logging setup
logger = logging.getLogger(__name__)


class Case(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class holds information about each child or young person
    Each case is unique
    """

    locked = models.BooleanField(
        """
        This determines if the case is locked from editing
        Cases can be locked under either of 2 sets of circumstances
        1. The child has opted out of the audit 
        - here all data relating to the child's ID is set to None but the ID retained.
        - in the UI, blank spaces in the case_list are rendered as ######
        2. All the fields for the child have been completed and the user has indicated the child is ready for submission.
        - The upload button in the UI is enabled up until the submission deadline to toggle the locked status
        3. The submission deadline has passed. The case is locked, irrespective of if fields are complete are not.
        """
        "Locked",
        default=False,
        blank=True,
        null=True,
    )
    locked_at = models.DateTimeField("Date record locked", null=True, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="locked by",
        null=True,
        blank=True,
    )
    nhs_number = models.CharField(  # the NHS number for England and Wales
        "NHS Number", unique=True, blank=True, null=True, max_length=10
    )
    first_name = CharField(
        "First name",
        max_length=100,
        blank=True,
        null=True,
    )
    surname = CharField(
        "Surname",
        max_length=100,
        blank=True,
        null=True,
    )
    sex = models.IntegerField(
        choices=SEX_TYPE,
        blank=True,
        null=True,
    )
    date_of_birth = DateField(
        "date of birth (YYYY-MM-DD)",
        blank=True,
        null=True,
    )
    postcode = CharField(
        "postcode",
        max_length=8,
        blank=True,
        null=True,
    )

    location_wgs = PointField(
        help_text="longitude and latitude of the postcode as British National Grid (BNG)",
        srid=27700,
        null=True,
        blank=True,
    )

    location_bng = PointField(
        help_text="longitude and latitude of the postcode as British National Grid (BNG)",
        srid=27700,
        null=True,
        blank=True,
    )

    location_wgs84 = PointField(
        help_text="longitude and latitude of the postcode as WGS 84",
        srid=4326,
        null=True,
        blank=True,
    )

    ethnicity = CharField(max_length=4, choices=ETHNICITIES, blank=True, null=True)

    index_of_multiple_deprivation_quintile = models.PositiveSmallIntegerField(
        # this is a calculated field - it relies on the availability of the Deprivare server running
        # A quintile is calculated on save and persisted in the database
        "index of multiple deprivation calculated from MySociety data.",
        blank=True,
        editable=False,
        null=True,
    )

    history = HistoricalRecords()

    # relationships
    organisations = models.ManyToManyField(
        "epilepsy12.Organisation",
        through="Site",
        related_name="cases",
        through_fields=("case", "organisation"),
    )

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    def age_days(self, today_date=date.today()):
        """
        Returns the age of the patient in years, months and days
        This is a calculated field
        Date of birth is required
        Today's date is optional and defaults to date.today()
        """
        # return stringify_time_elapsed(self.date_of_birth, today_date)
        return (today_date - self.date_of_birth).days

    def age(self, today_date=date.today()):
        """
        Returns the age of the patient in years, months and days
        This is a calculated field
        Date of birth is required
        Today's date is optional and defaults to date.today()
        """
        return stringify_time_elapsed(self.date_of_birth, today_date)
    
    def editable(self):
        return not self.locked and (self.registration and self.registration.days_remaining_before_submission > 0)

    def save(self, *args, **kwargs) -> None:
        # calculate the index of multiple deprivation quintile if the postcode is present
        # Skips the calculation if the postcode is on the 'unknown' list
        if self.postcode:
            if (
                str(self.postcode).replace(" ", "").replace("-", "")
                not in UNKNOWN_POSTCODES_NO_SPACES
            ):
                # capitalize all characters, remove dashes and spaces
                self.postcode = (
                    str(self.postcode).replace(" ", "").replace("-", "").upper()
                )

                # get IMD for postcode from census platform: note, assumes postcode is valid
                try:
                    self.index_of_multiple_deprivation_quintile = imd_for_postcode(
                        self.postcode
                    )
                except Exception as error:
                    # Deprivation score not persisted if deprivation score server down
                    self.index_of_multiple_deprivation_quintile = None
                    logger.exception(
                        f"Cannot calculate deprivation score for {self.postcode}: {error}"
                    )
                    pass

                # update the longitude and latitude
                """
                The SRID (Spatial Reference System Identifier) 27700 refers to the British National Grid (BNG), a common system used for mapping in the UK. It uses Eastings and Northings, rather than longitude & latitude.
                This system is different from the more common geographic coordinate systems like WGS 84 (SRID 4326), which is used by most global datasets including GPS and many web APIs.
                Coordinates from the ONS data therefore need transforming from WGS 84 (SRID 4326) to British National Grid (SRID 27700).
                Both are included here and stored in the model, as the shape files for the UK health boundaries are produced as BNG, rather than WGS84.
                """
                try:
                    # Fetch the coordinates (WGS 84)
                    lon, lat = coordinates_for_postcode(postcode=self.postcode)

                    # Create a Point in WGS 84
                    point_wgs84 = Point(lon, lat, srid=4326)
                    # Assign the transformed point to self.location
                    self.location_wgs84 = point_wgs84

                    # Transform to British National Grid (SRID 27700) - this has Eastings and Northings, rather than longitude and latitude.
                    point_bng = point_wgs84.transform(27700, clone=True)

                    # Assign the transformed point to self.location
                    self.location_bng = point_bng

                except Exception as error:
                    self.location_wgs84 = None
                    self.location_bng = None
                    logger.exception(
                        f"Cannot get longitude and latitude for {self.postcode}: {error}"
                    )
            else:
                # if the IMD quintile has previously been added and postcode now unknown, set
                # index_of_multiple_deprivation_quintile back to None
                self.index_of_multiple_deprivation_quintile = None
                self.location_wgs84 = None
                self.location_bng = None

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Deleting a Case involves deleting any registrations associated that exist first
        try:
            self.registration.delete()
        except:
            pass
        super(Case, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        # custom permissions for Case class
        permissions = [
            CAN_LOCK_CHILD_CASE_DATA_FROM_EDITING,
            CAN_UNLOCK_CHILD_CASE_DATA_FROM_EDITING,
            CAN_OPT_OUT_CHILD_FROM_INCLUSION_IN_AUDIT,
            CAN_CONSENT_TO_AUDIT_PARTICIPATION,
        ]
        ordering = ["surname"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.surname}"
