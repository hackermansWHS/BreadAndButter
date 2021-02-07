from flaskblog import db,bcrypt
from flaskblog.models import User,Post,Place,Menu,Orders
import pandas as pd
def create_restaurants():
    df = pd.read_csv('static/hack.csv', header = 0)
    print(df)
    usernames = df['Name'].to_list()
    addresses = df["Address"].to_list()
    charity = df["Charity"].to_list()
    percentage = df["Percentage"].astype(float).to_list()
    item1 = df["Item1"].to_list()
    price1 = df["Item1Price"].astype(float).to_list()
    item2 = df["Item2"].to_list()
    price2 = df["Item2Price"].astype(float).to_list()
    item3 = df["Item3"].to_list()
    price3 = df["Item3Price"].astype(float).to_list()
    item4 = df["Item4"].to_list()
    price4 = df["Item4Price"].astype(float).to_list()
    item5 = df["Item5"].to_list()
    price5 = df["Item5Price"].astype(float).to_list()
    '''
    for i in range(0,len(usernames)):
        if i != 0:
            email = usernames[i] + "@demo.com"
            password = "12345"
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username = usernames[i], email = email, password = hashed_password, userAddress = addresses[i], role = "restaurant")
            db.session.add(user)
            db.session.commit()
    '''

    users = User.query.all()
    i = 0
    for i in range(0,len(usernames)):
        user = User.query.filter_by(username = usernames[i]).first()
        menu = Menu(org = charity[i], percentage = percentage[i], item1 = item1[i], price1 = price1[i], item2 = item2[i], price2 = price2[i], item3 = item3[i], price3 = price3[i], item4 = item4[i], price4 = price4[i], item5 = item5[i], price5 = price5[i], author = user)
        db.session.add(menu)
        db.session.commit()
        print(i)
        print(user.email)
        i +=1
#user = User(username = form.username.data, email = form.email.data, password = hashed_password, userAddress = form.userAddress.data, role = "restaurant")
#menu = Menu(org = form.org.data, percentage = form.percentage.data, item1 = form.item1.data, item2 = form.item2.data,item3 = form.item3.data,item4 = form.item4.data,item5 = form.item5.data, price1 = form.price1.data, price2 = form.price2.data, price3 = form.price3.data, price4 = form.price4.data, price5 = form.price5.data, author = current_user)
create_restaurants()
