from myapp import db
from flask_login import UserMixin


class Clients(db.Model):
    __tablename__ = 'Clients'
    ClientID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    ContactInfo = db.Column(db.String(255), nullable=False)




class Drivers(db.Model):
    ___tablename__ = 'Drivers'
    DriverID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    ContactInfo = db.Column(db.String(255), nullable=False)



class Transport(db.Model):
    __tablename__ = 'Transport'
    TransportID = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String(255), nullable=False)
    Capacity = db.Column(db.Integer, nullable=False)
    LicensePlate = db.Column(db.String(255), nullable=False)


class Orders(db.Model):
    __tablename__ = 'Orders'
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ClientID = db.Column(db.Integer, db.ForeignKey('Clients.ClientID'), nullable=False)
    DriverID = db.Column(db.Integer, db.ForeignKey('Drivers.DriverID'))
    Status = db.Column(db.String(255), nullable=False)
    OrderDate = db.Column(db.DateTime, nullable=False)

    Client = db.relationship('Clients', backref='Orders', lazy=True)



class Cargo(db.Model):
    __tablename__ = 'Cargo'
    CargoID = db.Column(db.Integer, primary_key = True)
    OrderID = db.Column(db.Integer, db.ForeignKey('Orders.OrderID'), nullable=False)
    Description = db.Column(db.Text, nullable=False)
    Weight = db.Column(db.Integer, nullable=False)
    
    Order = db.relationship('Orders', backref='Cargo', lazy=True)


class Routes(db.Model):
    __tablename__ = 'Routes'
    RouteID = db.Column(db.Integer, primary_key=True)
    OrderID = db.Column(db.Integer, db.ForeignKey('Orders.OrderID'), nullable=False)
    TransportID = db.Column(db.Integer, db.ForeignKey('Transport.TransportID'), nullable=False)
    DriverID = db.Column(db.Integer, nullable=False)
    StartLocation = db.Column(db.String(255), nullable=False)
    EndLocation = db.Column(db.String(255), nullable=False)
    Distance = db.Column(db.Integer, nullable=False)
    EstimatedTravelTime = db.Column(db.Integer, nullable=False)

    Order = db.relationship('Orders', backref='Routes', lazy=True)


class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100))
    password = db.Column(db.String(50))
    registration_date = db.Column(db.Date)


class Admin_users(db.Model, UserMixin):
    __tablename__ = 'Admin_users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100))
    password = db.Column(db.String(50))
    registration_date = db.Column(db.Date)


class Cities(db.Model):
    __tablename__ = 'Cities'
    city_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.String(20), nullable=False)