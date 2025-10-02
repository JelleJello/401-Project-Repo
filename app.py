from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime

app = Flask(__name__)

bootstrap = Bootstrap5(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/flask_users_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default="user", nullable=False)

# class user profile (Natalie)
class User_Profile(db.Model):
    __tablename__ = 'user_profile'
    user_profile_id = db.Column(db.Integer, primary_key=True)
    fullName = db.Column(db.String(255))
    hashedPassword = db.Column(db.String(255))
    stocks = db.Column(db.String(255))
    email = db.Column(db.String(255))
    orderId = db.Column(db.Integer)
    portfolio = db.Column(db.String(255))
    availableFunds = db.Column(db.Integer)
    createdAt = db.Column(db.Integer)
    updatedAt = db.Column(db.Integer)
    # avatar?

# Admin Model (Hannah)
class Administrator(db.Model):
    __tablename__ = 'administrator'
    AdministratorId = db.Column(db.Integer, primary_key=True)
    Fullname = db.Column(db.String(255))
    Email = db.Column(db.String(255))
    password = db.Column(db.Text(255))


# Company Model (Hannah)
class Company(db.Model):
    __tablename__ = 'company'
    companyId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255))
    Description = db.Column(db.String(255))
    stockTotalQantity = db.Column(db.Integer)
    ticker = db.Column(db.Integer)
    currentMarketPrice = db.Column(db.Integer)
    createdAt = db.Column(db.Integer)
    updatedAt = db.Column(db.Integer)

# Financial Transaction Model (Hannah)
class Financial_transaction(db.Model):
    __tablename__ = 'financial_transaction'
    FinancialTransactionId = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    type_BUYSELL = db.Column(db.String(255))
    createdAt = db.Column(db.Integer)
    customerAccountNumber = db.Column(db.Integer, db.ForeignKey('user_profile.user_profile_id'), nullable=False)
    companyId = db.Column(db.Integer, db.ForeignKey('company.companyId'), nullable=False)
    # reltionship to Financial_transaction(db.Model)
    # financial_transactions = db.relationship('Financial_Transaction', backref='author', lazy='dynamic')

# Order History Model (Jenelle)
class OrderHistory(db.Model):
    __tablename__ = 'orderhistory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderType = db.Column(db.String(4), nullable=False)
    orderQuantity = db.Column(db.Integer, nullable=False)
    totalOrderAmount = db.Column(db.DECIMAL(10, 2), nullable=False)
    orderTicker = db.Column(db.String(10), unique=True, nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stockinventory_id = db.Column(db.Integer, db.ForeignKey('stockinventory.id'), nullable=False)
    administrator_id = db.Column(db.ForeignKey('administrator.AdministratorId'), nullable=False)

# Porfolio Model (Jenelle)
class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    walletAmount = db.Column(db.Integer, nullable=False, default=0)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    portfolio_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_order_history = db.Column(db.ForeignKey('orderhistory.id'), nullable=False)

# StockInventory Model (Jenelle)
class StockInventory(db.Model):
    __tablename__ = 'stockinventory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stockName = db.Column(db.String(255), unique=True, nullable=False)
    stockTicker = db.Column(db.String(10), unique=True, nullable=False)
    stockQuantity = db.Column(db.Integer, nullable=False)
    initialMarketPrice = db.Column(db.DECIMAL(10, 2), nullable=False)
    currentMarketPrice = db.Column(db.DECIMAL(10, 2), nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.companyId'), nullable=False)
    administrator_id = db.Column(db.ForeignKey('administrator.AdministratorId'), nullable=False)

# class WorkingDay (Natalie)
class Working_Day(db.Model):
    __tablename__ = 'working_day'
    workingDayId = db.Column(db.Integer, primary_key=True)
    dayOfWeek = db.Column(db.String(255))
    startTime = db.Column(db.Integer)
    endTime = db.Column(db.Integer)
    createdAt = db.Column(db.Integer)
    updatedAt = db.Column(db.Integer)
    AdministratorId = db.Column(db.Integer, db.ForeignKey('administrator.AdministratorId'))

# class Exception (Natalie)
class Exception(db.Model):
    __tablename__ = 'exception'
    exceptionId = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(255))
    holidayDate = db.Column(db.Integer)
    createdAt = db.Column(db.Integer)
    updatedAt = db.Column(db.Integer)
    AdministratorId = db.Column(db.Integer, db.ForeignKey('administrator.AdministratorId'))

# Create tables
with app.app_context():
    db.create_all()

# User or Admin authentication check
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

bcrypt = Bcrypt(app)

# Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        hashed_password = bcrypt.generate_password_hash(request.form.get("password")).decode('utf-8')
        user = User(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password=hashed_password,  # Store hashed password instead of plaintext
            role="user"
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            return redirect(url_for("portfolio"))
    return render_template("login.html")

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/admin-register', methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        # Verify the admin registration key
        admin_key = request.form.get("admin_key")
        if admin_key != "YOUR_SECRET_ADMIN_KEY":  # Change this to a secure key
            return redirect(url_for("login"))
       
        hashed_password = bcrypt.generate_password_hash(request.form.get("password")).decode('utf-8')
        admin = User(
            username=request.form.get("username"),
            password=hashed_password,
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        return redirect(url_for("login"))
   
    return render_template("admin_sign_up.html")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

# Admin only role
@app.route('/admin-dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()  # Get all users for admin to manage
    return render_template("admin_dashboard.html", users=users)

@app.route("/portfolio")
@login_required
def portfolio():
    return render_template("portfolio.html")

@app.route("/market")
@login_required
def market():
    return render_template("market.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")



if __name__ == "__main__":
    app.run(debug=True)
