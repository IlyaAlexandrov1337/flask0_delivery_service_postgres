from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, RadioField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email


class AuthenticationForm(FlaskForm):
    mail = StringField("Email:", validators=[Email(message="Введите почту")])
    password = PasswordField("Пароль:", validators=[Length(min=8, message="Пароль должен быть не менее 8 символов")])
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    mail = StringField("Email:", validators=[Email(message="Введите почту")])
    password = PasswordField("Пароль:", validators=[Length(min=8, message="Пароль должен быть не менее 8 символов")])
    submit = SubmitField("Зарегистрироваться")


class OrderForm(FlaskForm):
    name = StringField("Ваше имя:", validators=[DataRequired("Введите имя")])
    address = StringField("Адрес:", validators=[DataRequired("Введите адрес")])
    phone = StringField("Телефон:", validators=[Length(min=10, max=11, message="Введите корректный номер")])
    submit = SubmitField("Оформить заказ")


class OutCartForm(FlaskForm):
    meal = HiddenField()
    delete = SubmitField("Удалить")


class InCartForm(FlaskForm):
    meal = HiddenField()
    submit = SubmitField("В корзину")
