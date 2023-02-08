from flask import render_template, request, session, flash, redirect, url_for
from flask_bcrypt import check_password_hash

from helpers import FormLogin, FormUsuario, FormAdmin
from main import app, db
from models import Admins, Usuarios


@app.route('/admin/login', methods=['GET'])
def admin_login():
    form = FormLogin()
    return render_template('admin/admin_login.html', form=form)


@app.route('/auth_admin', methods=['POST'])
def auth_admin():
    form = FormLogin(request.form)

    admin = Admins().query.filter_by(email=form.email.data).first()

    if admin:
        senha = check_password_hash(admin.password, form.password.data)
        if senha:
            session['admin_logado'] = admin.username
            session['admin_id'] = admin.id
            return redirect('admin/dashboard')
        else:
            flash('Usuario não logado, por favor verifique sua senha.')
            return redirect(url_for('admin_login'))
    else:
        flash(
            'Usuário não logado. Não identificamos o email no nosso banco de dados. Por favor verifique se o email '
            'está correto ou se você tem acesso a essa área.')
        return redirect(url_for('admin_login'))


@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    total_users = Usuarios().query.count()
    aproved_users = Usuarios().query.filter_by(status=1).count()
    disapproved_users = Usuarios().query.filter_by(status=0).count()
    total_admins = Admins().query.count()

    return render_template('admin/admin_dashboard.html', total_user=total_users, total_aprove=aproved_users,
                           not_total_aprove=disapproved_users, total_admin=total_admins)


@app.route('/admin/get_all_user')
def get_all_user():
    total_users = Usuarios().query.all()
    return render_template('admin/all_user.html', users=total_users)


@app.route('/admin/all_aproved_users')
def get_all_aproved_users():
    all_aproved_users = Usuarios().query.filter_by(status=1)
    return render_template('admin/all_aproved_users.html', users=all_aproved_users)


@app.route('/admin/all_unapproved_users')
def get_all_unapproved_users():
    all_unaapproved_users = Usuarios().query.filter_by(status=0)
    return render_template('admin/all_unapproved_users.html', users=all_unaapproved_users)


@app.route('/admin/get_all_admins')
def get_all_admins():
    all_admins = Admins().query.all()
    return render_template('admin/all_admins.html', admins=all_admins)


@app.route('/admin/logout')
def admin_logout():
    if 'admin_logado' not in session or session['admin_logado'] is None:
        flash('admin não logado.')
        return redirect(url_for('admin_login'))
    else:
        session['admin_logado'] = None
        session['admin_id'] = None
        return redirect('/')


@app.route('/admin/edit_user/<int:id>')
def edit_user(id):
    user = Usuarios().query.filter_by(id=id).first()

    form = FormUsuario()
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.username.data = user.username
    form.email.data = user.email

    username = user.username
    email = user.email

    return render_template("admin/edit_user_profile.html", form=form, id=id, username=username, email=email)


@app.route('/admin/edit_admin/<int:id>')
def edit_admin(id):
    admin = Admins().query.filter_by(id=id).first()

    form = FormAdmin()
    form.username.data = admin.username
    form.email.data = admin.email

    username = admin.username
    email = admin.email

    return render_template("admin/edit_admin_profile.html", form=form, id=id, username=username, email=email)


@app.route('/update_admin', methods=["POST"])
def update_admin():
    if 'admin_logado' not in session or session['admin_logado'] is None:
        flash('Administrador não logado.')
        return redirect(url_for('admin_login'))
    else:
        form = FormAdmin(request.form)

        username = form.username.data
        email = form.email.data

        id = request.form['id']
        admin = Admins().query.filter_by(id=id).first()
        admin.username = username
        admin.email = email

        db.session.add(admin)
        db.session.commit()
        return redirect('admin/get_all_admins')


@app.route('/update_user', methods=["POST"])
def update_user():
    if 'admin_logado' not in session or session['admin_logado'] is None:
        flash('Administrador não logado.')
        return redirect(url_for('admin_login'))
    else:
        form = FormUsuario(request.form)

        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data

        id = request.form['id']
        user = Usuarios().query.filter_by(id=id).first()
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email

        db.session.add(user)
        db.session.commit()
        return redirect('admin/get_all_user')


@app.route('/admin/profile')
def admin_profile():
    admin_id = session['admin_id']
    admin = Admins().query.filter_by(id=admin_id).first()
    username = admin.username
    email = admin.email
    return render_template('/admin/edit_admin_profile.html', email=email, username=username)