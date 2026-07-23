import os
import uuid

from flask import Blueprint, abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..chat.forms import MessageForm
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
    chat_form = MessageForm()
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


@products_bp.route("/<int:product_id>")
def detail_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.status != "active":
        is_owner = current_user.is_authenticated and current_user.id == product.seller_id
        is_admin = current_user.is_authenticated and current_user.is_admin
        if not (is_owner or is_admin):
            abort(404)

    return render_template("products/detail.html", product=product)


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id:
        abort(403)

    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category = form.category.data
        if form.image.data and form.image.data.filename:
            new_image = _save_product_image(form.image.data)
            if new_image:
                product.image_path = new_image
        db.session.commit()
        flash("상품이 수정되었습니다.", "success")
        return redirect(url_for("products.detail_product", product_id=product.id))

    return render_template("products/edit.html", form=form, product=product)


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id:
        abort(403)

    db.session.delete(product)
    db.session.commit()
    flash("상품이 삭제되었습니다.", "success")
    return redirect(url_for("auth.mypage"))


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
