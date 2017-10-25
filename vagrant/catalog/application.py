from flask import Flask, render_template, url_for, request, redirect,flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base,User, Category, Item

app= Flask(__name__)

#connect to the database and create database session
engine = create_engine('sqlite:///neighborhoodmarketplace.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session=DBSession()



@app.route('/catalog/JSON')
def showCategoriesJSON():
    return"this page to show JSON representation of all cats"

@app.route('/')
@app.route('/catalog', methods=['GET'])
def showCategories():
    #return "this page to show all the categories"
    categories=session.query(Category).all()
    latestItems=session.query(Item).order_by(Item.id.desc()).limit(5)
    return render_template('categoriesWithlatestItems.html',categories=categories, items=latestItems)

@app.route('/catalog/add', methods=['GET','POST'])
def addCategory():
    if request.method=='POST':
        newCategory=Category(name=request.form['name'])
        session.add(newCategory)
        flash("New Category '%s' successfully created" %newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('addCategory.html')

@app.route('/catalog/<int:catID>/edit', methods=['GET','POST'])
def editCategory(catID):
    editedCategory=session.query(Category).filter_by(id=catID).one()
    oldName=editedCategory.name
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name=request.form['name']
        session.add(editedCategory)
        flash("Category '%s' has been changed to '%s'" %(oldName, editedCategory.name))
        session.commit()
        return redirect(url_for('showItems',catID=editedCategory.id))
    else:
        return render_template('editCategory.html', category=editedCategory)


@app.route('/catalog/<int:catID>/delete', methods=['GET','POST'])
def deleteCategory(catID):
    categoryTodelete=session.query(Category).filter_by(id=catID).one()
    itemsTodelete=session.query(Item).filter_by(category_id=catID).all()
    if request.method == 'POST':
        for i in itemsTodelete:
            session.delete(i)
        session.delete(categoryTodelete)
        flash("Category '%s' has been deleted and all its content" %categoryTodelete.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html',category=categoryTodelete)
    
        
@app.route('/catalog/<int:catID>/items', methods=['GET'])
def showItems(catID):
    #return "this page is to show the items within a category"
    categories= session.query(Category).all()
    category = session.query(Category).filter_by(id=catID).one()
    items = session.query(Item).filter_by(category_id=catID).all()
    return render_template('showItems.html',category=category,items=items,categories=categories)

@app.route('/catalog/items/<int:itemID>', methods=['GET'])
def showItem(itemID):
    #return "this page is to show a specific item description within a category"
    item = session.query(Item).filter_by(id=itemID).one()
    return render_template('showItem.html', item=item)

@app.route('/catalog/<int:catID>/items/add', methods=['GET','POST'])
def addItem(catID):
    if request.method == 'POST':
        if request.form['name']:
            newItem=Item(name=request.form['name'],category_id=catID)
        if request.form['description']:
            newItem.description=request.form['description']
        if request.form['price']:
            newItem.price=request.form['price']
        if request.form['brand']:
            newItem.brand=request.form['brand']    
        session.add(newItem)
        flash("New Item '%s' successfully added" %newItem.name)
        session.commit()
        
        return redirect(url_for('showItems',catID=catID))
    else:
        return render_template('addItem.html',catID=catID)

@app.route('/catalog/items/<int:itemID>/edit', methods=['GET','POST'])
def editItem(itemID):
    #return "This page to edit an item within a category"
    editedItem=session.query(Item).filter_by(id=itemID).one()
    if request.method=='POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['brand']:
            editedItem.brand=request.form['brand']
        if request.form['price']:
            editedItem.price=request.form['price']
        session.add(editedItem)
        flash("Item has been edited" )
        session.commit()
        return redirect(url_for('showItem',itemID=editedItem.id))

    else:
         return render_template('editItem.html',item=editedItem)
    

@app.route('/catalog/items/<int:itemID>/delete', methods=['GET','POST'])
def deleteItem(itemID):
    #return "this page is to delete an item within a category"
    itemTodelete=session.query(Item).filter_by(id=itemID).one()
    catID=itemTodelete.category_id
    if request.method == 'POST':
        session.delete(itemTodelete)
        flash("Item '%s' has been deleted" %itemTodelete.name)
        session.commit()
        return redirect(url_for('showItems',catID=catID))
    else:
        return render_template('deleteItem.html',item=itemTodelete)
    



if __name__ == '__main__':

    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)


