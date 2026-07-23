from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Product, Report, User
from .forms import ReportForm

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/product/<int:product_id>", methods=["GET", "POST"])
@login_required
def report_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.seller_id == current_user.id:
        flash("본인이 등록한 상품은 신고할 수 없습니다.", "error")
        return redirect(url_for("products.detail_product", product_id=product.id))

    already_reported = Report.query.filter_by(
        reporter_id=current_user.id, target_type="product", target_id=product.id
    ).first()
    if already_reported:
        flash("이미 신고한 상품입니다.", "error")
        return redirect(url_for("products.detail_product", product_id=product.id))

    form = ReportForm()
    if form.validate_on_submit():
        report = Report(
            reporter_id=current_user.id,
            target_type="product",
            target_id=product.id,
            reason=form.reason.data,
        )
        db.session.add(report)
        db.session.commit()

        report_count = Report.query.filter_by(target_type="product", target_id=product.id).count()
        if report_count >= current_app.config["REPORT_THRESHOLD"] and product.status == "active":
            product.status = "blocked"
            db.session.commit()
            flash("신고가 누적되어 해당 상품이 차단되었습니다.", "info")

        flash("신고가 접수되었습니다.", "success")
        return redirect(url_for("products.detail_product", product_id=product.id))

    return render_template(
        "reports/report_form.html", form=form, target_label=f"상품: {product.name}"
    )


@reports_bp.route("/user/<int:user_id>", methods=["GET", "POST"])
@login_required
def report_user(user_id):
    target_user = User.query.get_or_404(user_id)

    if target_user.id == current_user.id:
        flash("본인을 신고할 수 없습니다.", "error")
        return redirect(url_for("main.home"))

    already_reported = Report.query.filter_by(
        reporter_id=current_user.id, target_type="user", target_id=target_user.id
    ).first()
    if already_reported:
        flash("이미 신고한 사용자입니다.", "error")
        return redirect(url_for("main.home"))

    form = ReportForm()
    if form.validate_on_submit():
        report = Report(
            reporter_id=current_user.id,
            target_type="user",
            target_id=target_user.id,
            reason=form.reason.data,
        )
        db.session.add(report)
        db.session.commit()

        report_count = Report.query.filter_by(target_type="user", target_id=target_user.id).count()
        if report_count >= current_app.config["REPORT_THRESHOLD"] and target_user.status == "active":
            target_user.status = "dormant"
            db.session.commit()
            flash("신고가 누적되어 해당 사용자가 휴면 처리되었습니다.", "info")

        flash("신고가 접수되었습니다.", "success")
        return redirect(url_for("main.home"))

    return render_template(
        "reports/report_form.html", form=form, target_label=f"사용자: {target_user.nickname}"
    )
