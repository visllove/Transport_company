from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify
from models import Drivers, Transport, Orders, Routes, Clients, Cargo, Users, Admin_users, Cities, db
from myapp import create_app
# from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    print(username)
    password = request.form.get('password')
    print(password)

    user = Users.query.filter_by(username=username, password=password).first()
    admin = Admin_users.query.filter_by(username=username, password=password).first()
    
    print(user)
    print(admin)
    print(request.form.get('username'))

    
    if user:
        current_user = Users.query.filter_by(username=username, password=password).first().name
        # Redirect to the home page if login is successful
        return redirect(url_for('home'))
    elif admin:
        current_user = Admin_users.query.filter_by(username=username, password=password).first().name
        return render_template('admin_home.html', current_user=current_user)
        return redirect(url_for('admin_home'))
    else:
        # Redirect back to the login page if login fails
        # return redirect(url_for('login'))
        return render_template('login.html')
    
@app.route('/home')
def home():
    clients = Clients.query.all()
    drivers = Drivers.query.all()
    transports = Transport.query.all()
    orders = Orders.query.all()
    cargo = Cargo.query.all()
    routes = Routes.query.all()

    return render_template('home.html')


@app.route('/admin_home')
def admin_home():
    
    return render_template('admin_home.html')



@app.route('/show_table/<string:table>', methods=['GET', 'POST'])
def show_table(table):
    print(table)

    table_models = {
        'clients': Clients,
        'drivers': Drivers,
        'transport': Transport,
        'orders': Orders,
        'cargo': Cargo,
        'routes': Routes
    }
    
    selected_table = table_models.get(table)
    # Получаем первичный ключ (идентификатор) для модели
    primary_key = selected_table.__table__.primary_key.columns.keys()[0]

    if selected_table:
        data = selected_table.query.all()
        print(f'Primary key for table {selected_table} is {primary_key}')
        return render_template('show_table.html', table=table, data=data, primary_key=primary_key)
    
    else:
        # Обработка случая, если выбранной таблицы нет в словаре
        return render_template('error.html', message='Table not found')

# Обработчик для кнопки удаления записи
@app.route('/delete/<string:table>/<int:item_id>', methods=['POST'])
def delete_item(item_id, table):
    
    selected_table = request.view_args['table']
    # Словарь для сопоставления имен таблиц с моделями
    table_models = {
        'clients': Clients,
        'drivers': Drivers,
        'transport': Transport,
        'orders': Orders,
        'cargo': Cargo,
        'routes': Routes
    }
    
    selected_model = table_models.get(table)
    
    item_to_delete = selected_model.query.get_or_404(item_id)
    print(item_id)
    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        flash('Item deleted successfully', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        flash('Error during deletion', 'danger')
        # Обработайте ошибку удаления (например, запись не найдена)
        return render_template('error.html', message=str(e))
    

# Обработчик пересылки на кнопку добавления строки тестовый
@app.route('/add_row_test', methods=['POST'])
def add_row_test():
    return render_template("forms.html")

# Обработчик для кнопки добавления строки тестовый
@app.route('/add_row_1', methods=['POST'])
def add_row_1():
    transport_id = request.form['user_name']
    type = request.form['user_id']
    capacity = request.form['name']
    license_plate = request.form['password']
    new_row = Transport(Type=type, Capacity=capacity, LicensePlate=license_plate)
    db.session.add(new_row)
    db.session.commit()
    
    return redirect(url_for('home'))

    

# Обработчик для кнопки добавления строки
@app.route('/add_row', methods=['POST'])
def add_row(table):
    # Проверяем, что все поля ввода заполнены
    if not all(field in request.form for field in ['column1', 'column2']):
        return 'All fields must be filled', 400
    
    # Создаем новую строку и добавляем ее в базу данных
    new_row = table(column1=request.form['column1'], column2=request.form['column2'])
    new_row = table()
    db.session.add(new_row)
    db.session.commit()
    
#     # Перенаправляем пользователя на страницу с таблицей
#     return redirect(url_for('show_table', table=table))

# Обработчик для кнопки отображения карты
@app.route('/show_map/<string:table>/<int:item_id>', methods=['GET', 'POST'])
def show_map(table, item_id):
    city1 = db.session.query(Cities.latitude, Cities.longitude).select_from(Cities).join(Routes, onclause=(Cities.name == Routes.StartLocation)).filter(Routes.RouteID == item_id).first()
    city2 = db.session.query(Cities.latitude, Cities.longitude).select_from(Cities).join(Routes, onclause=(Cities.name == Routes.EndLocation)).filter(Routes.RouteID == item_id).first()
    print(city1)
    print(city2)
    return render_template('map_leaflet.html', city1=city1, city2=city2)


# Обработчик для кнопки редактирования строки
@app.route('/edit_item/<string:table>/<int:item_id>', methods=['GET', 'POST'])
def edit_item(table, item_id):
    return 0

@app.route('/map', methods=['GET', 'POST'])
def map():
    city1 = db.session.query(Cities.latitude, Cities.longitude).filter(Cities.name == 'Москва').first()
    city2 = db.session.query(Cities.latitude, Cities.longitude).filter(Cities.name == 'Санкт-Петербург').first()
    print(city1)
    print(city2)
    return render_template('map_leaflet.html', city1=city1, city2=city2)


# @app.route('/filtered_table', methods=['GET', 'POST'])
# def filtered_table(table):
#     # Получите данные из формы поиска
#     search_term = request.form.get('search', '')

#     # Определите модель для выбранной таблицы
#     table_model = table_models.get(table)

#     # Если модель и данные существуют, выполните фильтрацию
#     if table_model:
#         data = table_model.query.filter(or_(*[getattr(table_model, column).ilike(f"%{search_term}%") for column in table_model.__table__.columns]))
#         return render_template('filtered_table.html', table=table, data=data)

#     # Обработка случая, если выбранной таблицы нет в словаре
#     return render_template('error.html', message='Table not found')
