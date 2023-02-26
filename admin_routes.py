from flask import render_template, request, session, flash, redirect, url_for
from flask_bcrypt import check_password_hash, generate_password_hash

from helpers import FormLogin, FormUsuario, FormAdmin
from main import app, db
from models import Admins, Usuarios


@app.route('/admin/create_account', methods=['GET'])
def admin_create_account():
    form = FormAdmin()
    return render_template('admin/admin_create_account.html', form=form)


@app.route('/admin/add_account_user', methods=['GET'])
def add_account_user():
    form = FormUsuario()
    previous_page = request.args['previous_page']
    return render_template('admin/user_create_account.html', form=form, page=previous_page)


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
            flash('Logado com sucesso!', 'success')
            session['admin_logado'] = admin.username
            session['admin_id'] = admin.id
            return redirect('admin/dashboard')
        else:
            flash('Usuario não logado, por favor verifique sua senha.', 'warning')
            return redirect(url_for('admin_login'))
    else:
        flash(
            'Usuário não logado. Não identificamos o email no nosso banco de dados. Por favor verifique se o email '
            'está correto ou se você tem acesso a essa área.', 'warning')
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
    page = "get_all_user"
    return render_template('admin/all_user.html', users=total_users, page=page)


@app.route('/admin/all_aproved_users')
def get_all_aproved_users():
    all_aproved_users = Usuarios().query.filter_by(status=1)
    page = "get_all_aproved_users"
    return render_template('admin/all_aproved_users.html', users=all_aproved_users, page=page)


@app.route('/admin/all_unapproved_users')
def get_all_unapproved_users():
    all_unaapproved_users = Usuarios().query.filter_by(status=0)
    page = "get_all_unapproved_users"
    return render_template('admin/all_unapproved_users.html', users=all_unaapproved_users, page=page)


@app.route('/admin/get_all_admins')
def get_all_admins():
    all_admins = Admins().query.all()
    return render_template('admin/all_admins.html', admins=all_admins)


@app.route('/admin/logout')
def admin_logout():
    if 'admin_logado' not in session or session['admin_logado'] is None:
        flash('admin não logado.', 'warning')
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
    status = user.status

    if status == 1:
        form.status.data = "True"
    else:
        form.status.data = "False"

    previous_page = request.args['previous_page']

    return render_template("admin/edit_user_profile.html", form=form, id=id, username=username, email=email,
                           page=previous_page)


@app.route('/admin/edit_admin/<int:id>')
def edit_admin(id):
    admin = Admins().query.filter_by(id=id).first()

    form = FormAdmin()
    form.username.data = admin.username
    form.email.data = admin.email

    username = admin.username
    email = admin.email

    session['admin_logado'] = username

    return render_template("admin/edit_admin_profile.html", form=form, id=id, username=username, email=email)


@app.route('/admin/delete_admin/<int:id>')
def delete_admin(id):
    total_admins = Admins().query.count()
    if total_admins > 1:

        Admins().query.filter_by(id=id).delete()

        if session['admin_id'] == id:
            flash('Excluído com sucesso!', 'success')
            session['admin_logado'] = None
            session['admin_id'] = None
            db.session.commit()
            return redirect('/')
        else:
            flash('Excluído com sucesso!', 'success')
            db.session.commit()

            return redirect('/admin/get_all_admins')
    else:
        flash('Não é possível excluir. É necessário que tenha ao menos 1 administrador.', 'danger')
        return redirect('/admin/get_all_admins')


@app.route('/admin/delete_user/<int:id>')
def delete_user(id):
    flash('Usuário excluído com sucesso!', 'success')
    Usuarios().query.filter_by(id=id).delete()
    db.session.commit()

    previous_page = request.args['previous_page']
    return redirect(url_for(previous_page))


@app.route('/add_user', methods=['POST'])
def add_user():
    form = FormUsuario(request.form)

    first_name = form.first_name.data
    last_name = form.last_name.data
    username = form.username.data
    email = form.email.data
    password = form.password.data

    usuario = Usuarios().query.filter_by(email=email).first()
    if usuario:
        flash('Endereço de email já associado a uma conta.', 'warning')
        return redirect(url_for('user_login'))
    else:
        hash_password = generate_password_hash(password).decode('utf-8')
        user = Usuarios(first_name=first_name, last_name=last_name, username=username, email=email,
                        password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash("Usuário cadastrado.", 'success')
        page_redirect = request.form['page_redirect']
        return redirect(url_for(page_redirect))


@app.route('/add_admin', methods=['POST'])
def add_admin():
    form = FormAdmin(request.form)

    username = form.username.data
    email = form.email.data
    password = form.password.data

    admin = Admins().query.filter_by(email=email).first()
    if admin:
        flash('Endereço de email já associado a uma conta.', 'warning')
        return redirect(url_for('admin_create_account'))
    else:
        hash_password = generate_password_hash(password).decode('utf-8')
        admin = Admins(username=username, email=email, password=hash_password)
        db.session.add(admin)
        db.session.commit()
        flash("Administrador cadastrado.", 'success')
        return redirect('/admin/get_all_admins')


@app.route('/update_admin', methods=["POST"])
def update_admin():
    if 'admin_logado' not in session or session['admin_logado'] is None:
        flash('Administrador não logado.', 'warning')
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
        flash('Administrador não logado.', 'warning')
        return redirect(url_for('admin_login'))
    else:
        flash('Informações de usuário atualizadas com sucesso!', 'success')
        form = FormUsuario(request.form)

        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        status = form.status.data

        id = request.form['id']
        user = Usuarios().query.filter_by(id=id).first()
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        if status == "True":
            user.status = 1
        else:
            user.status = 0

        db.session.add(user)
        db.session.commit()

        page_redirect = request.form['page_redirect']
        return redirect(url_for(page_redirect))


@app.route('/admin/profile')
def admin_profile():
    admin_id = session['admin_id']
    admin = Admins().query.filter_by(id=admin_id).first()
    username = admin.username
    email = admin.email
    return render_template('/admin/edit_admin_profile.html', email=email, username=username)
