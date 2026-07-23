from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Product, Report, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/")
@admin_required
def dashboard():
    stats = {
        "user_count": User.query.count(),
        "product_count": Product.query.count(),
        "pending_report_count": Report.query.filter_by(status="pending").count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/users")
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/<int:user_id>/status", methods=["POST"])
@admin_required
def update_user_status(user_id):
    target = User.query.get_or_404(user_id)
    new_status = request.form.get("status")
    if new_status not in ("active", "dormant", "banned"):
        abort(400)

    if target.id == current_user.id:
        flash("본인 계정 상태는 변경할 수 없습니다.", "error")
        return redirect(url_for("admin.users"))

    target.status = new_status
    db.session.commit()
    flash(f"{target.nickname}님의 상태가 '{new_status}'(으)로 변경되었습니다.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/products")
@admin_required
def products():
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=all_products)


@admin_bp.route("/products/<int:product_id>/status", methods=["POST"])
@admin_required
def update_product_status(product_id):
    product = Product.query.get_or_404(product_id)
    new_status = request.form.get("status")
    if new_status not in ("active", "blocked", "sold"):
        abort(400)

    product.status = new_status
    db.session.commit()
    flash("상품 상태가 변경되었습니다.", "success")
    return redirect(url_for("admin.products"))


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("상품이 삭제되었습니다.", "success")
    return redirect(url_for("admin.products"))


@admin_bp.route("/reports")
@admin_required
def reports():
    all_reports = Report.query.order_by(Report.created_at.desc()).all()

    target_labels = {}
    for report in all_reports:
        if report.target_type == "product":
            product = Product.query.get(report.target_id)
            target_labels[report.id] = product.name if product else "(삭제된 상품)"
        else:
            target_user = User.query.get(report.target_id)
            target_labels[report.id] = target_user.nickname if target_user else "(삭제된 사용자)"

    return render_template("admin/reports.html", reports=all_reports, target_labels=target_labels)


@admin_bp.route("/reports/<int:report_id>/resolve", methods=["POST"])
@admin_required
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = "resolved"
    db.session.commit()
    flash("신고가 처리 완료로 표시되었습니다.", "success")
    return redirect(url_for("admin.reports"))
