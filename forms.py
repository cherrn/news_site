from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=100)])
    submit = SubmitField('Войти')


class FeedBackForm(FlaskForm):
    name = StringField('Name: ', validators=[DataRequired()])
    email = EmailField('Email: ', validators=[Email()])
    phoneNumber = StringField('Phone: ', validators=[DataRequired()])
    introduction = StringField('Introduction: ', validators=[DataRequired()])
    text = StringField('Text: ', validators=[DataRequired()])
    submit = SubmitField('Отправить')

class AddNewsForm(FlaskForm):
    title = StringField('Title: ', validators=[DataRequired()])
    text = StringField('Text: ', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired(), Length(min=4, max=100)])
    submit = SubmitField('Добавить')

