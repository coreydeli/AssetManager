# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from config import DevelopmentConfig
from models import db, Asset
from datetime import datetime
from forms import AssetForm

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    # Register the USD filter
    @app.template_filter()
    def usd(value):
        """
        Format a numeric value as USD, e.g. 1234.5 → "$1,234.50"
        """
        try:
            amount = float(value)
        except (ValueError, TypeError):
            return value
        return "${:,.2f}".format(amount)

    db.init_app(app)

    # Flask-Migrate setup
    from flask_migrate import Migrate
    migrate = Migrate(app, db)

    @app.route("/hello")
    def hello():
        return "<h1>👋 Hello, world!</h1>"

    @app.route("/")
    def index():
        assets = Asset.query.order_by(Asset.purchase_date.desc()).all()
        today = datetime.today().date()
        return render_template("index.html", assets=assets, today=today)

    @app.route("/asset/add", methods=["GET", "POST"])
    def add_asset():
        form = AssetForm()
        if form.validate_on_submit():
            new_asset = Asset(
                serial_number=form.serial_number.data,
                name=form.name.data,
                category=form.category.data,
                purchase_date=form.purchase_date.data,
                initial_cost=form.initial_cost.data,
                useful_life_years=form.useful_life_years.data
            )
            db.session.add(new_asset)
            db.session.commit()
            flash("Asset added successfully.", "success")
            return redirect(url_for("index"))
        return render_template("add_asset.html", form=form)

    @app.route("/asset/<int:asset_id>/edit", methods=["GET", "POST"])
    def edit_asset(asset_id):
        asset = Asset.query.get_or_404(asset_id)
        form = AssetForm(obj=asset)
        if form.validate_on_submit():
            asset.serial_number = form.serial_number.data
            asset.name = form.name.data
            asset.category = form.category.data
            asset.purchase_date = form.purchase_date.data
            asset.initial_cost = form.initial_cost.data
            asset.useful_life_years = form.useful_life_years.data
            db.session.commit()
            flash("Asset updated.", "success")
            return redirect(url_for("index"))
        return render_template("edit_asset.html", form=form, asset=asset)

    @app.route("/asset/<int:asset_id>/delete", methods=["POST"])
    def delete_asset(asset_id):
        asset = Asset.query.get_or_404(asset_id)
        db.session.delete(asset)
        db.session.commit()
        flash("Asset deleted.", "warning")
        return redirect(url_for("index"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001)
