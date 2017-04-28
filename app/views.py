"""
#620078849 - Romario Martin
#xxxxxxxxx - Ramone Dobson
#xxxxxxxxx - Michael Green
#xxxxxxxxx - Neelam Samtani
"""
import os
from app import app, db
from datetime import *
from flask import render_template, request, redirect, url_for,jsonify,session,send_file

from app.models import User, Wish, Token

import json
import time
import requests
import BeautifulSoup
import bcrypt
import urlparse
import urllib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Landing page
@app.route('/')
def index():
    """Render website's home page."""
    return app.send_static_file('index.html')
    
#Sign up Route
@app.route('/api/user/register', methods=['POST'])
def signup():
    json_data = json.loads(request.data)
    user = User(json_data.get('firstname'), json_data.get('lastname'), json_data.get('username'),bcrypt.hashpw(json_data.get('password').encode('utf-8'), bcrypt.gensalt()),json_data.get('email'),datetime.now())
    if user:
        db.session.add(user)
        db.session.commit()
        json_data_response = jsonify({"error":"null","data":{'firstname':json_data.get('firstname'),'lastname':json_data.get('lastname'),'username':json_data.get('username'),'email':json_data.get('email')},"message":"Sucess"})
    else:   
        json_data_response = jsonify({"error":"1","data":{},'message':'not signed up'})
    return json_data_response

#Function to login users
@app.route('/api/user/login', methods=["POST"])
def login():
    json_data = json.loads(request.data)
    user = db.session.query(User).filter_by(email=json_data['email']).first()
    if user and user.password == bcrypt.hashpw(json_data.get('password').encode('utf-8'), user.password.decode().encode('utf-8')):
        token = Token(user.id)
        db.session.add(token)
        db.session.commit()
        json_data_response = jsonify({"error":"null","data":{'id':user.id,'username':json_data.get('username'),'token':token.token},"message":"logged"})
    else:
        json_data_response = jsonify({"error":"1","data":{},"message":'not logged'})
    return json_data_response


@app.route('/api/user/logout',methods=["POST"])
def logout():
    json_data = json.loads(request.data)
    token = db.session.query(Token).filter_by(token=json_data['token']).first()
    if token:
        db.session.delete(token)
        db.session.commit()
        json_data_response = jsonify({'status':'logged out'})
    else:
        json_data_response = jsonify({'status':'did not log out'})
    return json_data_response
    

@app.route('/api/user/<userid>',methods=["GET"])
def user(userid):
    user = db.session.query(User).filter_by(id=userid).first()
    if user:
        json_data_response = jsonify({"error":"null","data":{'id':user.id,'firstname':user.first_name,'lastname':user.last_name,'username':user.username,'email':user.email,'addon':timeinfo(user.addon)},"message":"Success"})
    else:
        json_data_response = jsonify({"error":"1","data":{},'message':'did not retrieve user'})
    return json_data_response
    

@app.route('/api/users',methods=["GET"])
def users():
    users = db.session.query(User).all()
    list_of_users=[]
    for user in users:
        list_of_users.append({'id':user.id,'firstname':user.first_name,'lastname':user.last_name,'username':user.username,'email':user.email})
    if (len(list_of_users)>=1):
        json_data_response = jsonify({"error":"null","data":{"users":list_of_users},"message":"Success"})
    else:
        json_data_response = jsonify({"error":"1","data":{},"message":"did not retrieve all users"})
    return json_data_response


@app.route('/api/user/<userid>/wishlist',methods=["GET","POST"])
def wishes(userid):
    if request.method=="GET":
        user = db.session.query(User).filter_by(id=userid).first()
        wishes = db.session.query(Wish).filter_by(userid=user.id).all()
        wishlist = []
        for wish in wishes:
            wishlist.append({'title':wish.name,'url':wish.url,'thumbnail':wish.thumbnail,'description':wish.description,'addon':timeinfo(wish.addon)})
        if(len(wishlist)>0):
            json_data_response = jsonify({"error":"null","data":{"user":user.first_name + " " + user.last_name, "wishes":wishlist},"message":"Success"})
        else:
            json_data_response = jsonify({"error":"1","data":{},"message":"Unable to get wishes"})
        return json_data_response
    else:
        user = db.session.query(User).filter_by(id=userid).first()
        json_data = json.loads(request.data)
        wish = Wish(user.id,json_data.get('url'),json_data.get('thumbnail'),json_data.get('title'),json_data.get('description'),datetime.now())
        if wish:
            db.session.add(wish)
            db.session.commit()
            json_data_response = jsonify({"error":"null","data":{'userid':userid,'url':json_data.get('url'),'thumbnail':wish.thumbnail,'title':json_data.get('title'),'description':json_data.get('description')},"message":"Success"})
        else:
            json_data_response = jsonify({"error":"1", "data":{},'message':'did not create wish'})
        return json_data_response


@app.route('/api/thumbnail/process', methods=['GET'])
def get_images():
    url = request.args.get('url')
    soup = BeautifulSoup.BeautifulSoup(requests.get(url).text)
    images = BeautifulSoup.BeautifulSoup(requests.get(url).text).findAll("img")
    list_of_url = []
    og_image = (soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'og:image'}))
    if og_image and og_image['content']:
        list_of_url.append(urlparse.urljoin(url, og_image['content']))
    thumbnail_spec = soup.find('link', rel='image_src')
    if thumbnail_spec and thumbnail_spec['href']:
        list_of_url.append(urlparse.urljoin(url, thumbnail_spec['href']))
    for image in images:
        if "sprite" not in image["src"]:
            list_of_url.append(urlparse.urljoin(url, image["src"]))
    if(len(list_of_url)>0):
        json_data_response = jsonify({'error':'null', "data":{"thumbnails":list_of_url},"message":"Success"})
    else:
        json_data_response = jsonify({'error':'1','data':{},'message':'Unable to extract thumbnails'})
    return json_data_response
    
#Email Script for wishlist
@app.route('/api/send/<userid>',methods=['POST'])
def send(userid):
    user = db.session.query(User).filter_by(id=userid).first()
    data = json.loads(request.data)
    fromaddr = str(user.email)
    sender = str(user.first_name) + " " + str(user.last_name)
    emails = data.get('emails')
    message = data.get('message')
    subject = data.get('subject')
    wishes = data.get('wishes')
    wishlist = []
    for wish in wishes:
        wishlist.append(str(wish))
    allWishes = ", ".join(str(wish) for wish in wishlist)
    msg = MIMEMultipart()
    emaillist = []
    for email in emails:
        emaillist.append(str(email))
    msg['From'] = fromaddr
    msg['To'] = ", ".join(emaillist)
    msg['Subject'] = subject
    intro="Hey!"  + sender  + "Has Sent Their WishList , Make their dreams come through Today" + "\n"
    link = "This link leads to the application. link: https://desolate-headland-66198.herokuapp.com//#/users" + "\n"

    msg.attach(MIMEText(intro,'plain'))
    msg.attach(MIMEText(message,'plain'))
    msg.attach(MIMEText('Their Wishlist: '+ allWishes,'plain'))
    msg.attach(MIMEText(link,'plain'))
    messageToSend = msg.as_string()
    username = 'wjc.wishlist@gmail.com'
    password = 'ncsw zedf illm zcmt'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(sender,emaillist,messageToSend)
    server.quit()
    data_response = jsonify({"error":"null","data":{"emails":emaillist,"subject":subject,"message":message,"wishes":allWishes},"message":"Success"})
    return data_response
            
#Used for time added on items
def timeinfo(entry):
    day = time.strftime("%a")
    date = time.strftime("%d")
    if (date <10):
        date = date.lstrip('0')
    month = time.strftime("%b")
    year = time.strftime("%Y")
    return day + ", " + date + " " + month + " " + year

@app.after_request
def after_request(json_data_response):
    json_data_response.headers.add('Access-Control-Allow-Origin', '*')
    json_data_response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    json_data_response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return json_data_response
  
#Runs application
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8888")