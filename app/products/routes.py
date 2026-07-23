from flask import Blueprint, render_template

from ..chat.forms import GlobalChatForm
from ..models import Message, Product

products_bp = Blueprint("products", __name__, url_prefix="/products")


@products_bp.route("/")
def list_products():
    products = Product.query.filter_by(status="active").order_by(Product.created_at.desc()).all()
    messages = (
        Message.query.filter_by(receiver_id=None).order_by(Message.created_at.asc()).limit(50).all()
    )
    chat_form = GlobalChatForm()
    return render_template(
        "products/list.html", products=products, messages=messages, chat_form=chat_form
    )
