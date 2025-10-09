from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime, date
import holidays

from sqlalchemy import func
# import pandas as pd

app = Flask(__name__)

bootstrap = Bootstrap5(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/stocks_application'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default="user", nullable=False)

    def get_id(self):
        return f"user-{self.id}"

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
class Administrator(UserMixin, db.Model):
    __tablename__ = 'administrator'
    AdministratorId = db.Column(db.Integer, primary_key=True)
    Fullname = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text(255), nullable=False)

    def get_id(self):
        return f"admin-{self.AdministratorId}"

    @property
    def role(self):
        return "admin"


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
    id = db.Column(db.Integer, primary_key=True)
    orderType = db.Column(db.String(10), nullable=False)
    orderQuantity = db.Column(db.Integer, nullable=False)
    totalOrderAmount = db.Column(db.Float, nullable=False)
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    createdAt = db.Column(db.DateTime(timezone=True),server_default=func.now(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

# Porfolio Model (Jenelle)
class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    walletAmount = db.Column(db.Integer, nullable=False, default=10000)
    createdAt = db.Column(db.DateTime(timezone=True),server_default=func.now(), nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    portfolio_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_order_history = db.Column(db.ForeignKey('orderhistory.id'), nullable=False)

# StockInventory Model (Jenelle)
class StockInventory(db.Model):
    __tablename__ = 'stockinventory'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stockName = db.Column(db.String(255), unique=True, nullable=False)
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    currentMarketPrice = db.Column(db.DECIMAL(10, 2), nullable=False)
    createdAt = db.Column(db.DateTime(timezone=True),server_default=func.now(), nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # company_id = db.Column(db.Integer, db.ForeignKey('company.companyId'), nullable=False)
    # administrator_id = db.Column(db.ForeignKey('administrator.AdministratorId'), nullable=False)

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

    # hard coded sample data for stocks
    if not StockInventory.query.first():
        stock1 = StockInventory(stockName='NVIDIA Corp', ticker='NVDA', quantity='500', currentMarketPrice='189.11')
        stock2 = StockInventory(stockName='Intel Corp', ticker='INTC', quantity='500', currentMarketPrice='37.43')
        stock3 = StockInventory(stockName='Advanced Micro Devices Inc', ticker='AMD', quantity='500', currentMarketPrice='235.56')
        stock4 = StockInventory(stockName='Amazon.com Inc', ticker='AMZN', quantity='500', currentMarketPrice='225.22')
        db.session.add(stock1)
        db.session.add(stock2)
        db.session.add(stock3)
        db.session.add(stock4)
        db.session.commit()

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
    if user_id.startswith("user-"):
        return User.query.get(int(user_id.replace("user-", "")))
    elif user_id.startswith("admin-"):
        return Administrator.query.get(int(user_id.replace("admin-", "")))

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
        else:
            flash('Invalid username or password', 'error')
    return render_template("login.html")

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ADMIN SIGNUP & LOGIN
@app.route('/admin-register', methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        # Verify the admin registration key
        admin_key = request.form.get("admin_key")
        if admin_key != "iamadmin":
            return redirect(url_for("admin_login"))
       
        hashed_password = bcrypt.generate_password_hash(request.form.get("password")).decode('utf-8')
        admin = Administrator(
            Fullname=request.form.get("Fullname"),
            Email=request.form.get("Email"),
            password=hashed_password
        )
        db.session.add(admin)
        db.session.commit()
        return redirect(url_for("admin_login"))
   
    return render_template("admin_sign_up.html")

@app.route('/admin-login', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        administrator = Administrator.query.filter_by(Email=request.form.get("Email")).first()
        if administrator and bcrypt.check_password_hash(administrator.password, request.form.get("password")):
            login_user(administrator)
            return redirect(url_for("admin_dashboard"))
        else:
            flash('Invalid username or password', 'error')
    return render_template("admin_login.html")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

# More flexible role-based decorator
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Example route allowing multiple roles
@app.route('/manage-content')
@login_required
@role_required('admin', 'editor')
def manage_content():
    return render_template("manage_content.html")
# User management routes for Admins
@app.route('/delete-user/', methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/change-role/', methods=["POST"])
@login_required
@admin_required
def change_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get("role")
    
    # Validate the role
    if new_role in ["user", "admin", "editor"]:
        user.role = new_role
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

# Admin only role
@app.route('/admin-dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()  # Get all users for admin to manage
    return render_template('admin_dashboard.html', users=users)

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

@app.route("/createstocks", methods=['GET', 'POST'])
@login_required
@admin_required
def add_stocks():
    if request.method == 'POST':
            stockName = request.form.get('stockName')
            ticker = request.form.get('ticker')
            quantity = int(request.form('quantity'))
            currentMarketPrice = float(request.form('currentMarketPrice'))

            new_stock = StockInventory(
                stockName=stockName,
                ticker=ticker,
                quantity=quantity,
                currentMarketPrice=currentMarketPrice
            )
            db.session.add(new_item)
            db.session.commit()

            flash(f'Stock "{stockName}" added successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
            
    return render_template('admin_dashboard.html')

@app.route('/editstocks/<int:item_id>', methods=['GET', 'POST'])
def edit_item(StockInventory_id):
    stock = StockInventory.query.get_or_404(StockInventory_id)
    if request.method == 'POST':
        stock.name = request.form['name']
        stock.quantity = int(request.form['quantity'])
        stock.price = float(request.form['price'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_item.html', stock=stock)

@app.route('/deletestocks/<int:item_id>', methods=['POST'])
def delete_item(StockInventory_id):
    item = StockInventory.query.get_or_404(StockInventory_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/purchasingstocks', methods=["GET", "POST"])
def purchasingstocks():
    stock_symbol = request.form.get('symbol')
    amount_stock = request.form.get('quantity')

    # Validate inputs
    if not stock_symbol or not amount_stock:
        flash("Order couldn't go through: Missing information.")
        return redirect(url_for('purchasingstocks'))

    try:
        amount = int(amount_stock)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Order couldn't go through: Invalid amount.")
        return redirect(url_for('market'))

    # Here, you'd typically get the stock price from an API
    # For this example, let's assume a dummy stock price
    stock_price = StockInventory.query.filter_by(currentMarketPrice='symbol').first()
    total_cost = stock_price * amount

    new_order = OrderHistory(
        order_type='buy',
        quantity=amount,
        total_amount=total_cost,
        ticker=stock_symbol,
        date=db.DateTime(timezone=True),server_default=func.now()
    )

    try:
        db.session.add(new_order)
        db.session.commit()
        flash(f"Successfully bought {amount} shares of {stock_symbol}.")
        return redirect(url_for('portfolio'))
    except:
        db.session.rollback()
        flash("Order couldn't go through.")
        return redirect(url_for('market'))
    

@app.route("/sellingstocks")
@login_required
def sell_page():
    return render_template("sellingstocks.html")
    
# MARKET_HOURS = {
    # "NYSE": {
        # "open": datetime.time(9, 30),
        # "close": datetime.time(16, 00),
        # "timezone": "America/New_York",
    # }
# }

@admin_required
def change_stock_market_hours(current_user, exchange: str, open_time: datetime.time, close_time: datetime.time):
    """
    Changes the opening and closing hours for a specified stock exchange.
    This function can only be called by an admin, enforced by the decorator.
    """
    if exchange in MARKET_HOURS:
        print(f"⚙️ Changing hours for {exchange} from {MARKET_HOURS[exchange]['open']} to {open_time}...")
        MARKET_HOURS[exchange]["open"] = open_time
        MARKET_HOURS[exchange]["close"] = close_time
        print(f" Successfully updated {exchange} hours to Open: {open_time}, Close: {close_time}")
        return MARKET_HOURS[exchange]
    else:
        print(f" Exchange {exchange} not found.")
        return None
    
@admin_required
def open_season():
    today = date.today()
    
    # 1. Check for weekends (Saturday or Sunday)
    # The weekday() method returns Monday as 0 and Sunday as 6.
    if today.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
        return False

    # 2. Check for U.S. federal holidays
    # Create an instance of the holidays library for the U.S.
    # It will automatically generate a list of holidays for the current year.
    us_holidays = holidays.country_holidays('US')
    if today in us_holidays:
        return False

    # If it's not a weekend and not a holiday, the market is open
    return True

@app.route('/market-status', methods=['GET'])
def market_status():
    if open_season():
        return jsonify({
            "status": "Open",
            "message": "The market is currently open for business."
        })
    else:
        return jsonify({
            "status": "Closed",
            "message": "The market is currently closed. Please check back during standard business hours."
        })



if __name__ == "__main__":
    app.run(debug=True)
