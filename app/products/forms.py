from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange

CATEGORY_CHOICES = [
    ("전자기기", "전자기기"),
    ("생활가전", "생활가전"),
    ("가구/인테리어", "가구/인테리어"),
    ("의류", "의류"),
    ("도서", "도서"),
    ("스포츠/레저", "스포츠/레저"),
    ("기타", "기타"),
]


class ProductForm(FlaskForm):
    name = StringField(
        "상품명", validators=[DataRequired(message="상품명을 입력해주세요."), Length(max=100)]
    )
    description = TextAreaField(
        "상품 설명", validators=[DataRequired(message="상품 설명을 입력해주세요."), Length(max=2000)]
    )
    price = IntegerField(
        "가격",
        validators=[
            DataRequired(message="가격을 입력해주세요."),
            NumberRange(min=0, max=100_000_000, message="0원 이상 1억원 이하로 입력해주세요."),
        ],
    )
    category = SelectField("카테고리", choices=CATEGORY_CHOICES, validators=[DataRequired()])
    image = FileField(
        "상품 이미지",
        validators=[
            FileAllowed(["png", "jpg", "jpeg", "gif", "webp"], message="이미지 파일만 업로드할 수 있습니다.")
        ],
    )
