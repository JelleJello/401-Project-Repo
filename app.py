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
    createdAt = db.Column(db.DateTime(timezone=True),server_default=func.now(), nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    admin_id = db.Column(db.ForeignKey('administrator.AdministratorId'), unique=True)

# class Exception (Natalie)
class Exception(db.Model):
    __tablename__ = 'exception'
    exceptionId = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(255))
    holidayDate = db.Column(db.Date)
    createdAt = db.Column(db.DateTime(timezone=True),server_default=func.now(), nullable=False)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
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
    stock = StockInventory.query.all()  # Get all stocks for admin to manage
    return render_template('admin_dashboard.html', stock=stock)

@app.route("/portfolio")
@login_required
def portfolio():
    user_portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    wallet_amount = user_portfolio.walletAmount if user_portfolio else 0
    orderhistory = OrderHistory.query.filter_by(user_id=current_user.id).all()

    return render_template("portfolio.html", orderhistory=orderhistory, wallet_amount=wallet_amount)

@app.route('/addfunds', methods=["GET", "POST"])
@login_required
def addfunds():
    if request.method == "POST":
        amount_to_add = request.form.get("amount")

        try:
            amount = float(amount_to_add)
            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")
        except (ValueError, TypeError):
            flash("Invalid amount entered.", "error")
            return redirect(url_for("portfolio"))

        portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
        if not portfolio:
            portfolio = Portfolio(user_id=current_user.id, walletAmount=amount)
            db.session.add(portfolio)
        else:
            portfolio.walletAmount += amount
            portfolio.updatedAt = datetime.utcnow()

        db.session.commit()
        flash(f"${amount:,.2f} successfully added to your wallet!", "success")
        return redirect(url_for("portfolio"))

    return render_template("addfunds.html")

@app.route("/market")
@login_required
def market():
    stocks = StockInventory.query.all()
    return render_template("market.html", stocks=stocks)

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

    if not stock_symbol or not amount_stock:
        flash("Order couldn't go through: Missing information.", 'buy-error')
        return redirect(url_for('purchasingstocks'))

    try:
        amount = int(amount_stock)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Order couldn't go through: Invalid amount.", 'buy-error')
        return redirect(url_for('purchasingstocks'))

    stock = StockInventory.query.filter_by(ticker=stock_symbol).first()
    if not stock:
        flash("Stock not found in inventory.", 'buy-error')
        return redirect(url_for('purchasingstocks'))

    stock_price = float(stock.currentMarketPrice)
    total_cost = stock_price * amount

    new_order = OrderHistory(
        orderType='buy',
        orderQuantity=amount,
        totalOrderAmount=total_cost,
        ticker=stock_symbol,
        user_id=current_user.id
    )

    try:
        db.session.add(new_order)
        db.session.commit()
        flash(f"Successfully bought {amount} shares of {stock_symbol}.", 'success')
        return redirect(url_for('portfolio'))
    except Exception as e:
        db.session.rollback()
        flash("Order couldn't go through. Please try again.", 'buy-error')
        return redirect(url_for('purchasingstocks'))


# selling stocks adds to wallet
@app.route('/sellingstocks', methods=["GET", "POST"])
@login_required
def sellingstocks():
    if request.method == "GET":
        return render_template("sellingstocks.html")

    stock_symbol = request.form.get('symbol')
    amount_stock = request.form.get('quantity')

    if not stock_symbol or not amount_stock:
        flash("Order couldn't go through: Missing information.", 'sell-error')
        return redirect(url_for('sellingstocks'))

    try:
        amount = int(amount_stock)
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Order couldn't go through: Invalid amount.", 'sell-error')
        return redirect(url_for('sellingstocks'))

    stock = StockInventory.query.filter_by(ticker=stock_symbol).first()
    if not stock:
        flash("Stock not found in inventory.", 'sell-error')
        return redirect(url_for('sellingstocks'))

    stock_price = float(stock.currentMarketPrice)
    total_cost = stock_price * amount

    new_order = OrderHistory(
        orderType='sell',
        orderQuantity=amount,
        totalOrderAmount=total_cost,
        ticker=stock_symbol,
        user_id=current_user.id
    )

    try:
        db.session.add(new_order)
        db.session.commit()
        flash(f"Successfully sold {amount} shares of {stock_symbol}.", 'success')
        return redirect(url_for('portfolio'))
    except Exception as e:
        db.session.rollback()
        flash("Order couldn't go through. Please try again.", 'sell-error')
        return redirect(url_for('purchasingstocks'))
    

# ADMIN FUNCTIONS
@app.route("/create-stocks", methods=["GET", "POST"])
@login_required
@admin_required
def add_stocks():
    if request.method == 'POST':
        stockname = request.form['stockName']
        ticker = request.form['ticker']
        quantity = request.form['quantity']
        marketprice = request.form['price']
        
        if not stockname or not ticker or not quantity or not marketprice:
            flash('Make sure all parameters are met', 'error')
            return redirect(url_for('admin_dashboard'))
        
        try:
            new_stock = StockInventory(stockName=stockname, ticker=ticker, quantity=quantity, currentMarketPrice=marketprice)
            db.session.add(new_stock)
            db.session.commit()
            flash('Stock added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error in adding the Stock: {str(e)}', 'error')
            return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_dashboard.html')

@app.route("/update-stock/", methods=["GET", "POST"])
@login_required
@admin_required
def update_stock(id):
    stock = StockInventory.query.get_or_404(id)
    
    if request.method == 'POST':
        stockname = request.form['stockName']
        ticker = request.form['ticker']
        quantity = request.form['quantity']
        marketprice = request.form['price']

        if not stockname or not ticker or not quantity or not marketprice:
            flash('Make sure all parameters are met', 'error')
            return redirect(url_for('admin_dashboard', id=id))
        
        try:
            stock.stockName = stockname
            stock.ticker = ticker
            stock.quantity = quantity
            stock.currentMarketPrice = marketprice
            db.session.commit()
            flash('Stock updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error updating the stock: {str(e)}', 'error')
            return redirect(url_for('update_stock', id=id))            
            
    return render_template("admin_dashboard.html", stock=stock)


@app.route("/delete-stock/<int:id>")
@login_required
@admin_required
def delete_stock(id):
    stock = StockInventory.query.get_or_404(id)
    try:
        db.session.delete(stock)
        db.session.commit()
        flash('Stock deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error with deleting stock: {str(e)}', 'error')
    return redirect(url_for('get_stocks'))


@app.route("/liststocks", methods=["GET"])
@login_required
@admin_required
def get_stocks():
    stocks = StockInventory.query.all()
    return render_template("admin_dashboard.html", stocks=stocks)

@app.route("/manage_markethours", methods=['GET', 'POST'])
@login_required
@admin_required
def manage_markethours():
    if request.method == 'POST':
        day_of_week = int(request.form.get('dayOfWeek'))  # 0=Monday, 6=Sunday
        start_time = int(request.form.get('startTime'))  # in minutes
        end_time = int(request.form.get('endTime'))      # in minutes

        working_day = WorkingDay.query.filter_by(dayOfWeek=day_of_week).first()
        if not working_day:
            working_day = WorkingDay(dayOfWeek=day_of_week)
            db.session.add(working_day)

        working_day.startTime = start_time
        working_day.endTime = end_time
        db.session.commit()
        return redirect(url_for('manage_markethours'))

    return render_template('manage_markethours.html')
    
@app.route('/add_holiday', methods=['GET', 'POST'])
def add_holiday():
    if request.method == 'POST':
        holiday_date_str = request.form.get('holidayDate')  # format: 'YYYY-MM-DD'
        reason = request.form.get('reason')
        holiday_date = date.fromisoformat(holiday_date_str)

        # Check if already exists
        existing_exception = Exception.query.filter_by(holidayDate=holiday_date).first()
        if not existing_exception:
            new_exception = Exception(holidayDate=holiday_date, reason=reason)
            db.session.add(new_exception)
            db.session.commit()
        return redirect(url_for('manage_markethours'))

    return render_template('manage_markethours.html')


if __name__ == "__main__":
    app.run(debug=True)
