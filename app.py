#Imported information 
from flask import Flask, render_template, request, session, redirect #Imports funcitons for login and add, edit and delete funcitons
import mysql.connector #Imports mySql connector to set up connections with online database
import pandas as pd #Imported information to help plot dataAnalysis 
import matplotlib.pyplot as plt #Imported information to help plot dataAnalysis 
import gunicorn #Imported information to help plot dataAnalysis 

#Initialize variable
app = Flask(__name__)
app=Flask(__name__,template_folder='templates')
app.secret_key = "Chloe" #Need a secret_key value for function sessions to work 

my_db = mysql.connector.connect(
    host ="sql6.freemysqlhosting.net",
    user = "sql6464326",
    password ="9Kmpgyh5nr",
    database= "sql6464326"
)

mycursor= my_db.cursor() #Create a cursor to implement functions
mycursor = my_db.cursor(buffered =True)
#Creates table for different database tables with different parameters
mycursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), role VARCHAR(255), roomName VARCHAR (255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS requests (id INT AUTO_INCREMENT PRIMARY KEY, equipmentID INT, username VARCHAR(255), status VARCHAR (255), quantity VARCHAR (255), roomName VARCHAR (255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS roomName (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS categoryName (id INT AUTO_INCREMENT PRIMARY KEY, category VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS role (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS propertyName (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS dataAnalysis (id INT AUTO_INCREMENT PRIMARY KEY, teacherUsername VARCHAR(255), equipmentName VARCHAR(255), quantity VARCHAR(255), category VARCHAR(255), propertyType VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS equipment (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR (255), availableQuantity INT, totalQuantity INT, location VARCHAR(255), category VARCHAR (255), property VARCHAR(255))")

#Homepage 
@app.route("/") 
def home():
    if "username" in session: #For quick login for returning users on same device; session is locally stored data)
        if session["role"] == "teacher": #checks if the local role is a teacher, and if so, the program returns the teacher html file
            return render_template("homeTeacher.html", user = session["username"])
        else:
            #if the role is not teacher, then the role is an admin, and the function returns the admin home page 
            return render_template("home.html", user= session['username'])
    #returns to the home page 
    else:
        return render_template("login.html")
    #If the user has not logged in before, then the homepage is sent to the login page where they can sign up

@app.route("/userRole") 
def userRole():
    return render_template("userRole.html")   

@app.route("/approveRequest/<int:id>", methods = ["POST", "GET"])
#Admin approves the request of the user
def approveRequest(id):
    if request.method == "POST": #If the function is called upon with a submission, then the status of the equipment is changed to request 
    #approved
        status = "Request Approved"

        sql = "UPDATE requests SET status= %s WHERE id =%s" #Sets up the function to update the status to Request Approved
        values = [status, id] #Values is the parameter that fills in the sql with variables status and id 

        mycursor.execute(sql,values)#commits the action 
        my_db.commit() #Saves the result

    return render_template("home.html") #Returns to homepage 

@app.route("/approveReturn/<int:id>", methods = ["POST", "GET"]) #Admin approves the return of the request from user
def approveReturn(id):
    if request.method == "POST": #Creates an if statement if the function is called upon with a submission
        equipmentId = request.form.get("equipmentId") #equipmentID is initialized to equipmentID passed from the user 
        availableQuantity = request.form.get("availableQuantity") #availableQuantity is intialized to availableQuantity passed from the user
        propertyType = request.form.get("propertyType") #propertyType is intialized to propertyType passed from teh user 
        
        if propertyType == "Solid": #If the propertyType is solid, then the requested item is returnable 
            sql = "UPDATE equipment SET availableQuantity= availableQuantity+%s WHERE id =%s" #sets up the function to update the 
            #availableQuantity in database equipment given the id of the user
            values = [availableQuantity, equipmentId] #values is given parameters availableQuantity and equipmentID

            mycursor.execute(sql,values) #executes the sql function given parameter values 
            my_db.commit() #Saves the values into the database 

        sql = "DELETE FROM requests WHERE id =%s" #Deletes the request since the return has been successful 
        values = [id] #Values is given parameter id 

        mycursor.execute(sql,values) #Commits the sql function
        my_db.commit()

        sql = "DELETE FROM dataAnalysis WHERE id =%s" #Deletes the request since the return has been successful 
        values = [id] #Values is given parameter id 

        mycursor.execute(sql,values) #Commits the sql function
        my_db.commit()
        #my_db.commit()#Saves the values into the database

    return render_template("home.html") #Returns to the homepage 

@app.route("/addCategory", methods = ["POST", "GET"])
def addCategory():
    if request.method == "POST": #Post is a function that responds to a submission
        category = request.form.get("categoryName")
        sql = "INSERT INTO categoryName (category) VALUES (%s)"
        values = [category]
        #Saving in the database 
        mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
        return redirect("/")
    else:
        return render_template("addCategory.html")

@app.route("/addProperty", methods = ["POST", "GET"])
def addProperty():
    if request.method == "POST":
        name = request.form.get("propertyName")
        sql = "INSERT INTO propertyName (name) VALUES (%s)"
        values = [name]
        mycursor.execute(sql,values)
        my_db.commit()
        return redirect("/")
    else:
        return render_template("addProperty.html")

@app.route("/addRole", methods = ["POST", "GET"])
def addRole():
    if request.method == "POST":
        name = request.form.get("roleName")
        sql = "INSERT INTO role (name) VALUES (%s)"
        values = [name]
        mycursor.execute(sql,values)
        my_db.commit()
        return redirect("/")
    else:
        return render_template("addRole.html")


@app.route("/addEquipment", methods = ["POST", "GET"])
def addEquipment():
    if request.method == "POST": #Post is a function that responds to a submission
        name = request.form.get("equipmentName")#Name takes the value of equipmentName submitted from earlier
        quantity = request.form.get("equipmentQuantity")#quantity takes teh value of equipmentQuantity 
        #submitted from earlier
        location = request.form.get("equipmentLocation")#location takes the value of equipmentLocation submitted from earlier
        category = request.form.get("equipmentCategory")#category takes the value of equipmentCategory submitted from earlier
        property = request.form.get("equipmentProperty")#property takes the value of equipmentProperty submitted from earlier
    
        sql = "INSERT INTO equipment (name, availableQuantity, totalQuantity, location, category, property) VALUES (%s, %s, %s, %s, %s, %s)"
        #Sql initializes a function to change the values inside database equipment given variable values 
        values = [name, quantity, quantity, location, category, property]
        #Iniitializes values given variables name, availableQuantity, totalQuantity, location, category, property
        #Saving in the database 
        mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
        return redirect("/")
    else:
        scienceCategoryType = "SELECT id, category FROM categoryName " #Initializes function to gather values id and category from 
        #categoryName 
        mycursor.execute(scienceCategoryType) #Carries out the function to select values from categoryName
        categoryResult= mycursor.fetchall() #categoryResult takes the value of the executed action

        if len(categoryResult)> 0 : #Checks if the length of the result is greater than 0; if the length is not greater than 0, then no 
        #values are in the database categoryName
            categoryList = categoryResult #categoryList is initialized to categoryResult
        else:
            categoryList = "" #categoryList is empty 

        roomName = "SELECT id, name FROM roomName " #Same functionality as scienceCategoryType 
        mycursor.execute(roomName)
        roomNameResult= mycursor.fetchall()

        if len(roomNameResult)> 0 :
            roomList = roomNameResult
        else:
            roomList = ""
        
        propertyType = "SELECT id, name FROM propertyName "#Same functionality as scienceCategoryType 
        mycursor.execute(propertyType)
        propertyResult= mycursor.fetchall()

        if len(propertyResult)> 0 :
            propertyList = propertyResult
        else:
            propertyList = ""

        return render_template("addEquipment.html", categoryList = categoryList, roomList = roomList, propertyList = propertyList)
        #Returns the html file addEquipment given the parameters categoryList, roomList and propertyList

@app.route("/addRoom", methods = ["POST", "GET"])
def addRoom():
    if request.method == "POST":
        categoryType = "SELECT id, category FROM categoryName "
        mycursor.execute(categoryType)
        result= mycursor.fetchall()
        name = request.form.get("roomName")
        sql = "INSERT INTO roomName (name) VALUES (%s)"
        values = [name]
        #Saving in the database 
        mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
        return redirect("/")
    else:
        return render_template("addRoom.html")

@app.route("/database")
def database():
    return render_template("database.html")   


@app.route("/databaseCategory")
def databaseCategory():
    sql = "SELECT id, category FROM categoryName "
    mycursor.execute(sql)

    result= mycursor.fetchall()

    if len(result)> 0 :
        list = result
    else:
        list = ""

    return render_template("databaseCategory.html", categoryList = list)  

@app.route("/databaseDataAnalysis")
def databaseDataAnalysis():
    print("databaseDataAnalysis")
    sql = "SELECT id, equipmentName FROM dataAnalysis"
    mycursor.execute(sql)

    result= mycursor.fetchall()

    if len(result)> 0 :
        list = result
    else:
        list = ""
    print("databaseDataAnalysis 2")
    return render_template("databaseDataAnalysis.html", list = list)  

@app.route("/databaseEquipment") #Function is called upon if the user clicks on database in the header
def databaseEquipment():

    sql = "SELECT id, name, availableQuantity, totalQuantity, category , location, property  FROM equipment "
    #Initializes the function to gather parameters id, name, availableQuantity etc from the database equipment 
    mycursor.execute(sql)#Executes the sql command

    result= mycursor.fetchall() #Result is intialized to the gathered information from teh sql command

    if len(result)> 0 : #Checks whether the length of the result is greater than 0. If the length is greater than 0, that means the database
    #is not empty and contains a result
        list = result
    else: #If the length of the result is not greater than 0, that means the list is empty
        list = "" #List is intialized to an empty list

    return render_template("databaseEquipment.html", list = list) #Returns html file databaseEquipment given parameter list 

@app.route("/databaseProperty")
def databaseProperty():
    sql = "SELECT id, name FROM propertyName "
    mycursor.execute(sql)

    result= mycursor.fetchall()

    if len(result)> 0 :
        list = result
    else:
        list = ""

    return render_template("databaseProperty.html", propertyList = list)   

@app.route("/databaseRoom")
def databaseRoom():

    sql = "SELECT id, name FROM roomName "
    mycursor.execute(sql)

    result= mycursor.fetchall()

    if len(result)> 0 :
        roomList = result
    else:
        roomList = ""

    return render_template("databaseRoom.html", roomList = roomList)   

@app.route("/deleteCategory/<int:id>", methods = ["POST", "GET"]) 
def deleteCategory(id): #pass ID as a parameter
    if request.method == "POST": #Post is a function that responds to a submission    
        sql = "SELECT id, equipmentID from requests WHERE equipmentID=%s"
        value = [id]
        mycursor.execute(sql, value)

        searchResults = mycursor.fetchall()
        #if statement verifies that you can only delete category if equipment is not in the data table requests
        if len(searchResults) >0:
            return render_template("error.html", message = "Cannot delete category since it is still in use")
        else:
            sql = "DELETE from categoryName WHERE id=%s"
            values = [id]
            #Saving in the database 
            mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
            my_db.commit() #save commit info. 
        return redirect("/")
    else:
        sql = "SELECT id, category FROM categoryName WHERE id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        return render_template("deleteCategory.html" ,itemCategory=result)      

@app.route("/deleteDataAnalysis/<int:id>", methods = ["POST", "GET"]) 
def deleteDataAnalysis(id): #pass ID as a parameter
    print("deleteDataAnalysis")
    if request.method == "POST": #Post is a function that responds to a submission    
        print("testing")
        sql = "DELETE from dataAnalysis WHERE id=%s"
        values = [id]
        #Saving in the database 
        mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 

        return redirect("/")
    else:
        print("deleteDataAnalysis 2")
        sql = "SELECT id, equipmentName FROM dataAnalysis where id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        return render_template("deleteDataAnalysis.html" ,item=result)      

@app.route("/deleteEquipment/<int:id>", methods = ["POST", "GET"]) #Deletes the equipment given parameter id; methods in the function are 
#"POST" and "GET"
def deleteEquipment(id): #pass ID as a parameter
    if request.method == "POST": #Post is a function that responds to a submission    
        
        sql = "SELECT id, equipmentID from requests WHERE equipmentID=%s"
        value = [id]
        mycursor.execute(sql, value)

        searchResults = mycursor.fetchall()
        #If statement verifies that you can only delete equipment if equipment is not in the data table requests
        if len(searchResults) >0:
            return render_template("error.html", message = "Cannot delete equipment because it is still in use")
        else:
            sql = "DELETE from equipment WHERE id=%s" #Initializes the sql command to delete an item from database equipment
            values = [id] #Values takes the value of id
            mycursor.execute(sql,values) #Execute runs the sql function given parameter values
            my_db.commit() #save commit info. 
            return redirect("/") #Return to homepage 
    else:
        sql = "SELECT id, name FROM equipment WHERE id = %s" #Sql initializes the function to gather id and name from database equipment
        value = [id] #Variable value takes the value of id 
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Result is initialized to the result of the sql function; mycursor uses fetchone, because you only 
        #need to fetch "one" ID 
        return render_template("deleteEquipment.html" ,item=result) #Returns the html file deleteEquipment with parameter item, which is 
        #assigned the value of result from earlier

@app.route("/deleteProperty/<int:id>", methods = ["POST", "GET"])
def deleteProperty(id): #pass ID as a parameter
    if request.method == "POST": #Post is a function that responds to a submission    
        sql = "SELECT id, equipmentID from requests WHERE equipmentID=%s"
        value = [id]
        mycursor.execute(sql, value)

        searchResults = mycursor.fetchall()
        #If statement verifies that you can only delete property if equipment is not in the data table requests
        if len(searchResults) >0:
            return render_template("error.html", message = "Cannot delete property because it is still in use")
        else:
            sql = "DELETE from propertyName WHERE id=%s"
            values = [id]
            #Saving in the database 
            mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
            my_db.commit() #save commit info. 
        return redirect("/")
    else:
        sql = "SELECT id, name FROM propertyName WHERE id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        return render_template("deleteProperty.html" ,item=result) 

@app.route("/deleteRoom/<int:id>", methods = ["POST", "GET"])
def deleteRoom(id): #pass ID as a parameter
    if request.method == "POST": #Post is a function that responds to a submission    
        sql = "SELECT id, equipmentID from requests WHERE equipmentID=%s"
        value = [id]
        mycursor.execute(sql, value)

        searchResults = mycursor.fetchall()
        #If statement verifies that you can only delete room if equipment is not in the data table requests
        if len(searchResults) >0:
            return render_template("error.html", message = "Cannot delete room because it is still in use")
        else:
            sql = "DELETE from roomName WHERE id=%s"
            values = [id]
            #Saving in the database 
            mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
            my_db.commit() #save commit info. 
        return redirect("/")
    else:
        sql = "SELECT id, name FROM roomName WHERE id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        return render_template("deleteRoom.html" ,item=result) 

@app.route("/deleteFunction")
def deleteFunction():
    scienceCategoryType = "SELECT id, category FROM categoryName "
    mycursor.execute(scienceCategoryType)
    categoryResult= mycursor.fetchall()

    if len(categoryResult)> 0 :
        categoryList = categoryResult
    else:
        categoryList = ""

    roomName = "SELECT id, name FROM roomName "
    mycursor.execute(roomName)
    roomNameResult= mycursor.fetchall()

    if len(roomNameResult)> 0 :
        roomList = roomNameResult
    else:
        roomList = ""
    propertyType = "SELECT id, name FROM propertyName "
    mycursor.execute(propertyType)
    propertyResult= mycursor.fetchall()

    if len(propertyResult)> 0 :
        propertyList = propertyResult
    else:
        propertyList = ""
    return render_template("deleteFunction.html", categoryList = categoryList, roomList = roomList, propertyList = propertyList)

@app.route("/deleteUser/<int:id>", methods = ["POST", "GET"])
def deleteUser(id): #pass ID as a parameter
    if request.method == "POST": #Post is a function that responds to a submission    
        sql = "SELECT id, equipmentID from requests WHERE equipmentID=%s"
        value = [id]
        mycursor.execute(sql, value)

        searchResults = mycursor.fetchall()
        #If statement verifies that you can only delete user if equipment is not in the data table requests
        if len(searchResults) >0:
            return render_template("error.html", message = "Cannot delete user because it is still in use")
        else:
            sql = "DELETE from users WHERE id=%s"
            values = [id]
            #Saving in the database 
            mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
            my_db.commit() #save commit info. 
        return redirect("/")
    else:
        sql = "SELECT id, username, password, role, roomName FROM users WHERE id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        return render_template("deleteUser.html" ,item=result) 

@app.route("/editCategory/<int:id>", methods = ["POST", "GET"])
def editCategory(id):
    if request.method == "POST": #Post is a function that responds to a submission
        sql = "SELECT id, equipmentID from requests WHERE equipmentID=%s"
        value = [id]
        mycursor.execute(sql, value)

        searchResults = mycursor.fetchall()
        #If statement verifies that you can only deleteEquipment if equipment is not in the data table requests
        if len(searchResults) >0:
            return render_template("error.html", message = "Cannot edit equipment because it is still in use")
        else:
            category = request.form.get("categoryName")
            sql = "UPDATE categoryName SET category=%s WHERE id=%s"
            value = [category, id]
            #Saving in the database 
            mycursor.execute(sql,value) #Execute is running a database command (a sql command) 
            my_db.commit() #save commit info. 
        return redirect("/")
    else:
        sql = "SELECT id, category FROM categoryName WHERE id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        print(result)
        
        categoryType = "SELECT id, category FROM categoryName "
        mycursor.execute(categoryType)
        categoryResult= mycursor.fetchall()

        if len(categoryResult)> 0 :
            categoryList = categoryResult
        else:
            categoryList = ""
        return render_template("editCategory.html", item = result, category = categoryList)   

@app.route("/editEquipment/<int:id>", methods = ["POST", "GET"])
def editEquipment(id):
    if request.method == "POST": #Post is a function that responds to a submission (used after the user enters submit)
        name = request.form.get("equipmentName") #initializes name to the equipmentName posted after the user enters submit 
        availableQuantity = request.form.get("equipmentQuantity") #initializes availableQuantity to the equipmentQuantity posted after the 
        #user enters submit 
        originalTotalQuantity = request.form.get("originalEquipmentTotalQuantity")#initializes name to the equipmentName posted after the 
        #user enters submit 
        totalQuantity= request.form.get("equipmentTotalQuantity")#initializes totalQuantity to the equipmentTotalQuantity posted after the 
        #user enters submit 
        location = request.form.get("equipmentLocation")#initializes location to the equipmentLocation posted after the user enters submit 
        category = request.form.get("equipmentCategory")#initializes category to the equipmentCategory posted after the user enters submit 
        equipmentProperty = request.form.get("equipmentProperty")#initializes equipmentProperty to the equipmentProperty posted after the 
        #user enters submit 

        #This code checks whether the editted totalQuantity was changed such that the availableQuantity becomes negative. 
        originalTotalQuantity = float(originalTotalQuantity) #initializes originalTotalQuantity to a float, which is a number that has 
        #decimal points
        totalQuantity = float(totalQuantity) #initializes totalQuantity to a float, which is a number that has decimal points
        availableQuantity = float(availableQuantity) #initializes availableQuantity to a float, which is a number that has decimal points
        difference = totalQuantity- originalTotalQuantity #Initializes difference to totalQuantity - originalTotalQuantity
        availableQuantityChecker= availableQuantity + difference #Initializes availableQuantityChecker to availableQuantity + difference
        if(availableQuantityChecker<0): #Checks whether the change in the totalQuantity is less than availableQuantityChecker  
            return render_template("error.html", message = "Changes to total quantity makes available quantity negative ")
            #returns the error html file where the messsage sent to users is "Changes to total quantity makes available quantity negative"
        if(totalQuantity< availableQuantity): #checks if totalQuantity is less than availableQuantity
            return render_template("error.html", message = "Total quantity cannot be less than available quantity")
            #returns the error html file where the messsage sent to users is "Changes to total quantity makes available quantity negative"
        
        sql = "UPDATE equipment SET name=%s, availableQuantity=%s, totalQuantity = %s, location=%s, category=%s, property = %s WHERE id=%s"
        #Sql initializes the operation to update the equipment database by changing the values in columns name, availableQuantity, 
        #totalQuantity etc to values
        values = [name, availableQuantity, totalQuantity, location, category, equipmentProperty, id] 
        #initializes array values to name, availableQuantity, totalQuantity etc 
        #Saving in the database 
        mycursor.execute(sql,values) #Execute runs the sql function given parameter values
        my_db.commit() #save commit info. 
        return redirect("/") #returns to homepage 
    else: #Code that is accessed when the user hits edit in the 
        sql = "SELECT id, name, availableQuantity, totalQuantity, location, category, property FROM equipment WHERE id = %s"
        #Sql initializes funciton to access the values in columns id, name, availableQuantity, totalQuantity etc 
        value = [id]
        #Initializes value to id
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        
        scienceCategoryType = "SELECT id, category FROM categoryName " #Collects the science category to help save the value into
        #categoryResult
        mycursor.execute(scienceCategoryType)
        categoryResult= mycursor.fetchall()
        #saves values of categories into variable categoryResult

        if len(categoryResult)> 0 : #checks if the length of categoryResult is greater than 0, or if there was a value stored in 
        #categoryResult
            categoryList = categoryResult #categoryList takes the value of categoryResult
        else:
            categoryList = "" #if length is 0, then categoryList is empty

        roomName = "SELECT id, name FROM roomName " #same functionality as categoryResult
        mycursor.execute(roomName)
        roomNameResult= mycursor.fetchall()

        if len(roomNameResult)> 0 :
            roomList = roomNameResult
        else:
            roomList = ""

        propertyType = "SELECT id, name FROM propertyName "#same functionality as categoryResult
        mycursor.execute(propertyType)
        propertyResult= mycursor.fetchall()

        if len(propertyResult)> 0 :
            propertyList = propertyResult
        else:
            propertyList = ""
        return render_template("editEquipment.html" ,item=result, categoryList = categoryList, roomList = roomList, propertyList = 
        propertyList)   
        #Returns an html file that sends inputs item, categoryList, roomList and propertyList in the editEquipment html file
@app.route("/editProperty/<int:id>", methods = ["POST", "GET"])
def editProperty(id):
    if request.method == "POST": #Post is a function that responds to a submission
        name = request.form.get("propertyName")
        sql = "UPDATE propertyName SET name=%s WHERE id=%s"
        value = [name, id]
        #Saving in the database 
        mycursor.execute(sql,value) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
        return redirect("/")
    else:
        sql = "SELECT id, name FROM propertyName WHERE id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        print(result)
        
        propertyType = "SELECT id, name FROM propertyName "
        mycursor.execute(propertyType)
        propertyResult= mycursor.fetchall()

        if len(propertyResult)> 0 :
            propertyList = propertyResult
        else:
            propertyList = ""
        return render_template("editProperty.html", item = result, property = propertyList)

@app.route("/editRoom/<int:id>", methods = ["POST", "GET"])
def editRoom(id):
    if request.method == "POST": #Post is a function that responds to a submission
        name = request.form.get("roomName")
        sql = "UPDATE roomName SET name=%s WHERE id=%s"
        value = [name, id]
        #Saving in the database 
        mycursor.execute(sql,value) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
        return redirect("home.html")
    else:
        sql = "SELECT id, name FROM roomName WHERE id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        print(result)
        
        roomType = "SELECT id, name FROM roomName "
        mycursor.execute(roomType)
        roomResult= mycursor.fetchall()

        if len(roomResult)> 0 :
            roomList = roomResult
        else:
            roomList = ""
        return render_template("editRoom.html", item = result, room = roomList)


@app.route("/login", methods= ['POST', 'GET']) #login function that has methods "POST" and "GET"
def login():
    if request.method == "POST": #If the user has made a submission
        username = request.form.get("userName") #username is initialized to the user's submission of username
        password = request.form.get("password") #password is initialized to the user's submission of password
        role = request.form.get("role") #role is initialized to the user's submission of role

        sql = "SELECT role, roomName FROM users WHERE username=%s AND password = %s"
        #Initailizes the sql function to select the role and roomName from database users 
        values = [username, password]
        #Values is given parameters username and password

        mycursor.execute(sql, values) #Executes the sql command
        result = mycursor.fetchone() #Result is initialized the the result of the sql command
        if result == None: #Checks whether the result is none, indicating that there isn't a user with the correct username and password
            return render_template("error.html", message = "Login details are incorrect") #Returns an error message stating that login 
            #details are incorrect

        else:
            session['username'] = username #session[username] locally stores the username of the user
            session['roomName'] = result[1]#session[roomName] locally stores the roomName of the user
            session["role"] = result[0] #session[role] locally stores the role of the user
            return redirect("/") #Returns to the homepage


    else: #If the user has not made submission
        return render_template("login.html") #Returns to the login page

@app.route("/logout") #Logs out of the website
def logout():
    session.pop("username", None) #Pops out the session[username] to ensure that the locally stored username is not saved after logging out
    return render_template("login.html") #Returns to the login page    

@app.route("/search", methods = ["POST", "GET"]) #Search function that has methods POST and GET
def search():
    if request.method == "POST": #Post is a function that responds to a submission
        searchName = request.form.get("searchName") #Initializees searchName to parameter "searchName" from the HTML file
        sql = "SELECT id, name, availableQuantity, totalQuantity, location, category, property FROM equipment WHERE name= %s" 
        #Selects for values of items from table "equipment" with a placeholder checker for type "name"
        values = [searchName] #variable "values" is assigned to variable "searchName"
        #Saving in the database 
        mycursor.execute(sql,values) #Execute finds data values in the SQL array where "values" is equal to variable "name"
        result = mycursor.fetchall()
        if len(result)> 0 : #This process checks if there was a value found in the SQL array where "values" was equal to "name"
            myList = result
        else:
            myList = "" #Initializes myList as empty if no result was found
        if session['role'] == "teacher":
            return render_template("myEquipment.html", list = myList) #Return back to HTML file myEquipment with parameter list
        else:
            return render_template("databaseEquipment.html", list = myList)#Returns to the databaseEquipment htmlfile with parameter list

@app.route("/searchRequest", methods=['POST', 'GET']) #searchRequest function that has methods POST and GET 
def searchRequest():
    if request.method == "POST": #If statement that responds to a post from the user
        name = request.form.get("searchName") #name is initialized to searchName sent by the user 

        sql = "SELECT id, name, availableQuantity, location, category, property, totalQuantity FROM equipment WHERE name=%s"
        #Initializes a sql function to select parameters id, name, availableQuantity etc from database equipment where the name matches the 
        #user's name
        value = [name] #value is given parameter name
        mycursor.execute(sql, value) #Executes the sql function
        result = mycursor.fetchall() #Result is initialized to the result of the sql function
        
        mylist = [] #mylist is empty 

        if len(result) >0: #Checks whether the length of the result is greater than 0 to ensure that there is data in the datatable equipment
            id_list = [] #id_list is empty

            for item in result: #A for loop that adds the id of each equipment into id_list
                id_list.append(item[0])
            
            if len(result) > 0: #Checks whether the length of the result is greater than 0 to ensure that there is data in the datatable 
            #equipment
                sql = "SELECT id, equipmentID, username, status, quantity, roomName FROM requests WHERE equipmentID=%s"
                #Initailzies the function to select parameters id, equipmentID, username etc from database requests given the equipmentID
                mycursor.execute (sql, id_list) #executes the sql function
                requestResults = mycursor.fetchall() #Initializes requestResults to the resul to fthe sql function

            for element in requestResults: #For loop that adds to array myList elements given the equipmentID is equal to the id of the 
            #search request.
                for equipment in result:
                    if element[1] == equipment[0]: 
                        mylist.append([element[0],equipment, element[2], element[3], element[4], element[5]])#Adds id, all quantities in 
                        #variable result (id, name, availableQuantity, location etc in line 626), username, status, quantity and roomName

        if session['role'] == "teacher": #If the user's role is a teacher, return myEquipment.html and pass parameter list, which is equal
        #to myList
            return render_template("myEquipmentRequest.html", list=mylist)
        else: #If user's role not teacher, they are admin. Return requests.html and pass parameters list and roomName.
            return render_template("requests.html", list=mylist,roomName = session["roomName"])

@app.route("/searchRequestTeacherEquipment", methods=['POST', 'GET']) #searchRequest function that has methods POST and GET 
def searchRequestTeacherEquipment():
    if request.method == "POST": #If statement that responds to a post from the user
        name = request.form.get("searchName") #name is initialized to searchName sent by the user 

        sql = "SELECT id, name, availableQuantity, location, category, property, totalQuantity FROM equipment WHERE name=%s"
        #Initializes a sql function to select parameters id, name, availableQuantity etc from database equipment where the name matches the 
        #user's name
        value = [name] #value is given parameter name
        mycursor.execute(sql, value) #Executes the sql function
        result = mycursor.fetchall() #Result is initialized to the result of the sql function
        
        mylist = [] #mylist is empty 

        if len(result) >0: #Checks whether the length of the result is greater than 0 to ensure that there is data in the datatable equipment
            id_list = [] #id_list is empty

            for item in result: #A for loop that adds the id of each equipment into id_list
                id_list.append(item[0])
            
            if len(result) > 0: #Checks whether the length of the result is greater than 0 to ensure that there is data in the datatable 
            #equipment
                sql = "SELECT id, equipmentID, username, status, quantity, roomName FROM requests WHERE equipmentID=%s"
                #Initailzies the function to select parameters id, equipmentID, username etc from database requests given the equipmentID
                mycursor.execute (sql, id_list) #executes the sql function
                requestResults = mycursor.fetchall() #Initializes requestResults to the resul to fthe sql function

            for element in requestResults: #For loop that adds to array myList elements given the equipmentID is equal to the id of the 
            #search request.
                for equipment in result:
                    if element[1] == equipment[0]: 
                        mylist.append([element[0],equipment, element[2], element[3], element[4], element[5]])#Adds id, all quantities in 
            
                        #variable result (id, name, availableQuantity, location etc in line 626), username, status, quantity and roomName
        return render_template("teacherEquipmentRequest.html", list=mylist)
       



@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form.get("userName")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")
        role = request.form.get("role")
        roomName = request.form.get("roomName")
            #confirm userName has not been taken 
            #if all good, save info into data base 
        if password == confirmPassword:
            session['username'] = username
            session['roomName'] = roomName
            session['role']= role
            sql = "INSERT INTO users (username, password, role, roomName) VALUES (%s,%s,%s,%s)"
            values = [username, password, role, roomName]
            mycursor.execute(sql, values)
            my_db.commit()
            if role == "teacher":
                return render_template("homeTeacher.html", user = session['username'])
            else: 
                return render_template("home.html", user = session['username'])
        else:
            return render_template("signup.html")                

    else:
        roomName = "SELECT id, name FROM roomName "
        mycursor.execute(roomName)
        roomNameResult= mycursor.fetchall()

        if len(roomNameResult)> 0 :
            roomList = roomNameResult
        else:
            roomList = ""
        return render_template("signup.html", roomList = roomList) 



@app.route("/updateRoom")
def updateRoom():
    return render_template("updateRoom.html") 

@app.route("/report")
def report():
    return render_template("report.html") 

@app.route("/requestEquipment/<int:id>", methods = ["POST", "GET"])
def requestEquipment(id): #pass ID as a parameter
    if request.method == "POST": #Post is a function that responds to a submission
        teacherUsername = session["username"] #assigns variable teacherUsername to the status of the account user (teacher or admin)
        equipmentName = request.form.get("equipmentName")#assigns variable equipmentName to the value of requestedQuantity in
        #database table requests
        requestedQuantity = request.form.get("requestedQuantity") #assigns variable requestedQuantity to the value of requestedQuantity in
        #database table requests
        availableQuantity = request.form.get("availableQuantity") #assigns variable availableQuantity to the value of availableQuantity in
        #database table requests
        category = request.form.get("category")#assigns variable category to the value of category in
        #database table requests
        propertyType = request.form.get("propertyType")#assigns variable propertyType to the value of propertyType in
        #database table requests
        if float(requestedQuantity) < float(availableQuantity): #checks whether the requestedQuantity is lower than availableQuantity
            #Create request record
            status= "Request Pending" #changes the status to Request Pending
            roomName = session['roomName'] #assigns the variable name roomName to the roomName given from the login credentials
            sql = "INSERT INTO requests (equipmentID, username, status, quantity, roomName) VALUES (%s, %s, %s, %s,%s)" #Sets up the sql to 
            #store the requested values above (equipmentID, teacherUsername, equipmentName, requestedQuantity etc)
            values = [id, teacherUsername, status, requestedQuantity, roomName]# Values given parameters id, teacherUsername, status etc
            mycursor.execute(sql,values) #mycursor.execute saves the information from the sql into the database requests
            my_db.commit() #Saves the information of the sql function 
            newQuantity = float(availableQuantity)- float(requestedQuantity) #variable new quantity is created to subtract 
            #avaialbleQuantity from requestedQuantity, because after a request, the availbleQuantity of stock decreases when 
            #items are requested
            sql = "UPDATE equipment SET availableQuantity = %s WHERE id = %s" #Initializes sql function to update database equipment for 
            #column availableQuantity
            values = [newQuantity, id] #Values is given parameters newQuantity, id
            mycursor.execute(sql,values) #saves the new value of availableQuantity to newQuantity
            my_db.commit()
            sql = "INSERT INTO dataAnalysis (teacherUsername, equipmentName, quantity, category, propertyType) VALUES (%s,%s,%s,%s,%s)"
            #Inserts information into database dataAnalysis whose parameters include teacherUsername, equipmentName, quantity etc
            values = [teacherUsername, equipmentName, requestedQuantity, category, propertyType]
            #Values is given parameters similar to that of database dataAnalysis
            mycursor.execute(sql,values) #Executes the sql command
            my_db.commit()
            return redirect("/") #returns to homepage
        else:
            return render_template("error.html", message = "You have over requested an item. Please input a lower amount") 
            #if requestedQuantity is higher than availableQuantity, then error message is given 
    else: #code is called when method called is GET 
        sql = "SELECT id, name, availableQuantity, category, property FROM equipment WHERE id = %s" #gathers ID, name and availableQuantity 
        #from database table equipment
        value= [id]
        mycursor.execute(sql, value) 
        result= mycursor.fetchone() #variable result takes the qualities (id, name availableQuantity)
        return render_template("checkRequest.html", item =result) #accesses the html file checkRequest with parameter item that takes 
        #value result  
        

@app.route("/myEquipment")
def myEquipment():
    
    sql = "SELECT id, equipmentID, status, quantity FROM requests WHERE username = %s" 
    #gathers id, equipmentID and status from table "requests" given the username of the equipment
    values = [session["username"]]
    mycursor.execute(sql, values) 
    result= mycursor.fetchall() #stores the sql values into the variable "result"
 
    equipmentList = [] #equipmentList is intialized as an empty array
    list = ""
    if len(result)> 0 : #checks if the result has a value or is empty
        list = result
        for item in list: #Variable "item" loops through list
            sql = "Select id, name, availableQuantity, totalQuantity, location, category, property FROM equipment WHERE id = %s"
            value = [item[1]] #variable "value" takes the value of name
            mycursor.execute(sql,value)
            result = mycursor.fetchone() #result takes the stored values of names from table "equipment"

            equipmentList.append([item[0], result, item[2], item[3]]) 

        list = equipmentList #list is assigned to the value of equipmentList 

    return render_template("myEquipment.html", list = list) #returns the html file myEquipment and passes variable list as a parameter later

@app.route("/teacherEquipment")
def teacherEquipment():

    sql = "Select id, name, availableQuantity, totalQuantity, location, category, property FROM equipment"
    mycursor.execute(sql)

    result= mycursor.fetchall()

    if len(result)> 0 :
        list = result
    else:
        list = ""
    return render_template("teacherEquipment.html", list = list) 


@app.route("/returnEquipment/<int:id>", methods = ["POST", "GET"])
def returnEquipment(id):
    if request.method == "POST": #Post is a function that responds to a submission
        status= "Return Pending" #Assigns the variable "status" to Return Pending
        sql = "UPDATE requests SET status = %s WHERE id=%s"
        values = [status, id]
        #Saving in the database 
        mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
    return redirect("/")  

@app.route("/requests")
def requests():

    sql = "SELECT id, equipmentID, username, status, quantity, roomName FROM requests" 
    #gathers id, equipmentID and status from table "requests" given the username of the equipment
    mycursor.execute(sql)

    result= mycursor.fetchall() #stores the sql values into the variable "result"

    equipmentList = [] #equipmentList is intialized as an empty array
    list = ""
    if len(result)> 0 : #checks if the result has a value or is empty
        list = result
        for item in list: #Variable "item" loops through list
            sql = "Select id, name, availableQuantity, location, category, property FROM equipment WHERE id = %s"
            value = [item[1]] #variable "value" takes the value of name
            mycursor.execute(sql,value)
            equipmentResult = mycursor.fetchone() #result takes the stored values of names from table "equipment"
            #item[0] = request ID
            #item[2] = teacherUserName
            #item[3] = status
            equipmentList.append([item[0], equipmentResult, item[2], item[3], item[4], item[5]]) 

        list = equipmentList #list is assigned to the value of equipmentList 

    return render_template("requests.html", list = list) #returns the html file myEquipment and passes variable list as a parameter later

@app.route("/makeAdmin/<int:id>", methods = ["POST", "GET"])
def makeAdmin(id):
    if request.method == "POST":
        role = "admin"

        sql = "UPDATE users SET role= %s WHERE id =%s"
        values = [role, id]

        mycursor.execute(sql,values)
        my_db.commit()

    return redirect("/manageUsers")

@app.route("/makeTeacher/<int:id>", methods = ["POST", "GET"])
def makeTeacher(id):
    if request.method == "POST":
        role = "teacher"

        sql = "UPDATE users SET role= %s WHERE id =%s"
        values = [role, id]

        mycursor.execute(sql,values)
        my_db.commit()

    return redirect("/manageUsers")

@app.route("/manageUsers")
def manageUsers():

    sql = "SELECT id, username, role, roomName FROM users" 
    #gathers id, equipmentID and status from table "requests" given the username of the equipment
    mycursor.execute(sql)

    result= mycursor.fetchall() #stores the sql values into the variable "result"

    if len(result)> 0:
        return render_template("manageusers.html", list = result)
    else:
        return render_template("signup.html")

    return render_template("requests.html", list = list) #returns the html file myEquipment and passes variable list as a parameter later

@app.route("/dataAnalysis")
def dataAnalysis():
    dataAnalysis = "SELECT teacherUsername, equipmentName, quantity, category, propertyType FROM dataAnalysis"
    mycursor.execute(dataAnalysis)
    dataAnalysisResult= mycursor.fetchall()
        
    if len(dataAnalysisResult)> 0 :
        dataAnalysisList = dataAnalysisResult
    else:
        dataAnalysisList = ""    
    return render_template("dataAnalysis.html", dataAnalysisList= "") 

@app.route("/dataSummary", methods= ["POST", "GET"])
def dataSummary():
    if request.method == "POST": #Considers whether the user has made a submission or not
        filter = request.form.get("dataFilter") #Initializes filter as the submission made by the user
        x =[] #Initializes variable x 
        y= [] #Initializes variable x 
        yAxisFilter = request.form.get("yAxisFilter") #Initializes yAxisFilter as the submission made by the user 
        yAxisFilter = int(yAxisFilter) #Changes yAxisFilter into an integer
        if filter == "teacherUsername": 
            sql = "Select teacherUsername, avg(quantity), min(quantity), max(quantity), count(id) from dataAnalysis group by teacherUsername"
        if filter == "category":
            sql = "Select category, avg(quantity), min(quantity), max(quantity), count(id) from dataAnalysis group by category"
        if filter == "propertyType":
            sql = "Select propertyType, avg(quantity), min(quantity), max(quantity), count(id) from dataAnalysis group by propertyType"
        if filter == "equipmentName":
            sql = "Select equipmentName, avg(quantity), min(quantity), max(quantity), count(id) from dataAnalysis group by equipmentName"
        mycursor.execute(sql)
        result = mycursor.fetchall() 
        for item in result: #For loop that adds item[0], which is the first element in filter. This variable depends on the above if 
        #statement. For example, if filter is equal to teacherUsername, the first element is teacherUsername etc
            x.append(item[0])
            y.append(item[yAxisFilter])
        plt.bar(x,y)
        plt.xlabel(filter)
        if yAxisFilter == 1: 
            plt.ylabel("Averages")
        #Value passed from submission was 1, which corresopnds to element 1 in the sql and the submission made from 
        #earlier; element 1 in this case is averages
        if yAxisFilter == 2: 
            plt.ylabel("Min")
        #Value passed from submission was 2, which corresopnds to element 2 in the sql and the submission made from 
        #earlier; element 1 in this case is min
        if yAxisFilter == 3: 
            plt.ylabel("Max")
        #Value passed from submission was 3, which corresopnds to element 3 in the sql and the submission made from 
        #earlier; element 1 in this case is max
        if yAxisFilter == 4: 
            plt.ylabel("Total Count")
        #Value passed from submission was 4, which corresopnds to element 4 in the sql and the submission made from 
        #earlier; element 1 in this case is total count
        plt.savefig("static/images/category.png")
        plt.close()
        currentURL= "static/images/category.png"
        if len(result) >0:
            return render_template("dataAnalysis.html", dataAnalysisList = result, url = currentURL)
        else:
            return render_template("error.html",  message = "No results found")
    else:
        return render_template(dataAnalysis.html, dataAnalysisList = "")

if __name__ == '__main__':
    app.run()
    #Running the variable that we initialized earlier. 