from datetime import date
from random import randint

from django import forms
from django.conf import settings
from django.forms import ValidationError
import nhs_number

from ..models import Case, Organisation
from ..constants import *
from ..general_functions import is_valid_postcode, return_random_postcode


class CaseForm(forms.ModelForm):

    unknown_postcode = forms.CharField(required=False)

    first_name = forms.CharField(
        help_text="Enter the first name.",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First name"}
        ),
        required=True,
    )
    surname = forms.CharField(
        help_text="Enter the surname.",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Surname"}
        ),
        required=True,
    )
    date_of_birth = forms.DateField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Date of Birth",
                "type": "date",
            }
        ),
        required=True,
    )
    sex = forms.ChoiceField(
        choices=SEX_TYPE,
        widget=forms.Select(attrs={"class": "ui rcpch dropdown"}),
        required=True,
    )
    nhs_number = forms.CharField(
        help_text="Enter the NHS Number. This is 10 digits long.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "NHS Number",
                "type": "text",
                "data-mask": "000 000 0000",
            }
        ),
        required=False,
    )
    unique_reference_number = forms.CharField(
        help_text="Enter the Unique Reference Number (URN).",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "URN", "type": "text"}
        ),
        required=False,
    )

    postcode = forms.CharField(
        help_text="Enter the postcode.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Postcode",
                "type": "text",
            }
        ),
        required=True,
    )
    ethnicity = forms.ChoiceField(
        choices=ETHNICITIES,
        widget=forms.Select(attrs={"class": "ui rcpch dropdown"}),
        required=True,
    )
    locked_at = forms.DateTimeField(help_text="Time record locked.", required=False)
    locked_by = forms.CharField(help_text="User who locked the record", required=False)

    def __init__(self, *args, **kwargs) -> None:
        self.organisation_id = kwargs.pop(
            "organisation_id", None
        )  # This is the organisation_id
        super(CaseForm, self).__init__(*args, **kwargs)
        self.existing_nhs_number = self.instance.nhs_number
        self.fields["ethnicity"].widget.attrs.update({"class": "ui rcpch dropdown"})
        if Organisation.objects.get(id=self.organisation_id).ods_code == "RGT1W":
            # this is Jersey - hide the NHS number field
            self.fields["nhs_number"].widget = forms.HiddenInput()
            self.fields["nhs_number"].required = False
            self.fields["unique_reference_number"].required = True

        # Check if DEBUG is True and set the initial value conditionally
        if settings.DEBUG:
            self.fields["first_name"].initial = "Bob"
            self.fields["surname"].initial = "Dylan"
            self.fields["date_of_birth"].initial = date(
                randint(2005, 2021), randint(1, 12), randint(1, 28)
            )
            self.fields["postcode"].initial = return_random_postcode(
                country_boundary_identifier="E01000001"
            )
            if Organisation.objects.get(id=self.organisation_id).ods_code == "RGT1W":
                # this is Jersey
                self.fields["unique_reference_number"].initial = randint(1000, 9999)
            else:
                self.fields["nhs_number"].initial = nhs_number.generate()[0]

    class Meta:
        model = Case
        fields = [
            "first_name",
            "surname",
            "date_of_birth",
            "sex",
            "nhs_number",
            "postcode",
            "ethnicity",
            "unknown_postcode",
        ]

    def clean_postcode(self):
        postcode = self.cleaned_data["postcode"]

        if is_valid_postcode(postcode=postcode):
            return postcode

        raise ValidationError("Invalid postcode")

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data["date_of_birth"]
        today = date.today()
        if date_of_birth > today:
            raise ValidationError("Date of birth cannot be in the future.")
        else:
            return date_of_birth

    def clean_nhs_number(self):
        # remove spaces
        organisation = Organisation.objects.get(id=self.organisation_id)
        if organisation.ods_code == "RGT1W":
            nhs_number = None
            return nhs_number

        formatted_nhs_number = (
            str(self.cleaned_data["nhs_number"]).replace(" ", "").zfill(10)
        )

        # ensure NHS number is unique in the database
        if self.existing_nhs_number is not None:
            # this form is updating an existing NHS number
            if formatted_nhs_number != str(self.existing_nhs_number):
                # the new number does not match the one stored
                if Case.objects.filter(nhs_number=formatted_nhs_number).exists():
                    raise ValidationError("NHS Number already taken!")
        else:
            # this is a new form - check this number is unique in the database
            if Case.objects.filter(nhs_number=formatted_nhs_number).exists():
                raise ValidationError("NHS Number already taken!")

        # check NHS number is valid
        validity = nhs_number.is_valid(formatted_nhs_number)
        if validity:
            return formatted_nhs_number
        else:
            raise ValidationError(f"{formatted_nhs_number} is not a valid NHS number")

    def clean(self):
        cleaned_data = super().clean()
        nhs_number = cleaned_data.get("nhs_number")
        unique_reference_number = cleaned_data.get("unique_reference_number")
        organisation = Organisation.objects.get(id=self.organisation_id)
        if organisation.ods_code == "RGT1W":
            if unique_reference_number is None:
                raise ValidationError("URN is a mandatory field.")
            if self.instance.unique_reference_number:
                # there is an existing URN
                if unique_reference_number != self.instance.unique_reference_number:
                    # the new URN does not match the one stored
                    if Case.objects.filter(
                        unique_reference_number=unique_reference_number
                    ).exists():
                        raise ValidationError("Unique Reference Number already taken!")
            else:
                # this is a new form - check this number is unique in the database
                if Case.objects.filter(
                    unique_reference_number=self.instance.unique_reference_number
                ).exists():
                    raise ValidationError("Unique Reference Number already taken!")
        else:
            # this is England or Wales - NHS numbers are used
            # validation of NHS number is done in the clean_nhs_number method
            if nhs_number is None:
                raise ValidationError("NHS Number is a mandatory field.")

        return cleaned_data
