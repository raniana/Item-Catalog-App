from flask import Flask, render_template, url_for, request, redirect
from flask import flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item
from flask import session as login_session
import random
import string

# IMPORTS FOR applying oauth2 functionality
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

# connect to the database and create database session
engine = create_engine('sqlite:///neighborhoodmarketplace.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# Oauth2 functionalities code obtained from Udacity.com
#course authorization and authentication


@app.route('/gconnect', methods=['POST', 'GET'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is'
                                 'already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    # login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if a user exists, if not make a new one

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for'
                                 'given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalog/JSON')
def showCategoriesJSON():
    # return"this page to show JSON representation of all cats"
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/catalog/<int:catID>/items/JSON')
def showItemsJSON(catID):
    category = session.query(Category).filter_by(id=catID).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/')
@app.route('/catalog', methods=['GET'])
def showCategories():
    # return "this page to show all the categories"
    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(Item.id.desc()).limit(5)
    if 'username' not in login_session:
        return render_template('categorieswithLatestItemsPublic.html',
                               categories=categories, items=latestItems)
    else:
        return render_template('categoriesWithlatestItems.html',
                               categories=categories, items=latestItems)


@app.route('/catalog/add', methods=['GET', 'POST'])
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        flash("New Category '%s' successfully created" % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('addCategory.html')


@app.route('/catalog/<int:catID>/edit', methods=['GET', 'POST'])
def editCategory(catID):
    if 'username' not in login_session:
        return redirect('/login')
    editedCategory = session.query(Category).filter_by(id=catID).one()
    oldName = editedCategory.name
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        flash("Category '%s' has been changed to '%s'"
              % (oldName, editedCategory.name))
        session.commit()
        return redirect(url_for('showItems', catID=editedCategory.id))
    else:
        return render_template('editCategory.html', category=editedCategory)


@app.route('/catalog/<int:catID>/delete', methods=['GET', 'POST'])
def deleteCategory(catID):
    if 'username' not in login_session:
        return redirect('/login')
    categoryTodelete = session.query(Category).filter_by(id=catID).one()
    itemsTodelete = session.query(Item).filter_by(category_id=catID).all()
    if request.method == 'POST':
        for i in itemsTodelete:
            session.delete(i)
        session.delete(categoryTodelete)
        flash("Category '%s' has been deleted and all its content"
              % categoryTodelete.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html',
                               category=categoryTodelete)


@app.route('/catalog/<int:catID>/items', methods=['GET'])
def showItems(catID):
    # return "this page is to show the items within a category"
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=catID).one()
    creator = getUserInfo(category.user_id)
    items = session.query(Item).filter_by(category_id=catID).all()
    if ('username' not in login_session or
       login_session['user_id'] != creator.id):
        return render_template('showItemsPublic.html', category=category,
                               items=items, categories=categories)
    else:
        return render_template('showItems.html', category=category,
                               items=items, categories=categories)


@app.route('/catalog/items/<int:itemID>', methods=['GET'])
def showItem(itemID):
    # this page is to show a specific item description within a category
    item = session.query(Item).filter_by(id=itemID).one()
    creator = getUserInfo(item.user_id)
    if ('username' not in login_session or
       login_session['user_id'] != creator.id):
        return render_template('showItemPublic.html', item=item)
    else:
        return render_template('showItem.html', item=item)


@app.route('/catalog/<int:catID>/items/add', methods=['GET', 'POST'])
def addItem(catID):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            newItem = Item(name=request.form['name'], category_id=catID,
                           user_id=login_session['user_id'])
        if request.form['description']:
            newItem.description = request.form['description']
        if request.form['price']:
            newItem.price = request.form['price']
        if request.form['brand']:
            newItem.brand = request.form['brand']
        session.add(newItem)
        flash("New Item '%s' successfully added" % newItem.name)
        session.commit()
        return redirect(url_for('showItems', catID=catID))
    else:
        return render_template('addItem.html', catID=catID)


@app.route('/catalog/items/<int:itemID>/edit', methods=['GET', 'POST'])
def editItem(itemID):
    if 'username' not in login_session:
        return redirect('/login')
    # This page to edit an item within a category
    editedItem = session.query(Item).filter_by(id=itemID).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['brand']:
            editedItem.brand = request.form['brand']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        flash("Item has been edited")
        session.commit()
        return redirect(url_for('showItem', itemID=editedItem.id))

    else:
        return render_template('editItem.html', item=editedItem)


@app.route('/catalog/items/<int:itemID>/delete', methods=['GET', 'POST'])
def deleteItem(itemID):
    if 'username' not in login_session:
        return redirect('/login')
    # this page is to delete an item within a category
    itemTodelete = session.query(Item).filter_by(id=itemID).one()
    catID = itemTodelete.category_id
    if request.method == 'POST':
        session.delete(itemTodelete)
        flash("Item '%s' has been deleted" % itemTodelete.name)
        session.commit()
        return redirect(url_for('showItems', catID=catID))
    else:
        return render_template('deleteItem.html', item=itemTodelete)


if __name__ == '__main__':

    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
