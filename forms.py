from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class FeedbackForm(FlaskForm):
    rating = IntegerField("Puan (1–5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField("Yorum", validators=[DataRequired()])
    submit = SubmitField("Gönder")
