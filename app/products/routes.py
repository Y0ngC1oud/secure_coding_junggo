import os
import uuid

from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..chat.forms import GlobalChatForm
from ..extensions import db
from ..models import Message, Product
from .forms import ProductForm

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


@products_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        image_filename = _save_product_image(form.image.data)
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            image_path=image_filename,
            seller_id=current_user.id,
        )
        db.session.add(product)
        db.session.commit()
        flash("상품이 등록되었습니다.", "success")
        return redirect(url_for("products.list_products"))

    return render_template("products/create.html", form=form)


def _save_product_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    original_name = file_storage.filename
    ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    if ext not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return None

    # 원본 파일명을 그대로 쓰지 않고 랜덤 파일명으로 저장해 경로 조작/파일명 충돌을 방지
    random_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], random_name)
    file_storage.save(save_path)
    return random_name
