
**Catalog App:
This python App displays a set of categories , each category contains number of items. The app provides authprization and authentication functionalities. Logged in users can add new 
categories. Users who created a category can add, edit or delete Items to it, so as delete or edit their own categories.

##How to Run The Code:

**Python2.7 or 3 and VM virtualBox** should be installed on your computer. First open the app folder, then navigate to the vagrant directory it contains the Vagrant file, open up the 
gitbash in that folder. Run the command vagrant up and vagrant ssh to fire up the virtual machine. Then cd to the shared directory /vagrant. Cd to the catalog directory which contains 
the python and html files. Run the python file models.py using the command **python models.py** that will create a database file called neighborhoodmarketplace. Optionally run
 **python populatedatabase.py** to fill the database with some data. Finally run the command **python application.py** that will create a local host on port no. 8000. open up your 
favourite web browser and navigate to   http://localhost:8000/catalog to open up the homepage. Use the buttons and links provided to explore each category and each item in a cateogry. 
Use the login button to log in and create a new user using your gmail account. Then create a new category, fill with items, edit or delete the items you added. Also you can navigate to: 
http://localhost:8000/catalog/Json to see all the categories and their id's in JSON format. And http://localhost:8000/catalog/category_id/items/JSON to see all the items in a specific 
category in JSON Format. 





