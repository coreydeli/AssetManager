# forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DateField,
    DecimalField,
    IntegerField,
    SelectField,
    SubmitField
)
from wtforms.validators import DataRequired, NumberRange, Length, Optional
import re

# General list of categories
CATEGORY_CHOICES = [
    ("Electronics", "Electronics"),
    ("Furniture", "Furniture"),
    ("Appliances", "Appliances"),
    ("Tools", "Tools"),
    ("Office", "Office"),
    ("Other", "Other")
]

def strip_currency(value):
    """
    Remove any character that isn't a digit or a decimal point.
    e.g. "$1,234.56" → "1234.56"
    """
    if not isinstance(value, str):
        return value
    # Remove all except digits and dot
    return re.sub(r"[^\d.]", "", value)

class AssetForm(FlaskForm):
    serial_number = StringField(
        "Serial Number",
        validators=[Optional(), Length(max=64)]
    )

    name = StringField(
        "Item Name", validators=[DataRequired(), Length(max=128)]
    )
    purchase_date = DateField(
        "Purchase Date", validators=[DataRequired()], format="%Y-%m-%d"
    )
    initial_cost = DecimalField(
        "Initial Cost (USD)",
        validators=[DataRequired(), NumberRange(min=0)],
        filters=[strip_currency]  # apply strip_currency before validation
    )
    category = SelectField(
        "Category",
        choices=CATEGORY_CHOICES,
        validators=[DataRequired()]
    )
    useful_life_years = IntegerField(
        "Useful Life (years)", validators=[DataRequired(), NumberRange(min=1, max=50)]
    )
    submit = SubmitField("Save")
