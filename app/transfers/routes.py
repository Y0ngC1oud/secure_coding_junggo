from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..extensions import db
from ..models import Transaction, User
from .forms import TransferForm

transfers_bp = Blueprint("transfers", __name__, url_prefix="/transfers")


@transfers_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_transfer():
    form = TransferForm()
    if form.validate_on_submit():
        identifier = form.receiver_username.data.strip()
        # 아이디로 먼저 찾고, 없으면 닉네임으로 조회 (닉네임은 중복 가능하므로 아이디를 우선함)
        receiver = User.query.filter_by(username=identifier).first()
        if receiver is None:
            receiver = User.query.filter_by(nickname=identifier).first()
        amount = form.amount.data

        if receiver is None:
            flash("존재하지 않는 사용자입니다.", "error")
        elif receiver.id == current_user.id:
            flash("본인에게는 송금할 수 없습니다.", "error")
        elif current_user.balance < amount:
            flash("잔액이 부족합니다.", "error")
        else:
            # 잔액 확인부터 차감/적립, 거래 기록까지 한 트랜잭션으로 커밋해 원자성을 보장
            current_user.balance -= amount
            receiver.balance += amount
            transaction = Transaction(sender_id=current_user.id, receiver_id=receiver.id, amount=amount)
            db.session.add(transaction)
            db.session.commit()
            flash(f"{receiver.nickname}님에게 {amount:,}원을 송금했습니다.", "success")
            return redirect(url_for("transfers.history"))

    return render_template("transfers/new.html", form=form)


@transfers_bp.route("/history")
@login_required
def history():
    transactions = (
        Transaction.query.filter(
            or_(Transaction.sender_id == current_user.id, Transaction.receiver_id == current_user.id)
        )
        .order_by(Transaction.created_at.desc())
        .all()
    )
    return render_template("transfers/history.html", transactions=transactions)
