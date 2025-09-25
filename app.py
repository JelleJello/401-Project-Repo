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

# Order History Model
# class OrderHistory(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    # ordername = db.Column(db.String(80), unique=True, nullable=False)
    # quantity = db.Column(db.String(120), unique=True, nullable=False)
    # price = db.Column(db.String(30), unique=True, nullable=False)
    # status
    # ticker
    # createdAt
    # updatedAt
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
# class stocks (Natalie)
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