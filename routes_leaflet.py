from flask import render_template, request, redirect, url_for, flash, session, abort, after_this_request, Blueprint, jsonify
from models import Drivers, Transport, Orders, Routes, Clients, Cargo, Users, Cities, db
from myapp import create_app, login_manager
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from functools import wraps, update_wrapper
import requests

app = create_app()
bcrypt = Bcrypt(app)

table_models = {
            'clients': Clients,
            'drivers': Drivers,
            'transport': Transport,
            'orders': Orders,
            'cargo': Cargo,
            'routes': Routes
        }


def no_cache(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        @after_this_request
        def no_cache_response(response):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response

        return view_func(*args, **kwargs)

    return update_wrapper(wrapped_view, view_func)


@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(user_id)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Поиск пользователей в базе данных
        user = Users.query.filter_by(username=username).first()

        # Аутентификация пользователей
        if user and user.password == password: # and bcrypt.check_password_hash(user.password, password):
            # Передаем ифнормацию о пользователе в сессию для функций home и admin_home
            session['cur_user'] = user.name
            login_user(user)
            if user.role_id == 1:
                return redirect(url_for('home'))
            elif user.role_id == 2:
                return redirect(url_for('admin_home'))
            
        else:
            flash('Invalid email or password')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
@no_cache
def home():
    cur_user = session.get('cur_user')
    return render_template('home.html', cur_user=cur_user)


@app.route('/admin_home')
@login_required
@no_cache
def admin_home():
    if current_user.role_id != 2:
        abort(403)
    cur_user = session.get('cur_user')
    print(cur_user)
    return render_template('admin_home.html', cur_user=cur_user)


# Обработчик для отображения страниц с таблицами
@app.route('/show_table/<string:table>', methods=['GET', 'POST'])
@login_required
def show_table(table):
    print(table)
    
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
@login_required
def delete_item(item_id, table):
    try:
        # Словарь для сопоставления имен таблиц с моделями
        

        selected_model = table_models.get(table)
        
        if selected_model is None:
            return jsonify({'error': 'Invalid table name'}), 400
        
        item_to_delete = selected_model.query.get_or_404(item_id)
        db.session.delete(item_to_delete)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
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


# Погода - передача иконки в шаблон leaflet_map
# def get_weather_data(lat, lon):
#     api_key = "ea7ca8e35058dc85e79701f2e137b924"
#     url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
#     response = requests.get(url)
#     data = response.json()
#     weather_icon = data['list'][0]['weather'][0]['icon']
#     return {'weather_icon': weather_icon}

# Погода - работа с API
# @app.route('/get_weather/<lat>/<lon>')
# def get_weather(lat, lon):
#     api_key = "ea7ca8e35058dc85e79701f2e137b924"
#     url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
#     response = requests.get(url)
#     data = response.json()
#     return jsonify(data)


# Обработчик для кнопки отображения карты
@app.route('/show_map/<string:table>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def show_map(table, item_id):
    city1 = db.session.query(Cities.latitude, Cities.longitude).select_from(Cities).join(Routes, onclause=(Cities.name == Routes.StartLocation)).filter(Routes.RouteID == item_id).first()
    city2 = db.session.query(Cities.latitude, Cities.longitude).select_from(Cities).join(Routes, onclause=(Cities.name == Routes.EndLocation)).filter(Routes.RouteID == item_id).first()
    print(city1)
    print(city2)

    # weather_data = get_weather_data(city1[0], city1[1])

    return render_template('map_leaflet.html', city1=city1, city2=city2)#, weather_data=weather_data)


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


@app.route('/update_item/<string:table>/<int:item_id>', methods=['POST'])
@login_required
def update_item(table, item_id):
    # Retrieve data from the AJAX request
    
    print('Сохранено')

    item_id = item_id
    print(item_id)
    table = table.capitalize()
    
    print(item_id)
    # Update item based on table
    if table == 'Clients':
        client = Clients.query.get(item_id)
        if client:
            client.Name = request.form.get('Name')
            client.ContactInfo = request.form.get('ContactInfo')
            db.session.commit()
            return jsonify({'message': 'Client updated successfully'})
    elif table == 'Drivers':
        driver = Drivers.query.get(item_id)
        if driver:
            driver.Name = request.form.get('Name')
            driver.ContactInfo = request.form.get('ContactInfo')
            db.session.commit()
            return jsonify({'message': 'Driver updated successfully'})
    elif table == 'Transport':
        transport = Transport.query.get(item_id)
        if transport:
            transport.Type = request.form.get('Type')
            transport.Capacity = request.form.get('Capacity')
            transport.LicensePlate = request.form.get('LicensePlate')
            db.session.commit()
            return jsonify({'message': 'Transport updated successfully'})
    elif table == 'Orders':
        order = Orders.query.get(item_id)
        if order:
            order.ClientID = request.form.get('ClientID')
            order.DriverID = request.form.get('DriverID')
            order.Status = request.form.get('Status')
            db.session.commit()
            return jsonify({'message': 'Order updated successfully'})
    elif table == 'Cargo':
        cargo = Cargo.query.get(item_id)
        if cargo:
            cargo.OrderID = request.form.get('OrderID')
            cargo.Description = request.form.get('Description')
            cargo.Weight = request.form.get('Weight')
            db.session.commit()
            return jsonify({'message': 'Cargo updated successfully'})
    elif table == 'Routes':
        route = Routes.query.get(item_id)
        if route:
            route.OrderID = request.form.get('OrderID')
            route.TransportID = request.form.get('TransportID')
            route.DriverID = request.form.get('DriverID')
            route.StartLocation = request.form.get('StartLocation')
            route.EndLocation = request.form.get('EndLocation')
            route.Distance = request.form.get('Distance')
            route.EstimatedTravelTime = request.form.get('EstimatedTravelTime')
            db.session.commit()
            return jsonify({'message': 'Route updated successfully'})
    
    # If item is not found or table is invalid, return an error message
    return jsonify({'error': 'Item not found or invalid table'}), 404


@app.route('/submit_form/<string:table>', methods=['POST'])
@login_required
def submit_form(table):
    print(request.get_data())
    table = table.capitalize()
    print(request.form.get('ContactInfo'))
    print(table, 'submit')

    if table == 'Clients':
        name = request.form.get('Name')
        contact_info = request.form.get('ContactInfo')
        # Insert data into the Clients table

        print(name, contact_info)

        new_client = Clients(Name=name, ContactInfo=contact_info)
        db.session.add(new_client)
        db.session.commit()
        flash('New client added successfully!', 'success')
    elif table == 'Drivers':
        name = request.form.get('Name')
        contact_info = request.form.get('ContactInfo')
        # Insert data into the Drivers table
        new_driver = Drivers(Name=name, ContactInfo=contact_info)
        db.session.add(new_driver)
        db.session.commit()
        flash('New driver added successfully!', 'success')
    elif table == 'Transport':
        type = request.form.get('Type')
        capacity = request.form.get('Capacity')
        license_plate = request.form.get('LicensePlate')
        # Insert data into the Transport table
        new_transport = Transport(Type=type, Capacity=capacity, LicensePlate=license_plate)
        db.session.add(new_transport)
        db.session.commit()
        flash('New transport added successfully!', 'success')
    elif table == 'Orders':
        client_id = request.form.get('ClientID')
        driver_id = request.form.get('DriverID')
        status = request.form.get('Status')
        order_date = request.form.get('OrderDate')
        # Insert data into the Orders table
        new_order = Orders(ClientID=client_id, DriverID=driver_id, Status=status, OrderDate=order_date)
        db.session.add(new_order)
        db.session.commit()
        flash('New order added successfully!', 'success')
    elif table == 'Cargo':
        order_id = request.form.get('OrderID')
        description = request.form.get('Description')
        weight = request.form.get('Weight')
        if request.form.get('CargoID'):
            cargo_id = request.form.get('CargoID')
        # Insert data into the Cargo table
        new_cargo = Cargo(OrderID=order_id, Description=description, Weight=weight)
        db.session.add(new_cargo)
        db.session.commit()
        flash('New cargo added successfully!', 'success')
    elif table == 'Routes':
        order_id = request.form.get('OrderID')
        transport_id = request.form.get('TransportID')
        start_location = request.form.get('StartLocation')
        end_location = request.form.get('EndLocation')
        distance = request.form.get('Distance')
        estimated_travel_time = request.form.get('EstimatedTravelTime')
        # Insert data into the Routes table
        new_route = Routes(OrderID=order_id, TransportID=transport_id, StartLocation=start_location, EndLocation=end_location, Distance=distance, EstimatedTravelTime=estimated_travel_time)
        db.session.add(new_route)
        db.session.commit()
        flash('New route added successfully!', 'success')
    else:
        flash('Invalid table specified!', 'error')
    # Return a response indicating success or failure
    return jsonify({'message': 'Data submitted successfully'})
