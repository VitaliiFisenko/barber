import time

from flask import Flask, request, render_template, redirect, session
from flask_bootstrap import Bootstrap
import db
from forms import LoginForm, RegisterForm, OrderForm, StatusForm

app = Flask(__name__)

Bootstrap(app)


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        if session.get('current_user')['role_id'] == 1:
            return redirect('/manage_orders/1')
        return redirect('/')
    elif request.method == 'POST' and not form.validate():
        return redirect('/register')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        user = db.db_get(f"""select * from Buser where login='{form.login.data}';""")
        if user:
            return render_template('register.html', form=form), 400
        query = f"""
        insert into Buser (login, password, name, last_name, surname, phone, email, Role_id) values ('{form.login.data}',
        '{form.password.data}','{form.name.data}','{form.last_name.data}','{form.surname.data}',
        '{form.phone.data}', '{form.email.data}', 2);
        """
        db.db_save(query)
        user = db.db_get(f"""select * from Buser where login='{form.login.data}';""")
        session['current_user'] = user
        db.db_save(f"""insert into cart (Buser_id, Status_id) values ({user['id']}, 6);""")
        session['current_user_cart'] = db.db_get(f"""select * from cart where Buser_id={user['id']}""")
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def services():
    if not session.get('current_user'):
        return redirect('/login')
    query = """
    SELECT * FROM Service;
    """
    data = db.db_get(query, cur_type='all')
    return render_template('services.html', data=data)


@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    cart_id = session.get('current_user_cart')['id']
    query = f"""
    INSERT INTO Service_cart_rel (Service_id, Cart_id) VALUES ({item_id}, {cart_id})
    """
    db.db_save(query)
    return redirect('/')


@app.route('/view_cart', methods=['POST', 'GET'])
def view_cart():
    if not session.get('current_user'):
        return redirect('/login')
    data = db.db_get(
        f"""select * from service where id in (select service_id  from Service_cart_rel where cart_id={session.get('current_user_cart')['id']});""",
        cur_type='all')
    price = 0
    if data:
        for item in data:
            price += item['price']
    context = {'data': data, 'price': price}
    return render_template('cart.html', data=context)


@app.route('/create_order', methods=['POST', 'GET', 'PATCH'])
def create_order():
    if not session.get('current_user'):
        return redirect('/login')
    form = OrderForm(request.form)
    user_id = session.get('current_user')['id']
    cart_id = session.get('current_user_cart')['id']
    order = db.db_get(f'select * from border where buser_id={user_id} and status_id=1;')
    if request.method == 'POST':
        query = f"""UPDATE Buser set name='{form.name.data}', last_name='{form.last_name.data}', surname='{form.surname.data}', phone='{form.phone.data}', email='{form.email.data}' where id={user_id};
                    update cart set status_id=7 where id={cart_id};
                    insert into cart (Buser_id, Status_id) values ({user_id}, 6);
                    insert into  border (Buser_id,Status_id,payment_type) values ({user_id}, 1, '{form.payment_type.data}');
                    insert into Order_cart_rel (Cart_id, Border_id) values ({cart_id},  (SELECT MAX(id) FROM border));
"""
        db.db_save(query)
        session['current_user_cart'] = db.db_get(f'select * from cart where buser_id={user_id} and status_id=6;')
    elif request.method == 'PATCH':
        query = f"""update border set status_id=5 where buser_id={user_id} and status_id=1;"""
        db.db_save(query)
        return redirect('/')
    data = db.db_get(
        f"""select * from service where id in (select service_id  from Service_cart_rel where cart_id={session.get('current_user_cart')['id']});""",
        cur_type='all')
    price = 0
    if data:
        for item in data:
            price += item['price']
    context = {'data': data, 'price': price, 'order_exist': True if order else False}
    return render_template('order.html', data=context, form=form)


@app.route('/manage_orders/<int:status_id>', methods=['GET', 'POST'])
def manage_orders(status_id):
    if not session.get('current_user'):
        return redirect('/login')
    elif not session.get('current_user')['role_id'] == 1:
        return render_template('401.html')
    form = StatusForm(request.form)
    if request.method == 'POST':
        db.db_save(f'update border set Status_id={form.status.data} where id={request.args.get("ord_id")}')

    db_data = db.db_get(f'select * from border where status_id={status_id};', cur_type='all')
    return render_template('orders.html', data=db_data, form=form, status_id=status_id)


if __name__ == '__main__':
    db.create_db()
    time.sleep(5)
    db.fill_db()
    app.secret_key = 'super secret key'
    app.run(debug=True, host='0.0.0.0')
