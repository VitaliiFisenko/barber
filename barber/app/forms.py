import wtforms as f
from db import db_get
from flask import session

import flask_wtf as ft


class LoginForm(ft.FlaskForm):
    login = f.StringField('Логин', [f.validators.DataRequired()])
    password = f.StringField('Пароль', [f.validators.DataRequired(), f.validators.Length(min=8, max=30)])
    submit = f.SubmitField('Войти')

    def validate(self, extra_validators=None):
        valid = super().validate(extra_validators)
        query = f"""
        SELECT * FROM Buser where login='{self.login.data}';
        """
        user = db_get(query)
        if not user:
            return False
        session['current_user'] = user
        session['current_user_cart'] = db_get(f"select * from cart where Buser_id={user['id']}")
        return valid


class RegisterForm(ft.FlaskForm):
    login = f.StringField('Логин', [f.validators.DataRequired()])
    password = f.StringField('Пароль', [f.validators.DataRequired(), f.validators.Length(min=8, max=30)])
    name = f.StringField('Имя', [f.validators.Length(min=1, max=20)])
    last_name = f.StringField('Фамилия', [f.validators.Length(min=1, max=20)])
    surname = f.StringField('Отчество', [f.validators.Length(min=1, max=20)])
    phone = f.StringField('Телефон')
    email = f.StringField('Емейл', [f.validators.Length(min=8, max=30)])
    submit = f.SubmitField('Зарегестрироваться')


class OrderForm(ft.FlaskForm):
    payment_type = f.SelectField('Тип оплаты',choices=['Наличные', 'Карта'])
    name = f.StringField('Имя', [f.validators.Length(min=1, max=20)])
    last_name = f.StringField('Фамилия', [f.validators.Length(min=1, max=20)])
    surname = f.StringField('Отчество', [f.validators.Length(min=1, max=20)])
    phone = f.StringField('Телефон')
    email = f.StringField('Емейл', [f.validators.Length(min=8, max=30)])
    submit = f.SubmitField('Сделать заказ')


class StatusForm(ft.FlaskForm):
    status = f.SelectField('Статус', choices=[(1, 'Подтвержденный'), (2, 'В реализации'), (3, 'Отклонен'), (4, 'Завершен'), (5, 'Оплачен')])
    submit = f.SubmitField('Изменить статус')
