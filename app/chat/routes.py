from flask import Blueprint, flash, redirect, url_for
from flask_login import current_user, login_required

from ..extensions import db, limiter
from ..models import Message
from .forms import GlobalChatForm

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


@chat_bp.route("/global", methods=["POST"])
@login_required
@limiter.limit("20 per minute")
def send_global_message():
    form = GlobalChatForm()
    if form.validate_on_submit():
        message = Message(sender_id=current_user.id, receiver_id=None, content=form.content.data)
        db.session.add(message)
        db.session.commit()
    else:
        flash("메시지를 입력해주세요.", "error")
    return redirect(url_for("products.list_products"))
