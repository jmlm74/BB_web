from app.auth import bp
from flask import g, request
from flask_login import current_user, login_user, logout_user
from flask import flash, redirect, url_for, render_template
from app.auth.forms import (LoginForm,
                            RegistrationForm,
                            ResetPasswordForm,
                            ResetPasswordRequestForm,
                            CreateForm,
                            UpdateForm)
from app.auth.models import User
from app import is_admin
from app import db
from app.utils.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        if login_user(user, remember=form.remember_me.data):
            g.user = user.username
            g.is_admin = user.is_admin
            return redirect(url_for('index'))
        else:
            flash("User is not active")
    return render_template('auth/login.html', title='Login', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/auth_generic.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/auth_generic.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/auth_generic.html', form=form, title="Reset Password")


@bp.route('/create', methods=['GET', 'POST'])
@is_admin
def create_user():
    form = CreateForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    is_admin=form.is_admin.data,
                    is_active=form.is_active.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"user {form.username.data} created")
        return redirect(url_for('auth.liste_users'))
    return render_template('auth/auth_generic.html', form=form, title="Create")


@bp.route('/update/<user_id>', methods=['GET', 'POST'])
@is_admin
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        user = None
        flash(f'User {user_id} not found')
        form = UpdateForm(obj=user)
        form.submit.render_kw = {'disabled': 'disabled'}
    else:
        form = UpdateForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        db.session.commit()
        flash(f"user {form.username.data} updated")
        return redirect(url_for('auth.liste_users'))
    return render_template('auth/auth_generic.html', title="Update user", form=form)

@bp.route('/delete/<user_id>', methods=['GET', 'POST'])
@is_admin
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        user = None
        flash(f'User {user_id} not found')
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        flash(f"user {user.username} deleted !")
        return redirect(url_for('auth.liste_users'))
    return render_template('auth/delete_user.html', title="Delete user", user=user)


@bp.route('/list')
def liste_users():
    users = User.query.order_by(User.username).all()
    print(f"users - {users}")
    return render_template('auth/list_users.html', title='liste utilisateurs', users=users)


@bp.route('auth/ajax_list')
def ajax_liste_users():
    query = User.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            User.username.like(f'%{search}%'),
            User.email.like(f'%{search}%')
        ))

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['username', 'email']:
            col_name = 'username'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(User, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    total_filtered = query.count()

    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    return {
        'data': [user.to_dict() for user in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': User.query.count(),
        'draw': request.args.get('draw', type=int),
    }
