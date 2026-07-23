from flask import Blueprint, render_template

from ..models import Product, Transaction, User
from ..products.forms import CATEGORY_CHOICES

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    recent_products = (
        Product.query.filter_by(status="active").order_by(Product.created_at.desc()).limit(4).all()
    )
    stats = {
        "user_count": User.query.count(),
        "product_count": Product.query.filter_by(status="active").count(),
        "transaction_count": Transaction.query.count(),
    }
    return render_template(
        "main/home.html",
        recent_products=recent_products,
        stats=stats,
        categories=CATEGORY_CHOICES,
    )
