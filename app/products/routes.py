import os
import uuid

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..chat.forms import MessageForm
from ..extensions import db
from ..models import Message, Product, Transaction
from .forms import CATEGORY_CHOICES, ProductForm

products_bp = Blueprint("products", __name__, url_prefix="/products")


@products_bp.route("/")
def list_products():
    products = Product.query.filter_by(status="active").order_by(Product.created_at.desc()).all()
    messages = (
        Message.query.filter_by(receiver_id=None).order_by(Message.created_at.asc()).limit(50).all()
    )
    chat_form = MessageForm()
    return render_template(
        "products/list.html",
        products=products,
        messages=messages,
        chat_form=chat_form,
        categories=CATEGORY_CHOICES,
    )


@products_bp.route("/search")
def search_products():
    keyword = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    query = Product.query.filter_by(status="active")
    if keyword:
        query = query.filter(Product.name.ilike(f"%{keyword}%"))
    if category:
        query = query.filter_by(category=category)

    products = query.order_by(Product.created_at.desc()).all()
    return render_template(
        "products/search.html",
        products=products,
        categories=CATEGORY_CHOICES,
        keyword=keyword,
        selected_category=category,
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

    if product.status == "blocked":
        is_owner = current_user.is_authenticated and current_user.id == product.seller_id
        is_admin = current_user.is_authenticated and current_user.is_admin
        if not (is_owner or is_admin):
            abort(404)

    return render_template("products/detail.html", product=product)


@products_bp.route("/<int:product_id>/buy", methods=["POST"])
@login_required
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.seller_id == current_user.id:
        flash("본인이 등록한 상품은 구매할 수 없습니다.", "error")
        return redirect(url_for("products.detail_product", product_id=product.id))

    if product.status != "active":
        flash("이미 판매되었거나 구매할 수 없는 상품입니다.", "error")
        return redirect(url_for("products.detail_product", product_id=product.id))

    if current_user.balance < product.price:
        flash("잔액이 부족합니다.", "error")
        return redirect(url_for("products.detail_product", product_id=product.id))

    seller = product.seller
    # 잔액 차감/적립, 거래 기록 생성, 상품 상태 변경을 하나의 트랜잭션으로 커밋해 원자성을 보장
    current_user.balance -= product.price
    seller.balance += product.price
    product.status = "sold"
    db.session.add(Transaction(sender_id=current_user.id, receiver_id=seller.id, amount=product.price))
    db.session.commit()

    flash(f"'{product.name}' 상품을 {product.price:,}원에 구매했습니다.", "success")
    return redirect(url_for("products.detail_product", product_id=product.id))


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
