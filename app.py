from flask import Flask, render_template, request, session, redirect
import mysql.connector
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import gunicorn 

#Initialize variable
app = Flask(__name__)
app=Flask(__name__,template_folder='templates')
app.secret_key = "Chloe" #Need a secret_key value for function sessions to work 

my_db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database= "jaredDatabase"
)

mycursor= my_db.cursor() #Create a cursor to implement functions
mycursor = my_db.cursor(buffered =True)
mycursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255), role VARCHAR(255), roomName VARCHAR (255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS requests (id INT AUTO_INCREMENT PRIMARY KEY, equipmentID INT, username VARCHAR(255), status VARCHAR (255), quantity VARCHAR (255), roomName VARCHAR (255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS roomName (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS categoryName (id INT AUTO_INCREMENT PRIMARY KEY, category VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS role (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS propertyName (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS dataAnalysis (id INT AUTO_INCREMENT PRIMARY KEY, teacherUsername VARCHAR(255), equipmentName VARCHAR(255), quantity VARCHAR(255), category VARCHAR(255), propertyType VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS equipment (id INT AUTO_INCREMENT PRIMARY KEY, id INT, name VARCHAR (255), availableQuantity INT, totalQuantity INT, location VARCHAR(255), category VARCHAR (255), property VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS labEquipment (id INT AUTO_INCREMENT PRIMARY KEY, id INT, name VARCHAR (255), quantity INT, location VARCHAR(255), category VARCHAR(255))")

#mycursor.execute("CREATE TABLE IF NOT EXISTS equipment (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), quantity VARCHAR(255), location VARCHAR(255), category VARCHAR(255), property VARCHAR(255))")
#mycursor.execute creates a table for items in a database. 

# "/" just means main homepage; every application has this opener 
#Variable name must be consistent with the route
@app.route("/") 
def home():
    if "username" in session: #For quick login for returning users on same device; session is locally stored data)
        if session["role"] == "teacher": #checks if the local role is a teacher, and if so, the program returns the teacher html file
            return render_template("homeTeacher.html", user = session["username"])
        else:
            #if the role is not a teacher, or an admin, the program returns the regular home html file for admins
            return render_template("home.html", user= session['username'])
    #the name of home does not matter, but for convention, it means the homepage.
    else:
        return render_template("login.html")

@app.route("/userRole") 
def userRole():
    return render_template("userRole.html")       

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

@app.route("/addFunction")
def addFunction():
    return render_template("addFunction.html")

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
        name = request.form.get("equipmentName")
        availableQuantity = request.form.get("equipmentQuantity")
        totalQuantity = request.form.get("equipmentTotalQuantity")
        location = request.form.get("equipmentLocation")
        category = request.form.get("equipmentCategory")
        property = request.form.get("equipmentProperty")
    
        sql = "INSERT INTO equipment (name, availableQuantity, totalQuantity, location, category, property) VALUES (%s, %s, %s, %s, %s, %s)"
        #have a checker to make sure that VALUES does not have same name
        values = [name, availableQuantity, totalQuantity, location, category, property]
        #Saving in the database 
        mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
        return redirect("/")
    else:
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

        return render_template("addEquipment.html", categoryList = categoryList, roomList = roomList, propertyList = propertyList)

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

@app.route("/deleteCategory/<int:id>", methods = ["POST", "GET"])
def deleteCategory(id): #pass ID as a parameter
    if request.method == "POST": #Post is a function that responds to a submission    
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
        print(result)
        return render_template("deleteCategory.html" ,itemCategory=result)      

@app.route("/deleteEquipment/<int:id>", methods = ["POST", "GET"])
def deleteEquipment(id): #pass ID as a parameter
    if request.method == "POST": #Post is a function that responds to a submission    
        sql = "DELETE from equipment WHERE id=%s"
        values = [id]
        #Saving in the database 
        mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
        return redirect("/")
    else:
        sql = "SELECT id, name FROM equipment WHERE id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        print(result)
        return render_template("deleteEquipment.html" ,item=result)   

@app.route("/deleteRoom/<int:id>", methods = ["POST", "GET"])
def deleteRoom(id): #pass ID as a parameter
    if request.method == "POST": #Post is a function that responds to a submission    
        sql = "DELETE from roomName WHERE id=%s"
        values = [id]
        #Saving in the database 
        mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
        return redirect("/")
    else:
        sql = "SELECT id, name FROM roomName "
        mycursor.execute(sql)

        result= mycursor.fetchall()
        return render_template("deleteRoom.html", roomItem = result)      

@app.route("/deleteProperty/<int:id>", methods = ["POST", "GET"])
def deleteProperty(id): #pass ID as a parameter
    if request.method == "POST": #Post is a function that responds to a submission    
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
        print(result)
        return render_template("deleteProperty.html" ,item=result) 

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

@app.route("/editCategory/<int:id>", methods = ["POST", "GET"])
def editCategory(id):
    if request.method == "POST": #Post is a function that responds to a submission
        name = request.form.get("categoryName")
        sql = "UPDATE equipment SET name=%s, WHERE id=%s"
        values = [name, quantity, location, category, property, id]
        #Saving in the database 
        mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
        return redirect("/")
    else:
        sql = "SELECT id, name, quantity, location, category, property FROM categoryName WHERE id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        print(result)
        
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

        return render_template("editCategory.html" ,item=result, categoryList = categoryList, roomList = roomList, propertyList = propertyList)     

@app.route("/editEquipment/<int:id>", methods = ["POST", "GET"])
def editEquipment(id):
    if request.method == "POST": #Post is a function that responds to a submission
        name = request.form.get("equipmentName")
        availableQuantity = request.form.get("equipmentQuantity")
        originalTotalQuantity = request.form.get("originalEquipmentTotalQuantity")
        totalQuantity= request.form.get("equipmentTotalQuantity")
        location = request.form.get("equipmentLocation")
        category = request.form.get("equipmentCategory")
        equipmentProperty = request.form.get("equipmentProperty")

        originalTotalQuantity = float(originalTotalQuantity)
        totalQuantity = float(totalQuantity)
        availableQuantity = float(availableQuantity)
        updatedTotalQuantity = totalQuantity -originalTotalQuantity  
        difference = totalQuantity- originalTotalQuantity
        availableQuantity= availableQuantity + difference
        if(difference > quantity):
            return render_template("error.html", message = "Changes to total quantity makes available quantity negative ")

        sql = "UPDATE equipment SET name=%s, availableQuantity=%s, totalQuantity = %s, location=%s, category=%s, property = %s WHERE id=%s"
        values = [name, availableQuantity, totalQuantity, location, category, equipmentProperty, id]
        #Saving in the database 
        mycursor.execute(sql,values) #Execute is running a database command (a sql command) 
        my_db.commit() #save commit info. 
        return redirect("/")
    else:
        sql = "SELECT id, name, availableQuantity, totalQuantity, location, category, property FROM equipment WHERE id = %s"
        value = [id]
        mycursor.execute(sql, value) #mycursor.execute selects data based on the id value 
        result = mycursor.fetchone() #Use fetchone, because you only need to fetch "one" ID 
        
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
        return render_template("editEquipment.html" ,item=result, categoryList = categoryList, roomList = roomList, propertyList = propertyList)   

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

@app.route("/login", methods= ['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form.get("userName")
        password = request.form.get("password")

        sql = "SELECT role, roomName FROM users WHERE username=%s AND password = %s"
        values = [username, password]

        mycursor.execute(sql, values)
        result = mycursor.fetchone()

        if len(result) > 0:
            session['username'] = username
            session['roomName'] = result[1]
            session["role"] = result[0]

            return redirect("/")
        else:
            return render_template("login.html")                

    else:
        return render_template("login.html") 

@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template("login.html")     

@app.route("/search", methods = ["POST", "GET"])
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
            return render_template("myEquipment.html", list = myList) #Return back to the HTML file with a datatable of found values
        else:
            return render_template("databaseEquipment.html", list = myList)

@app.route("/searchRequest", methods=['POST', 'GET'])
def searchRequest():
    if request.method == "POST":
        name = request.form.get("searchName")

        sql = "SELECT id, name, availableQuantity, location, category, property, totalQuantity FROM equipment WHERE name=%s"
        value = [name]

        mycursor.execute(sql, value)

        result = mycursor.fetchall()
        
        mylist = []

        if len(result) >0:
            id_list = []

            for item in result:
                id_list.append(item[0])
            
            if len(result) > 0:
                sql = "SELECT id, equipmentID, username, status, quantity, roomName FROM requests WHERE equipmentID=%s"
                mycursor.execute (sql, id_list)
                requestResults = mycursor.fetchall()

            for element in requestResults:
                for equipment in result:
                    if element[1] == equipment[0]:
                        mylist.append([element[0],equipment, element[2], element[3], element[4], element[5]])

        if session['role'] == "teacher":
            return render_template("myEquipment.html", list=mylist)
        else:
            return render_template("requests.html", list=mylist,roomName = session["roomName"])

    
    

@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form.get("userName")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")
        roomName = request.form.get("roomName")
            #confirm userName has not been taken 
            #if all good, save info into data base 
        if password == confirmPassword:
            session['username'] = username
            session['roomName'] = roomName
            role = "teacher"

            sql = "INSERT INTO users (username, password, role, roomName) VALUES (%s,%s,%s,%s)"
            values = [username, password, role, roomName]

            mycursor.execute(sql, values)
            my_db.commit()

            return render_template("home.html", user = session['username'],)
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

@app.route("/databaseEquipment")
def databaseEquipment():

    sql = "SELECT id, name, availableQuantity, totalQuantity, category , location, property  FROM equipment "
    mycursor.execute(sql)

    result= mycursor.fetchall()

    if len(result)> 0 :
        list = result
    else:
        list = ""

    return render_template("databaseEquipment.html", list = list)   

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

@app.route("/database")
def database():
    return render_template("database.html")   

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
        equipmentName = request.form.get("equipmentName")
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

            sql = "INSERT INTO requests (equipmentID, username, status, quantity, roomName) VALUES (%s, %s, %s, %s,%s)" #
            values = [id, teacherUsername, status, requestedQuantity, roomName]
            mycursor.execute(sql,values) #mycursor.execute saves the information from the sql into the database requests
            my_db.commit() #save commit info. 

            #Update the available quantity 

            newQuantity = float(availableQuantity)- float(requestedQuantity) #variable new quantity is created to subtract 
            #avaialbleQuantity from requestedQuantity, because after a request, the avvailbleQuantity of stock decreases
            sql = "UPDATE equipment SET availableQuantity = %s WHERE id = %s"
            values = [newQuantity, id] 
            
            mycursor.execute(sql,values) #saves the new value of availableQuantity to newQuantity
            my_db.commit()

            #Track data for analysis 
            sql = "INSERT INTO dataAnalysis (teacherUsername, equipmentName, quantity, category, propertyType) VALUES (%s,%s,%s,%s,%s)"
            values = [teacherUsername, equipmentName, requestedQuantity, category, propertyType]
            
            mycursor.execute(sql,values)
            my_db.commit()

            return redirect("/") #returns to homepage

            
        else:
            return render_template("error.html", message = "You have overrequested an item. Please input a lower amount") 
            #if requestedQuantity is higher than availableQuantity, then error message is given 
    else: #code is called when method called is GET 
        sql = "SELECT id, name, availableQuantity, category, property FROM equipment WHERE id = %s" #gathers ID, name and availableQuantity from database table
        #equipment
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

@app.route("/approveRequest/<int:id>", methods = ["POST", "GET"])
def approveRequest(id):
    if request.method == "POST":
        status = "Request Approved"

        sql = "UPDATE requests SET status= %s WHERE id =%s"
        values = [status, id]

        mycursor.execute(sql,values)
        my_db.commit()

    return render_template("home.html")

@app.route("/approveReturn/<int:id>", methods = ["POST", "GET"])
def approveReturn(id):
    if request.method == "POST":
        equipmentId = request.form.get("equipmentId")
        availableQuantity = request.form.get("availableQuantity")
        propertyType = request.form.get("propertyType")
        
        if propertyType == "Solid":
            sql = "UPDATE equipment SET availableQuantity= availableQuantity+%s WHERE id =%s"
            values = [availableQuantity, equipmentId]

            mycursor.execute(sql,values)
            my_db.commit()

        sql = "DELETE FROM requests WHERE id =%s"
        values = [id]

        mycursor.execute(sql,values)
        my_db.commit()

    return render_template("home.html")

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
        role = "admin"

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

    if request.method == "POST":
        filter = request.form.get("dataFilter")
        x =[]
        y= []
        yAxisFilter = request.form.get("yAxisFilter")
        yAxisFilter = int(yAxisFilter)
        if filter == "teacherUsername":
            sql = "Select teacherUsername, avg(quantity), min(quantity), max(quantity), count(id) from dataAnalysis group by teacherUsername"
        if filter == "category":
            sql = "Select category, avg(quantity), min(quantity), max(quantity), count(id) from dataAnalysis group by category"
        if filter == "propertyType":
            sql = "Select propertyType, avg(quantity), min(quantity), max(quantity), count(id) from dataAnalysis group by propertyType"
        if filter == "equipmentName":
            sql = "Select equipmentName, avg(quantity), min(quantity), max(quantity), count(id) from dataAnalysis group by equipmentName"
        if filter == "quantity":
            sql = "Select quantity, avg(quantity), min(quantity), max(quantity), count(id) from dataAnalysis group by quantity"
        mycursor.execute(sql)
        result = mycursor.fetchall()

            # category vs total count
        for item in result:
            x.append(item[0])
            y.append(item[yAxisFilter])

        plt.bar(x,y)
        plt.xlabel(filter)
        plt.ylabel("Total Count")
        plt.savefig("static/images/category.png")
        plt.close()
        currentURL= "static/images/category.png"

       

        if len(result) >0:
            return render_template("dataAnalysis.html", dataAnalysisList = result, url = currentURL)
        else:
            return render_template("error.html")
    else:
        return render_template(dataAnalysis.html, dataAnalysisList = "")

if __name__ == '__main__':
    app.run()
    #Running the variable that we initialized earlier. 