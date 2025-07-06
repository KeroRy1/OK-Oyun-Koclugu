from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, NumberRange

class FeedbackForm(FlaskForm):
    rating = IntegerField("Puan", validators=[InputRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField("Yorum")
    submit = SubmitField("Gönder")
