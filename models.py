# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import date
from dateutil.relativedelta import relativedelta

db = SQLAlchemy()

class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(64), nullable=True)
    name = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(64), nullable=False, default="Other")
    purchase_date = db.Column(db.Date, nullable=False)
    initial_cost = db.Column(db.Numeric(12, 2), nullable=False)
    useful_life_years = db.Column(db.Integer, nullable=False)

    def depreciated_value(self, as_of: date = None) -> float:
        if as_of is None:
            as_of = date.today()

        total_months = self.useful_life_years * 12
        delta = relativedelta(as_of, self.purchase_date)
        elapsed_months = delta.years * 12 + delta.months

        if elapsed_months <= 0:
            return float(self.initial_cost)
        if elapsed_months >= total_months:
            return 0.00

        monthly_dep = float(self.initial_cost) / total_months
        current_value = float(self.initial_cost) - (monthly_dep * elapsed_months)
        return round(current_value, 2)

    def percent_remaining(self, as_of: date = None) -> float:
        dv = self.depreciated_value(as_of)
        if not self.initial_cost:
            return 0.0
        return round((dv / float(self.initial_cost)) * 100, 1)
