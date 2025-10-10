from calendar import weekday
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
    user_portfolio = db.relationship('Portfolio', backref=db.backref('user'), uselist=False)
    user_orderhistory = db.relationship('OrderHistory', backref=db.backref('user'))
    admin_id = db.Column(db.ForeignKey('administrator.AdministratorId'), unique=True)

    def get_id(self):
        return f"user-{self.id}"

# Admin Model (Hannah)
class Administrator(UserMixin, db.Model):
    __tablename__ = 'administrator'
    AdministratorId = db.Column(db.Integer, primary_key=True)
    Fullname = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text(255), nullable=False)
    admin_orderhistory = db.relationship('OrderHistory', backref=db.backref('administrator'))
    admin_stocks = db.relationship('StockInventory', backref=db.backref('administrator'))
    admin_workingday = db.relationship('WorkingDay', backref=db.backref('administrator'))
    admin_exception= db.relationship('Exception', backref=db.backref('administrator'))
    admin_usermanagement = db.relationship('User', backref=db.backref('administrator'))

    def get_id(self):
        return f"admin-{self.AdministratorId}"

    @property
    def role(self):
        return "admin"

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
    admin_id = db.Column(db.ForeignKey('administrator.AdministratorId'))

# Porfolio Model (Jenelle)
class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    walletAmount = db.Column(db.Integer, nullable=False, default=10000)
    createdAt = db.Column(db.DateTime(timezone=True),server_default=func.now(), nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)

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
    admin_id = db.Column(db.ForeignKey('administrator.AdministratorId'))

# class WorkingDay (Natalie)
class WorkingDay(db.Model):
    __tablename__ = 'working_day'
    workingDayId = db.Column(db.Integer, primary_key=True)
    dayOfWeek = db.Column(db.Integer)  # 0=Monday, 6=Sunday
    startTime = db.Column(db.Integer)
    endTime = db.Column(db.Integer)
    createdAt = db.Column(db.Integer)
    updatedAt = db.Column(db.Integer)
    admin_id = db.Column(db.ForeignKey('administrator.AdministratorId'), unique=True)

# class Exception (Natalie)
class Exception(db.Model):
    __tablename__ = 'exception'
    exceptionId = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(255))
    holidayDate = db.Column(db.Date)
    createdAt = db.Column(db.Integer)
    updatedAt = db.Column(db.Integer)
    admin_id = db.Column(db.ForeignKey('administrator.AdministratorId'), unique=True)

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
            flash('Invalid username or password', 'login-error')
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
       
        hashed_password = bcrypt.generate_password_hash(request.form.get("password")).decode('utf-8')
        admin = Administrator(
            Fullname=request.form.get("Fullname"),
            Email=request.form.get("Email"),
            password=hashed_password
        )
        db.session.add(admin)
        db.session.commit()
        return redirect(url_for("admin_login"))
   
    return render_template("admin_register.html")

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


# market functions BUY/SELL (for user)
@app.route('/purchasingstocks', methods=["GET", "POST"])
@login_required
def purchasingstocks():
    if request.method == "GET":
        return render_template("purchasingstocks.html")

    stock_symbol = request.form.get('symbol')
    amount_stock = request.form.get('quantity')

    # Validate inputs
    if not stock_symbol or not amount_stock:
        flash("Order couldn't go through: Missing information.", 'buy-error')
        return redirect(url_for('purchasingstocks'))

    try:
        amount = int(amount_stock)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Order couldn't go through: Invalid amount.", 'buy-error')
        return redirect(url_for('market'))

    # getting stock price from stock in db
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
        flash("Order couldn't go through.", 'buy-error')
        return redirect(url_for('purchasingstocks'))
    
@app.route("/sellingstocks")
@login_required
def sellingstocks():
    if request.method == "GET":
        return render_template("sellingstocks.html")

    stock_symbol = request.form.get('symbol')
    amount_stock = request.form.get('quantity')

    # Validate inputs
    if not stock_symbol or not amount_stock:
        flash("Order couldn't go through: Missing information.", 'sell-error')
        return redirect(url_for('sellingstocks'))

    try:
        amount = int(amount_stock)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Order couldn't go through: Invalid amount.", 'sell-error')
        return redirect(url_for('market'))

    # getting stock price from stock in db
    stock_price = StockInventory.query.filter_by(currentMarketPrice='symbol').first()
    total_cost = stock_price * amount

    new_order = OrderHistory(
        order_type='sell',
        quantity=amount,
        total_amount=total_cost,
        ticker=stock_symbol,
        date=db.DateTime(timezone=True),server_default=func.now()
    )

    try:
        db.session.add(new_order)
        db.session.commit()
        flash(f"Successfully sold {amount} shares of {stock_symbol}.")
        return redirect(url_for('portfolio'))
    except:
        db.session.rollback()
        flash("Order couldn't go through.", 'sell-error')
        return redirect(url_for('sellingstocks'))
    
# MARKET_HOURS = {
    # "NYSE": {
        # "open": datetime.time(9, 30),
        # "close": datetime.time(16, 00),
        # "timezone": "America/New_York",
    # }
# }

# ADMIN FUNCTIONS
@app.route("/createstocks", methods=['GET', 'POST'])
@login_required
@admin_required
def add_stocks():
    if request.method == 'POST':
            stockName = request.form['stockName']
            ticker = request.form['ticker']
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
            
            new_stock = StockInventory(
                stockName=stockName,
                ticker=ticker,
                quantity=quantity,
                currentMarketPrice=price
            )
            db.session.add(new_stock)
            db.session.commit()

            flash("Stock added to the Market.", "success")
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_dashboard.html')

@app.route('/editstocks/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(StockInventory_id):
    stock = StockInventory.query.get_or_404(StockInventory_id)
    if request.method == 'POST':
        stock.name = request.form['name']
        stock.quantity = int(request.form['quantity'])
        stock.price = float(request.form['price'])
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_item.html', stock=stock)

@app.route('/deletestocks/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_item(StockInventory_id):
    item = StockInventory.query.get_or_404(StockInventory_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@admin_required
def change_stock_market_hours(current_user, exchange: str, open_time: datetime.time, close_time: datetime.time):
    """
    Changes the opening and closing hours for a specified stock exchange.
    This function can only be called by an admin, enforced by the decorator.
    """
    working_day = WorkingDay.query.filter_by(dayOfWeek=weekday).first()

    if working_day:
        print(f"⚙️ Changing hours for {exchange} from {working_day.open_time} to {open_time}...")
        working_day.open_time = open_time
        working_day.close_time = close_time
    else:
        # If not found, create a new entry
        print(f"➕ Creating new working day entry for {exchange}.")
        working_day = WorkingDay(
            exchange=exchange,
            open_time=open_time,
            close_time=close_time,
            timezone="America/New_York"  # Or make this dynamic
        )
        db.session.add(working_day)

    db.session.commit()
    print(f"✅ Successfully updated {exchange} hours to Open: {open_time}, Close: {close_time}")
    return {
        "exchange": exchange,
        "open": open_time,
        "close": close_time
    }
    
@admin_required
def open_season():
    today = date.today()
    
    # Check for weekends (Saturday or Sunday)
    # The weekday() method returns Monday as 0 and Sunday as 6.
    if Exception.query.filter_by(date=today).first():
        return False

    # Check for U.S. federal holidays
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
