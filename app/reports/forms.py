from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Length


class ReportForm(FlaskForm):
    reason = TextAreaField(
        "신고 사유", validators=[DataRequired(message="신고 사유를 입력해주세요."), Length(max=300)]
    )
