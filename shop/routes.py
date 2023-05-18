from shop import app, db, bcrypt
from flask import Flask, render_template, url_for, session, flash, redirect, request, current_app, Blueprint
from flask_login import login_user, current_user, logout_user, login_required


from werkzeug.utils import secure_filename
import os

from .models import User, Product, Cart
from .forms import RegistrationForm, LoginForm, CheckoutForm, CartForm

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    products = Product.query.all()
    return render_template("home.html", products=products)

UPLOAD_FOLDER = 'static/images'

@app.route("/addproduct", methods=["GET", "POST"])
def addproduct():
    if request.method == "POST":
        name = request.form.get('product_name')
        price = float(request.form.get('price'))
        description = request.form.get('product_description')
        environment = request.form.get('product_environment')
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = secure_filename(image.filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                image.save(os.path.join(UPLOAD_FOLDER, filename))
                image_path = os.path.join(UPLOAD_FOLDER, 'images', filename)
                product = Product(name=name, price=price, description=description,
                                  environment=environment, image=image_path)
                db.session.add(product)
                db.session.commit()
                return 'Product added successfully'
            else:
                return 'Error: Start again'
        return redirect("home")
    return render_template("addproduct.html")

@app.route("/product/<int:product_id>")
def single_page(product_id):
    product = Product.query.get_or_404(product_id)
    form = CartForm()
    if form.validate_on_submit():
        cart_item = Cart(product_id=product_id)
        db.session.add(cart_item)
        db.session.commit()
        flash('Product added to cart.')
        return redirect(url_for("cart"))
    return render_template("single_page.html", product=product, form=form)


@app.route("/cart", methods=["GET", "POST"])
def cart():
    form = CartForm()
    if form.validate_on_submit():
        product_id = form.product_id.data
        product = Product.query.get(product_id)
        if not product:
            flash('Product not found.')
            return redirect(url_for("home"))
        cart_item = session.get('cart', {}).get(str(product_id))
        if cart_item:
            flash('Product already in cart.')
        else:
            cart = session.get('cart', {})
            cart[str(product_id)] = True 
            session['cart'] = cart
            flash('Product added to cart.')
        return redirect(url_for("cart"))
    cart_items = session.get('cart', {})
    product_ids = [int(key) for key in cart_items.keys()]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    cart_items = {product.id: product for product in products}
    return render_template("cart.html", form=form, cart_items=cart_items)

@app.route("/checkout", methods=['GET','POST'])
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        return render_template('success.html', title='Checkout Success!')
    return render_template('checkout.html', title='Checkout', form=form)



#extra features
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(fullname=form.fullname.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully signed up!')
        return redirect(url_for("home"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash('You\'re already logged in')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            flash('You have successfully logged in.')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have successfully signed out!')
    return redirect(url_for("home"))

