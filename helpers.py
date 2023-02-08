from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


class FormChangePassword(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=1, max=50)])
    current_password = PasswordField('Senha atual', validators=[DataRequired(), validators.length(min=1, max=50)])
    new_password = PasswordField("Nova senha", validators=[DataRequired(), Length(min=8, max=50)], id="password")
    confirm_password = PasswordField("Confirmar nova senha", validators=[DataRequired(), EqualTo('new_password')])
    save = SubmitField('Salvar')


class FormLogin(FlaskForm):
    email = StringField('Email', [validators.data_required(), validators.length(min=1, max=50)])
    password = PasswordField('Senha', [validators.data_required(), validators.length(min=1, max=40)])
    login = SubmitField('Login')


class FormUsuario(FlaskForm):
    first_name = StringField('Nome', [validators.data_required(), validators.length(min=1, max=50)])
    last_name = StringField('Sobrenome', [validators.data_required(), validators.length(min=1, max=50)])
    username = StringField('Nome de usuário', [validators.data_required(), validators.length(min=1, max=50)])
    email = StringField('Email', [validators.data_required(), validators.length(min=1, max=50)])
    password = PasswordField('Senha', [validators.data_required(), validators.length(min=1, max=255)])
    login = SubmitField('Salvar')


class FormAdmin(FlaskForm):
    username = StringField('Nome de usuário', [validators.data_required(), validators.length(min=1, max=50)])
    email = StringField('Email', [validators.data_required(), validators.length(min=1, max=50)])
    login = SubmitField('Salvar')
