import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RestaurantForm, MenuForm, OrderForm, MapForm
from flaskblog import app,db, bcrypt
from flaskblog.models import User,Post, Place, Menu, Orders
from flask_login import login_user, current_user, logout_user, login_required
from geopy.distance import great_circle
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from flask_user import roles_required
import plotly.express as px
import stripe
import boto3
from google.cloud import vision
import io

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page',1,type = int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page = 5)
    return render_template('home.html', posts =posts)

@app.route('/about')
def about():
    return render_template('about.html', title = "About")

@app.route('/register', methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if form.user.data:
            user = User(username = form.username.data, email = form.email.data, password = hashed_password, userAddress = form.userAddress.data, role = "user")
            db.session.add(user)
            db.session.commit()
            flash(f'Your account has been created! You are now able to log in', 'success')
        elif form.restaurant.data:
            user = User(username = form.username.data, email = form.email.data, password = hashed_password, userAddress = form.userAddress.data, role = "restaurant")
            db.session.add(user)
            db.session.commit()
            flash(f'Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',title = 'Register', form = form)

@app.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
            return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password' , 'danger')
    return render_template('login.html',title = 'Login', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (250,200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def saveMap(map, username):
    map_fn = "personalMap" + username + ".html"
    map_path = os.path.join(app.root_path, 'templates\personalMaps', map_fn)
    map.save(map_path)
    return map_fn

def makeMap(vers):
    places = Place.query.all()
    users = User.query.filter(User.role == "restaurant")
    geolocator = Nominatim(user_agent="name")
    location = geolocator.geocode(current_user.userAddress)
    f_map = folium.Map((location.latitude, location.longitude), zoom_start=12)
    data = []
    dict_home = dict()
    dict_home["name"] = location.address
    dict_home["lat"] = location.latitude
    dict_home["long"] = location.longitude
    data.append(dict_home)
    if vers == "True":
        for place in places:
            place_dict = dict()
            location_2 = geolocator.geocode(place.address)
            if location_2 == None:
                continue
            place_dict["name"] = place.location_name
            place_dict["lat"] = location_2.latitude
            place_dict["long"] = location_2.longitude
            data.append(place_dict)
        df_data = pd.DataFrame(data)
        for index, row in df_data.iterrows():
            if row['lat'] == None or row['long'] == None:
                continue
            if row['name'] == location.address and current_user.role == "user":
                folium.Marker([row['lat'], row['long']], icon=folium.Icon(color='red', icon="home"),
                              popup="Home").add_to(f_map)
            elif row['name'] == location.address and current_user.role == "restaurant":
                folium.Marker([row['lat'], row['long']], icon=folium.Icon(color='red', icon="home"),
                              popup="Home").add_to(f_map)
            else:
                folium.Marker([row['lat'], row['long']], popup=row['name']).add_to(f_map)
        return f_map
    else:
        for user in users:
            user_dict = dict()
            location_2 = geolocator.geocode(user.userAddress)
            if location_2 == None:
                continue
            user_dict["name"] = user.username
            user_dict["lat"] = location_2.latitude
            user_dict["long"] = location_2.longitude
            data.append(user_dict)
        df_data = pd.DataFrame(data)
        for index, row in df_data.iterrows():
            if row['lat'] == None or row['long'] == None:
                continue
            if row['name'] == location.address and current_user.role == "user":
                folium.Marker([row['lat'], row['long']], icon=folium.Icon(color='red', icon="home"),
                              popup="Home").add_to(f_map)
            elif row['name'] == location.address and current_user.role == "restaurant":
                folium.Marker([row['lat'], row['long']], icon=folium.Icon(color='red', icon="home"),
                              popup="Home").add_to(f_map)
            else:
                folium.Marker([row['lat'], row['long']], popup=row['name']).add_to(f_map)
        return f_map
@app.route('/account/<mapVal>', methods = ['GET','POST'])
@login_required
def account(mapVal):
    form = UpdateAccountForm()
    form_m = MapForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
    if form_m.validate_on_submit():
        if form_m.events.data:
            return redirect(url_for('account', mapVal = True))
        else:
            return redirect(url_for('account', mapVal = False))
    elif request.method == "GET" and current_user.role == "user":
        form.username.data = current_user.username
        form.email.data = current_user.email
    elif request.method == "GET" and current_user.role == "restaurant":
        form.username.data = current_user.username
        form.email.data = current_user.email
        menu = Menu.query.filter_by(author=current_user).first()
        if not menu:
            flash("You Must Create a Menu First!", 'danger')
            return redirect(url_for("createMenu"))
    places = Place.query.all()
    users = User.query.filter(User.role == "restaurant")
    geolocator = Nominatim(user_agent="name")
    location = geolocator.geocode(current_user.userAddress)
    f_map = folium.Map((location.latitude, location.longitude), zoom_start=12)
    data = []
    dict_home = dict()
    dict_home["name"] = location.address
    dict_home["lat"] = location.latitude
    dict_home["long"] = location.longitude
    data.append(dict_home)
    if current_user.role == "user":
        f_map = makeMap(mapVal)
    if current_user.role == "restaurant":
        orders = Orders.query.filter_by(author=current_user).all()
        menu = Menu.query.filter_by(author=current_user).first()
        if not menu:
            flash("You Must Create a Menu First!", 'danger')
            return redirect(url_for("createMenu"))
        totalSales = 0
        totalSales += menu.num1 * menu.price1
        totalSales += menu.num2 * menu.price2
        totalSales += menu.num3 * menu.price3
        totalSales += menu.num4 * menu.price4
        totalSales += menu.num5 * menu.price5
        moneyRaise = totalSales * menu.percentage
        for order in orders:
            place_dict = dict()
            location_2 = geolocator.geocode(order.userAddress)
            place_dict["name"] = order.username
            place_dict["lat"] = location_2.latitude
            place_dict["long"] = location_2.longitude
            data.append(place_dict)
        df_data = pd.DataFrame(data)
        for index, row in df_data.iterrows():
            if row['name'] == location.address:
                folium.Marker([row['lat'], row['long']], icon=folium.Icon(color='red', icon = "home"),popup= "Home").add_to(f_map)
            else:
                folium.Marker([row['lat'],row['long']], popup=row['name']).add_to(f_map)
    path = saveMap(f_map, current_user.username)

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    if current_user.role == "user":
        return render_template('account.html', title  = 'Account', image_file = image_file, form = form,path = path, mapVal = mapVal, form_m = form_m)
    return render_template('account.html', title='Account', image_file=image_file, form=form, path=path, menu=menu,
                               created=True, totalSales=totalSales, moneyRaise = moneyRaise, mapVal = mapVal, form_m = form_m)

@app.route("/personalMap/<path>")
@login_required
def loadMap(path):
    return render_template("/personalMaps/" + path)

@app.route("/post/new", methods = ['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, location = form.location.data, content = form.content.data, author = current_user)
        place = Place(location_name = form.title.data, address = form.location.data)
        db.session.add(post)
        db.session.add(place)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title = "New Post", form = form, legend = "New Post")

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    place = Place.query.get_or_404(post_id)
    distance = distanceFinder(place)
    return render_template('post.html', title = post.title, post =post, distance = distance)

def distanceFinder(place):
    geolocator = Nominatim(user_agent = "lol")
    address = place.address
    userLocation = geolocator.geocode(current_user.userAddress)
    placeLocation = geolocator.geocode(address)
    userLatLong = (userLocation.latitude, userLocation.longitude)
    placeLatLong = (placeLocation.latitude, placeLocation.longitude)
    distance = round(great_circle(userLatLong, placeLatLong).miles, 2)
    return distance

@app.route("/post/<int:post_id>/update", methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.location = form.location.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.location.data = post.location
    return render_template('create_post.html', title = "Update Post", form = form, legend = "Update Post")

@app.route("/post/<int:post_id>/delete", methods = ['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    place = Place.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.delete(place)
    db.session.commit()
    flash('Your post has been deleted!', 'sucess')
    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page',1,type = int)
    user = User.query.filter_by(username = username).first_or_404()
    posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).paginate(page = page, per_page = 5)
    return render_template('user_posts.html', posts =posts,user = user)
'''
@app.route('/redirectRegister')
def redirectRegister():
    return render_template('redirectRegister.html')

@app.route('/registerRestaurant', methods = ['GET', 'POST'])
def registerRestaurant():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RestaurantForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        restaurant = Restaurant(username = form.username.data, email = form.email.data, password = hashed_password, userAddress = form.userAddress.data)
        db.session.add(restaurant)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('loginRestaurant'))
    return render_template('registerRestaurant.html', form = form)
'''

'''
@app.route('/loginRestaurant', methods = ['GET','POST'])
def loginRestaurant():
    if current_user.is_authenticated:
            return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        restaurant = Restaurant.query.filter_by(email=form.email.data).first()
        if restaurant and bcrypt.check_password_hash(restaurant.password, form.password.data):
            login_user(restaurant, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password' , 'danger')
    return render_template('loginRestaurant.html',title = 'Login', form = form)
'''

@app.route('/createMenu', methods = ['GET', 'POST'])
def createMenu():
    form = MenuForm()
    menu2 = Menu.query.filter_by(author=current_user).first()
    if form.validate_on_submit():
        menu = Menu(org = form.org.data, percentage = form.percentage.data, item1 = form.item1.data, item2 = form.item2.data,item3 = form.item3.data,item4 = form.item4.data,item5 = form.item5.data, price1 = form.price1.data, price2 = form.price2.data, price3 = form.price3.data, price4 = form.price4.data, price5 = form.price5.data, author = current_user)
        db.session.add(menu)
        db.session.commit()
        return redirect(url_for('home'))
    elif menu2:
        return redirect(url_for('updateMenu',menu_id = menu2.id))
    else:
        return render_template('createMenu.html', form = form, legend = "New Menu")

@app.route('/updateMenu/<int:menu_id>', methods = ['GET','POST'])
@login_required
def updateMenu(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    if menu.author != current_user:
        abort(403)
    form = MenuForm()
    if form.validate_on_submit():
        menu.org = form.org.data
        menu.percentage = form.percentage.data
        menu.item1 = form.item1.data
        menu.item2 = form.item2.data
        menu.item3 = form.item3.data
        menu.item4 = form.item4.data
        menu.item5 = form.item5.data
        menu.price1 = form.price1.data
        menu.price2 = form.price2.data
        menu.price3 = form.price3.data
        menu.price4 = form.price4.data
        menu.price5 = form.price5.data
        db.session.commit()
        flash('Your menu has been updated!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.org.data = menu.org
        form.percentage.data = menu.percentage
        form.item1.data = menu.item1
        form.item2.data = menu.item2
        form.item3.data = menu.item3
        form.item4.data = menu.item4
        form.item5.data = menu.item5
        form.price1.data = menu.price1
        form.price2.data = menu.price2
        form.price3.data = menu.price3
        form.price4.data = menu.price4
        form.price5.data = menu.price5
    return render_template('createMenu.html', title = "Update Menu", form = form, legend = "Update Menu", created = True)

@app.route('/restaurants')
def restaurants():
    users = User.query.filter(User.role == "restaurant")
    return render_template('restaurants.html',users = users)

@app.route('/thanks/<username>')
def thanks(username):
    return render_template('Thanks.html',username = username)

@app.route('/orders/<string:username>', methods = ['GET', 'POST'])
@login_required
def orders(username):
    user = User.query.filter_by(username = username).first_or_404()
    menu = Menu.query.filter_by(author = user).first()
    totalPrice = 2100
    form = OrderForm()
    if form.validate_on_submit():
        order = Orders(qty1  = form.qty1.data, qty2  = form.qty2.data, qty3  = form.qty3.data, qty4  = form.qty4.data, qty5  = form.qty5.data, author = menu.author, username = form.username.data, userAddress = form.userAddress.data)
        db.session.add(order)
        db.session.commit()
        totalPrice = form.qty1.data * menu.price1 + form.qty2.data * menu.price2 + form.qty3.data * menu.price3 + form.qty4.data * menu.price4 + form.qty5.data * menu.price5 * 100
    stripe.api_key = app.config['STRIPE_SECRET_KEY']
    price = stripe.Price.create(
        unit_amount= totalPrice,
        currency="usd",
        product="prod_HVG4aJHQfnM224",
    )
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price,
            'quantity': 1,
        }],
        mode='payment',
        success_url= url_for('thanks',username = username, _external = True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url= url_for('home', _external=True),
    )
    return render_template('orderForm.html', form = form, legend = "New Menu", menu = menu, checkout_session_id = session['id'],checkout_public_key = app.config['STRIPE_PUBLIC_KEY'])

@app.route('/orderList/<string:username>')
@login_required
def orderList(username):
    user = User.query.filter_by(username = username).first_or_404()
    menu = Menu.query.filter_by(author=user).first()
    orders = Orders.query.filter_by(author = user).all()
    currentorders = Orders.query.count()
    return render_template("orderList.html", orders = orders,menu = menu,currentorders = currentorders)

@app.route("/order/<int:order_id>/delete", methods = ['POST'])
@login_required
def delete_order(order_id):
    order = Orders.query.get_or_404(order_id)
    menu = Menu.query.filter_by(author=current_user).first()
    menu.num1 += order.qty1
    menu.num2 += order.qty2
    menu.num3 += order.qty3
    menu.num4 += order.qty4
    menu.num5 += order.qty5
    db.session.delete(order)
    db.session.commit()
    flash('Your order has been finished!', 'sucess')
    return redirect(url_for('orderList', username = current_user.username))

@app.route('/dashboard/<string:username>')
@login_required
def dashboard(username):
    user = User.query.filter_by(username = username).first_or_404()
    menu = Menu.query.filter_by(author=user).first()
    orders = Orders.query.filter_by(author = user).all()
    currentorders = Orders.query.count()
    if not menu:
        flash("You Must Create a Menu First!", 'danger')
        return redirect(url_for("createMenu"))
    organization = menu.org
    totalSales = 0
    totalSales += menu.num1 * menu.price1
    totalSales += menu.num2 * menu.price2
    totalSales += menu.num3 * menu.price3
    totalSales += menu.num4 * menu.price4
    totalSales += menu.num5 * menu.price5
    moneyRaise = round(totalSales * menu.percentage /100,2)
    maxNum = 0
    a = 0
    b = 0
    c = 0
    d = 0
    e = 0
    a = menu.num1
    b = menu.num2
    c = menu.num3
    d = menu.num4
    e = menu.num5
    nums = [a,b,c,d,e]
    maxNum = -1
    maxInd = 0
    totalNums = 0
    for i in range(0,len(nums)):
        if nums[i] > maxNum:
            maxInd = i
            maxNum = nums[i]
        totalNums += nums[i]
    maxInd +=1
    if maxInd == 1:
        maxItem = menu.item1
    if maxInd == 2:
        maxItem = menu.item2
    if maxInd == 3:
        maxItem = menu.item3
    if maxInd == 4:
        maxItem = menu.item4
    if maxInd == 5:
        maxItem = menu.item5
    geolocator = Nominatim(user_agent="name")
    location = geolocator.geocode(current_user.userAddress)
    f_map = folium.Map((location.latitude, location.longitude), zoom_start=12)
    data = []
    dict_home = dict()
    dict_home["name"] = location.address
    dict_home["lat"] = location.latitude
    dict_home["long"] = location.longitude
    data.append(dict_home)
    for order in orders:
        place_dict = dict()
        location_2 = geolocator.geocode(order.userAddress)
        place_dict["name"] = order.username
        place_dict["lat"] = location_2.latitude
        place_dict["long"] = location_2.longitude
        data.append(place_dict)
    df_data = pd.DataFrame(data)
    for index, row in df_data.iterrows():
        if row['name'] == location.address:
            folium.Marker([row['lat'], row['long']], icon=folium.Icon(color='red', icon="home"),
                          popup="Home").add_to(f_map)
        else:
            folium.Marker([row['lat'], row['long']], popup=row['name']).add_to(f_map)
    path = saveMap(f_map, current_user.username)
    Item = [menu.item1,menu.item2,menu.item3,menu.item4,menu.item5]
    QuantitySold = [menu.num1, menu.num2, menu.num3, menu.num4, menu.num5]
    data_bar = dict()
    data_bar['Item'] = Item
    data_bar["Quantity Sold"] = QuantitySold
    fig = px.bar(data_bar, x = 'Item', y = 'Quantity Sold', title = "Items Sold")
    bar_fn = "personalChart" + username + ".html"
    bar_path = os.path.join(app.root_path, 'templates\personalCharts', bar_fn)
    fig.write_html(bar_path)
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    if totalNums == 0:
        return render_template('dashboard.html', currentorders=currentorders, totalSales=round(totalSales, 2),
                               moneyRaise=moneyRaise, organization=organization, maxItem=maxItem, maxNum=maxNum,
                               percent= 0, path=path, barpath=bar_fn,
                               image_file=image_file)
    return render_template('dashboard.html', currentorders = currentorders,totalSales  = round(totalSales,2), moneyRaise = moneyRaise, organization = organization,maxItem = maxItem, maxNum = maxNum, percent = round(maxNum/totalNums,2)*100,path=path, barpath = bar_fn, image_file = image_file)

@app.route('/loadChart/<path>')
def loadChart(path):
    return render_template('/personalCharts/' + path)

@app.route('/receiptAnalyzer')
def receiptAnalzyer():
    path = 'C:/Users/HP/Desktop/EpsilonHacks-master/Website/flaskblog/static/'
    s3 = boto3.client('s3')
    s3.download_file('breaddyandbuttery1', 'orderimage.png', path + 'orderimage.png')

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(path + 'orderimage.png')
    picture_fn = random_hex + f_ext

    output_size = (500,500)
    i = Image.open(path + "orderimage.png")
    i.thumbnail(output_size)
    i.save(path + picture_fn)

    f = "C:/Users/HP/Desktop/EpsilonHacks-master/Website/flaskblog/static/orderimage.png"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/HP/Desktop/crafty-sound-269020-513337242ac1.json"
    image_file = url_for('static', filename=picture_fn)
    client = vision.ImageAnnotatorClient()
    with io.open(f, 'rb') as image:
        content = image.read()

    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    response = client.document_text_detection(image=image)

    x = []
    for text in texts:
        x.append(text.description)
        break
    y = str(x[0])
    y = y.replace("\n", ",")
    y = y.replace("(", ",")
    y = y.replace(")", "")
    arr = y.split(",")

    username = ""
    userAddress = ""
    qty1 = ""
    qty2 = ""
    qty3 = ""
    qty4 = ""
    qty5 = ""
    restaurantName = ""
    for j in arr:
        if "Restaurant" in j:
            restaurantName = j.replace("Restaurant: ", "")
            restaurantName = restaurantName.strip()
    user = User.query.filter_by(username=restaurantName).first_or_404()
    menu = Menu.query.filter_by(author=user).first()
    for i in range(0,len(arr)):
        if "Username" in arr[i]:
            username = arr[i].replace("Username: ", "")
            username = username.strip()
            print(username)
        if "UserAddress" in arr[i]:
            userAddress = arr[i].replace("UserAddress: ", "")
            userAddress += ","+ arr[i+1] +"," + arr[i+2] + "," + arr[i+3]
            userAddress = userAddress.strip()
            print(userAddress)
        if menu.item1 in arr[i]:
            qty1 = arr[i].replace(menu.item1 + " " + str(menu.price1) + " ", "")
            qty1 = qty1.strip()
            qty1 = float(qty1)
            print(qty1)
        if menu.item2 in arr[i]:
            qty2 = arr[i].replace(menu.item2 + " " + str(menu.price2) + " ", "")
            qty2 = qty2.strip()
            qty2 = float(qty2)
            print(qty2)
        if menu.item3 in arr[i]:
            qty3 = arr[i].replace(menu.item3 + " " + str(menu.price3) + " ", "")
            qty3 = qty3.strip()
            qty3 = float(qty3)
            print(qty3)
        if menu.item4 in arr[i]:
            qty4 = arr[i].replace(menu.item4 + " " + str(menu.price4) + " ", "")
            qty4 = qty4.strip()
            qty4 = float(qty4)
            print(qty4)
        if menu.item5 in arr[i]:
            qty5 = arr[i].replace(menu.item5 + " " + str(menu.price5) + " ", "")
            qty5 = qty5.strip()
            qty5= float(qty5)
            print(qty5)
    user = User.query.filter_by(username=restaurantName).first_or_404()
    menu = Menu.query.filter_by(author=user).first()
    order = Orders(qty1=qty1, qty2=qty2, qty3=qty3, qty4=qty4,
                   qty5=qty5, author=menu.author, username=username,
                   userAddress=userAddress)
    db.session.add(order)
    db.session.commit()
    return render_template('receiptAnalyzer.html', image_file = image_file, words = arr)
