from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_, or_

from ..extensions import db, limiter
from ..models import Message, User
from .forms import MessageForm

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


@chat_bp.route("/global", methods=["POST"])
@login_required
@limiter.limit("20 per minute")
def send_global_message():
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(sender_id=current_user.id, receiver_id=None, content=form.content.data)
        db.session.add(message)
        db.session.commit()
    else:
        flash("메시지를 입력해주세요.", "error")
    return redirect(url_for("products.list_products"))


@chat_bp.route("/inbox")
@login_required
def inbox():
    direct_messages = (
        Message.query.filter(
            Message.receiver_id.isnot(None),
            or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id),
        )
        .order_by(Message.created_at.desc())
        .all()
    )

    partners = {}
    for message in direct_messages:
        partner = message.receiver if message.sender_id == current_user.id else message.sender
        if partner.id not in partners:
            partners[partner.id] = {"user": partner, "last_message": message}

    return render_template("chat/inbox.html", conversations=partners.values())


@chat_bp.route("/<int:user_id>", methods=["GET", "POST"])
@login_required
def conversation(user_id):
    partner = User.query.get_or_404(user_id)
    if partner.id == current_user.id:
        abort(404)

    form = MessageForm()
    if form.validate_on_submit():
        message = Message(sender_id=current_user.id, receiver_id=partner.id, content=form.content.data)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for("chat.conversation", user_id=partner.id))

    messages = (
        Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == partner.id),
                and_(Message.sender_id == partner.id, Message.receiver_id == current_user.id),
            )
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    return render_template("chat/conversation.html", partner=partner, messages=messages, form=form)
