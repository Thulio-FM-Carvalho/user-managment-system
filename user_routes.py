from flask import render_template, request, session, flash, redirect, url_for

from helpers import FormLogin, FormUsuario, FormChangePassword
from app import app, db
from models import Usuarios
from flask_bcrypt import generate_password_hash, check_password_hash


@app.route('/auth_user', methods=['POST'])
def auth_user():
    form = FormLogin(request.form)

    usuario = Usuarios().query.filter_by(email=form.email.data).first()

    if usuario:
        senha = check_password_hash(usuario.password, form.password.data)
        if senha:
            session['usuario_logado'] = usuario.first_name
            session['user_id'] = usuario.id
            flash(usuario.first_name + ' logado com sucesso!')
            return redirect('user/dashboard')
        else:
            flash('Usuário não logado, por favor verifique sua senha.')
            return redirect(url_for('user_login'))
    else:
        flash(
            'Usuário não logado. Não identificamos o email no nosso banco de dados. Por favor verifique se o email '
            'está correto ou se você já tem cadastro.')
        return redirect(url_for('user_login'))


@app.route('/update', methods=['POST'])
def update():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        flash('Usuário não logado.')
        return redirect(url_for('user_login'))
    else:
        form = FormUsuario(request.form)

        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data

        id = session['user_id']
        user = Usuarios().query.filter_by(id=id).first()
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email

        db.session.add(user)
        db.session.commit()
        return redirect('user/dashboard')


@app.route('/create', methods=['POST'])
def create():
    form = FormUsuario(request.form)

    first_name = form.first_name.data
    last_name = form.last_name.data
    username = form.username.data
    email = form.email.data
    password = form.password.data

    usuario = Usuarios().query.filter_by(email=email).first()
    if usuario:
        flash('Endereço de email já associado a uma conta.')
        return redirect(url_for('user_login'))
    else:
        hash_password = generate_password_hash(password).decode('utf-8')
        user = Usuarios(first_name=first_name, last_name=last_name, username=username, email=email,
                        password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash("Usuário cadastrado, por favor faça seu login.")
        return redirect(url_for('user_login'))


@app.route('/user/password', methods=['POST'])
def password():
    form = FormChangePassword(request.form)
    if form.validate_on_submit():
        form_new_password = form.new_password.data
        id = session['user_id']
        user = Usuarios().query.filter_by(id=id).first()
        password_is_valid = check_password_hash(user.password, form.current_password.data)
        email_is_valid = form.email.data == user.email
        if password_is_valid and email_is_valid:
            new_password = generate_password_hash(form_new_password).decode('utf-8')

            Usuarios().query.filter_by(id=id).update(dict(password=new_password))
            db.session.commit()
        else:
            flash('Seu Email ou sua senha atual não confere.')
            return redirect(url_for('user_change_password'))
        flash('Senha atualizada!')
        return redirect(url_for('user_dashboard'))
    else:
        flash('A nova senha e a confirmação da nova senha não conferem.')
        return redirect(url_for('user_change_password'))


@app.route('/user/login', methods=['GET'])
def user_login():
    form = FormLogin()
    return render_template('user/user_login.html', form=form)


@app.route('/user/dashboard', methods=['GET'])
def user_dashboard():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        flash('Usuário não logado.')
        return redirect(url_for('/user/'))
    else:
        id = session['user_id']
        user = Usuarios().query.filter_by(id=id).first()
    return render_template('user/dashboard.html', title="Dashboard", user=user)


@app.route('/user/logout')
def user_logout():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        flash('Usuário não logado.')
        return redirect(url_for('user_login'))
    else:
        session['usuario_logado'] = None
        session['user_id'] = None
        return redirect('/')


@app.route('/user/update', methods=['GET'])
def user_update():
    form = FormUsuario()
    return render_template('user/update-profile.html', form=form)


@app.route('/user/create_account', methods=['GET'])
def user_create_account():
    form = FormUsuario()
    return render_template('user/create_account.html', form=form)


@app.route('/user/change_password', methods=['GET', 'POST'])
def user_change_password():
    form = FormChangePassword()
    return render_template('user/change_password.html', form=form)
