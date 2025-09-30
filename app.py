from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5

app = Flask(__name__)

bootstrap = Bootstrap5(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/flask_users_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(30), unique=True, nullable=False)

# Admin Model
class Administrator(db.Model):
    AdministratorId = db.Column(db.Integer, primary_key=True)
    Fullname = db.Column(db.String(255))
    Email = db.Column(db.String(255))
    password = db.Column(db.String(255))


# Company Model
class Company(db.Model):
    companyId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255))
    Description = db.Column(db.String(255))
    stockTotalQantity = db.Column(db.Integer)
    ticker = db.Column(db.Integer)
    currentMarketPrice = db.Column(db.Integer)
    createdAt = db.Column(Integer)
    updatedAt = db.Column(Integer)

# Financial Transaction Model
class Financial_transaction(db.Model):
    FinancialTransactionId = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    type_BUYSELL = db.Column(db.String(255))
    createdAt = db.Column(db.Integer)
    customerAccountNumber = db.Column(db.Integer, ForeignKey)
    Customer:companyId = db.Column(db.Integer, ForeignKey)
    Company:orderId = db.Column(db.Integer, ForeignKey)
    OrderHistory = 

# Order History Model
# class OrderHistory(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    # ordername = 
    # quantity = 
    # price = 
    # ticker
    # createdAt
    # updatedAt
    # userid (db.ForeignKey('user.id')
    # StockInventoryid (db.ForeignKey('StockInventory.id'))
    # StockInvenntory (db.ForeignKey('StockInventory'))
    # Administrator (db.ForeignKey('Administrator'))

# Porfolio Model
# class Portfolio(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    

# StockInventory Model
# class StockInventory(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    



# class user profile (Natalie)
class User_Profile(db.Model):
    user_profile_id = db.Column(db.Integer, primary_key=True)
    user_profile = db.Column(db.String(255))
    stocks = db.Column(db.String)
    portfolio = db.Column(db.String)
# avatar?
    
# class stocks (Natalie)
class Stocks(db.Model):
    stock_id = db.Column(db.Integer, primary_key=True)
    stock_ticker = db.Column(db.Float)
    company = db.Column(db.String)
    initial_price = db.Column(db.Float)
    available_stocks = db.Column(db.Integer)
# Stocks (Natalie)
# Administrator (Hannah)
# Company (Hannah)
# Financial_transaction (Hannah)
# Order_history (Jenelle)
# Portfolio (Jenelle)
# Stock_inventory (Jenelle)


# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def home():
    users = User.query.all()
    return render_template("home.html", users=users)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('signup'))
        
        try:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error adding user: {str(e)}', 'error')
            return redirect(url_for('signup'))
    
    return render_template('signup.html')

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")

@app.route("/market")
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
