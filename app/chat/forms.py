from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class GlobalChatForm(FlaskForm):
    content = StringField(
        "메시지", validators=[DataRequired(message="메시지를 입력해주세요."), Length(max=500)]
    )
