from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, NumberRange


class TransferForm(FlaskForm):
    receiver_username = StringField(
        "받는 사람 아이디", validators=[DataRequired(message="받는 사람 아이디를 입력해주세요.")]
    )
    amount = IntegerField(
        "송금 금액",
        validators=[
            DataRequired(message="송금 금액을 입력해주세요."),
            NumberRange(min=1, max=100_000_000, message="1원 이상 1억원 이하로 입력해주세요."),
        ],
    )
