from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length

from .conf import MAX_SHORT_URL_LENGTH, AVAILABLE_CHARS_FOR_SHORT_ID


class URLMapForm(FlaskForm):
    original_link = StringField(
        'Введите длинную ссылку',
        validators=(DataRequired(message='Обязательное поле'),)
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=(
            Length(
                min=0,
                max=MAX_SHORT_URL_LENGTH,
                message=f'Короткий адрес не должен превышать {MAX_SHORT_URL_LENGTH} символов'),
        )
    )
    submit = SubmitField('Создать')

    @staticmethod
    def validate_custom_id(form, field):
        if field.data and set(field.data).difference(set(AVAILABLE_CHARS_FOR_SHORT_ID)):
            raise ValidationError('Недопустимые символы у ссылки')
