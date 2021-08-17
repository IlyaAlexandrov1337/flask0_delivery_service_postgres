import datetime
from csv import DictReader

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, request, render_template
from forms import RegisterForm, AuthenticationForm, OrderForm, OutCartForm, InCartForm
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql.expression import func
from init_and_models import db, app, User, Meal, Category, Order


csrf = CSRFProtect(app)
admin = Admin(app)  # т.к. в курсе ничего не сказано про то, как защитить админку, я сделал её для галочки, не более

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Order, db.session))
admin.add_view(ModelView(Meal, db.session))


def transform_order_meals(order):
    try:
        return len(order.meals)
    except AttributeError:
        return 0


def transform_sum(order):
    try:
        return order.sum
    except AttributeError:
        return 0


@app.errorhandler(500)
def render_server_error(error):
    return f'<h1>Что-то не так, но мы все починим</h1><p>{error}</p>'


@app.errorhandler(404)
def render_server_error(error):
    return f'<h1>Ничего не нашлось! Вот неудача, url некорректный:(</h1><p>{error}</p>'


@app.route('/', methods=["GET", "POST"])
def main_render():
    error_msg = ''
    form = InCartForm()
    l = []
    for cat in Category.query.all():
        l.append(Meal.query.filter(Meal.category_id == cat.id).order_by(func.random()).limit(3))
    user_id = session.get('user_id', 0)
    order = Order.query.filter(db.and_(Order.user_id == user_id, Order.status == 'Формируется')).first()
    if form.is_submitted() and request.method == "POST":
        meal_id = form.meal.data
        meal = Meal.query.get(meal_id)
        now = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        if not order:
            mail = User.query.get(user_id).mail
            new_order = Order(date=now, sum=meal.price, status='Формируется', mail=mail, name='', phone='', address='',
                              user_id=user_id)
            db.session.add(new_order)
            new_order.meals.append(meal)
            db.session.commit()
            return redirect('/cart')
        else:
            if meal in order.meals:
                error_msg = 'Заказать можно только одну порцию блюда'
            else:
                order.sum += meal.price
                order.date = now
                order.meals.append(meal)
                db.session.commit()
                return redirect('/cart')
    return render_template("main.html", categories=l, flag=user_id, count=transform_order_meals(order), form=form,
                           sum=transform_sum(order), error_msg=error_msg)


@app.route("/register", methods=["GET", "POST"])
def registration_render():
    error_msg = ''
    if session.get("user_id"):
        return redirect('/account')
    form = RegisterForm()
    if form.validate_on_submit() and request.method == "POST":
        mail = form.mail.data
        password = form.password.data
        user = User.query.filter(User.mail == mail).first()
        if not user:
            new_user = User(mail=mail, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return render_template('register_successful.html')
        else:
            error_msg = 'Попробуйте ещё раз с другой почтой'
        return render_template("register.html", form=form, error_msg=error_msg)
    return render_template("register.html", form=form, error_msg='')


@app.route("/auth", methods=["GET", "POST"])
def auth_render():
    error_msg = ''
    user_id = session.get('user_id', False)
    if user_id:
        return redirect('/account')
    form = AuthenticationForm()
    if form.validate_on_submit() and request.method == "POST":
        mail = form.mail.data
        password = form.password.data
        user = User.query.filter(User.mail == mail).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_mail"] = user.mail
            return redirect('/account')
        if not user:
            error_msg += 'Пользователя с такой почтой не существует'
            return render_template("auth.html", form=form, error_msg=error_msg)
        if not check_password_hash(user.password, password):
            error_msg += 'Неверный пароль'
            return render_template("auth.html", form=form, error_msg=error_msg)
    return render_template("auth.html", form=form, error_msg=error_msg)


@app.route('/logout')
def logout():
    if session.get("user_id"):
        session.clear()
    return redirect("/")


@app.route("/account")
def account_render():
    mail = session.get('user_mail')
    if not mail:
        redirect('/auth')
    orders = Order.query.filter(Order.mail == mail).order_by(Order.date.desc()).all()
    order = Order.query.filter(db.and_(Order.user_id == session['user_id'], Order.status == 'Формируется')).first()
    return render_template("account.html", orders=orders, count=transform_order_meals(order), flag=mail,
                           sum=transform_sum(order))


@app.route("/cart", methods=["GET", "POST"])
def cart_render():
    if not session.get("user_id"):
        return redirect('/auth')
    form = OrderForm()
    del_form = OutCartForm()
    user_id = session.get('user_id')
    order = Order.query.filter(db.and_(Order.user_id == user_id, Order.status == 'Формируется')).first()
    if not order:
        return redirect('/')
    if request.method == "POST":
        if del_form.delete.data and del_form.validate():
            form.errors.clear()
            meal_id = del_form.meal.data
            meal = Meal.query.get(meal_id)
            now = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            order.sum -= meal.price
            order.date = now
            order.meals.remove(meal)
            db.session.commit()
        elif form.validate_on_submit():
            name = form.name.data
            address = form.address.data
            phone = form.phone.data
            order.name = name
            order.address = address
            order.phone = phone
            order.status = "В обработке"
            db.session.commit()
            return redirect('/ordered')
    return render_template("cart.html", order=order, count=transform_order_meals(order), sum=transform_sum(order),
                           flag=user_id, form=form, del_form=del_form)


@app.route("/ordered")
def order_render():
    return render_template("ordered.html")


if __name__ == "__main__":
    
    with open('raw_database/categories.csv', encoding='UTF8') as file:
        reader = DictReader(file)
        for row in reader:
            category = Category(id=row['id'], title=row['title'])
            if Category.query.get(row['id']):
                break
            db.session.add(category)
        db.session.commit()

    with open('raw_database/meals.csv', encoding='UTF8') as file:
        reader = DictReader(file)
        for row in reader:
            meal = Meal(id=row['id'], title=row['title'], price=row['price'], description=row['description'],
                        picture=f"static/{row['picture']}", category=Category.query.get(int(row['category_id'])))
            if Meal.query.get(row['id']):
                break
            db.session.add(meal)
        db.session.commit()
        
    app.run()
