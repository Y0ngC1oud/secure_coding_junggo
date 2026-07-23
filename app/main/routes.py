from flask import Blueprint, render_template

from ..models import Product

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    recent_products = (
        Product.query.filter_by(status="active").order_by(Product.created_at.desc()).limit(4).all()
    )
    return render_template("main/home.html", recent_products=recent_products)
