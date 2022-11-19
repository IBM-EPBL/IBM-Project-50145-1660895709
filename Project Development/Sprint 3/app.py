from flask import Flask, render_template, request, redirect, session
import re
import ibm_db
import dateutil.parser
from sendemail import *
 
app = Flask(__name__)
 
app.secret_key = 'your secret key'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30756;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=bkq23793;PWD=6sWRxHNJMuQyhfqs;", "", "")
 
 
@app.route("/home")
def home():
   return render_template("homepage.html")
 
@app.route("/")
def add():
   return render_template("home.html")
 
@app.route("/signup")
def signup():
   return render_template("signup.html")
 
 
@app.route('/register', methods =['GET', 'POST'])
def register():
   msg = ''
   if request.method == 'POST' :
       username = request.form['username']
       email = request.form['email']
       password = request.form['password']
      
       queryfind = "SELECT * FROM register WHERE username = '{}'".format(username)
       out = ibm_db.exec_immediate(conn,queryfind)
       account = ibm_db.fetch_assoc(out)
       print(account)
       if account:
           msg = 'Account already exists !'
       elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
           msg = 'Invalid email address !'
       elif not re.match(r'[A-Za-z0-9]+', username):
           msg = 'name must contain only characters and numbers !'
       else:
           query3 = "INSERT INTO register VALUES ('{}', '{}', '{}')".format(username,email,password)
           ibm_db.exec_immediate(conn,query3)
           msg = 'You have successfully registered !'
           return render_template('signup.html', msg = msg)
  
@app.route("/signin")
def signin():
   return render_template("login.html")
      
@app.route('/login',methods =['GET', 'POST'])
def login():
   global userid
   msg = ''
 
   if request.method == 'POST' :
       username = request.form['username']
       password = request.form['password']
       query = "SELECT * FROM register WHERE username = '{}' AND password = '{}'".format(username,password)
       out = ibm_db.exec_immediate(conn,query)
       account = ibm_db.fetch_assoc(out)
       print (account)
      
       if account:
           session['loggedin'] = True
           session['id'] = account['EMAIL']
           userid=  account['EMAIL']
           session['username'] = account['USERNAME']
         
           return redirect('/home')
       else:
           msg = 'Incorrect username / password !'
   return render_template('login.html', msg = msg)
 
@app.route("/add")
def adding():
   return render_template('add.html')
 
 
@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
  
   date = request.form['date']
   print(date)
   date = dateutil.parser.parse(date).strftime('%Y-%m-%d')
   expensename = request.form['expensename']
   amount = request.form['amount']
   paymode = request.form['paymode']
   category = request.form['category']
 
   query3 = "INSERT INTO expenses(email,date,expensename,amount,paymode,category) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(session['id'] ,date, expensename, amount, paymode, category)
   ibm_db.exec_immediate(conn,query3)
   print(date + " " + expensename + " " + amount + " " + paymode + " " + category)
  
   return redirect("/display")
 
@app.route("/display")
def display():
   print(session["username"],session['id'])
   queryfind = "SELECT * FROM expenses WHERE email = '{}' ORDER BY date DESC".format(str(session['id']))
   out = ibm_db.exec_immediate(conn,queryfind)
   account = ibm_db.fetch_tuple(out)
   list1 = []
   list2 = []
   while account!=False:
       list2.append(account[0])
       list2.append(account[1])
       list2.append(account[2])
       list2.append(account[3])
       list2.append(account[4])
       list2.append(account[5])
       list2.append(account[6])
       list1.append(list2.copy())
       list2.clear()
       account = ibm_db.fetch_tuple(out)
   print(account)
      
   return render_template('display.html' ,expense = list1)
                        
@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete(id):
    query3 = "DELETE FROM expenses WHERE id = '{}'".format(id)
    ibm_db.exec_immediate(conn,query3)
    print('deleted successfully')   
    return redirect("/display")
 
@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
   queryfind = "SELECT * FROM expenses WHERE id = '{}'".format(id)
   out = ibm_db.exec_immediate(conn,queryfind)
   row = ibm_db.fetch_tuple(out)
 
   print(row[0])
   return render_template('edit.html', expenses = row)
 
@app.route('/update/<id>', methods = ['POST'])
def update(id):
 if request.method == 'POST' :
     date = request.form['date']
     print(date)
     date = dateutil.parser.parse(date).strftime('%Y-%m-%d')
     expensename = request.form['expensename']
     amount = request.form['amount']
     paymode = request.form['paymode']
     category = request.form['category']
     query = "UPDATE expenses SET date = '{}' , expensename = '{}' , amount = '{}', paymode = '{}', category = '{}' WHERE id = '{}' ".format(date, expensename, amount, str(paymode), str(category),id)
     ibm_db.exec_immediate(conn,query)     
     print('successfully updated')
     return redirect("/display")
 
@app.route("/limit" )
def limit():
      return redirect('/limitn')
 
@app.route("/limitnum" , methods = ['POST' ])
def limitnum():
    if request.method == "POST":
        number= request.form['number']
        query = "INSERT INTO limits(email,limitamt) VALUES ('{}', '{}') ".format(session['id'], number)
        ibm_db.exec_immediate(conn,query)
        return redirect('/limitn')
   
       
@app.route("/limitn")
def limitn():
   query = "SELECT limitamt FROM limits WHERE email = '{}' ORDER BY id DESC LIMIT 1".format(session['id'])
   out = ibm_db.exec_immediate(conn,query)
   x = ibm_db.fetch_tuple(out)
   s = x
  
  
   return render_template("limit.html" , y= s)
 
@app.route("/today")
def today():
     query = "SELECT DATE(date)   , amount FROM expenses  WHERE email = '{}' AND DATE(date) = DATE(NOW()) ".format(str(session['id']))
 
     out = ibm_db.exec_immediate(conn,query)
     account = ibm_db.fetch_tuple(out)
     texpense = []
     list2 = []
     while account!=False:
       list2.append(account[0])
       list2.append(account[1])
       texpense.append(list2.copy())
       list2.clear()
       account = ibm_db.fetch_tuple(out)
    
     query2 = "SELECT * FROM expenses WHERE email = '{}' AND DATE(date) = DATE(NOW()) ORDER BY date DESC".format(str(session['id']))
     out = ibm_db.exec_immediate(conn,query2)
     account = ibm_db.fetch_tuple(out)
     expense = []
     list2 = []
     while account!=False:
       list2.append(account[0])
       list2.append(account[1])
       list2.append(account[2])
       list2.append(account[3])
       list2.append(account[4])
       list2.append(account[5])
       list2.append(account[6])
       expense.append(list2.copy())
       list2.clear()
       account = ibm_db.fetch_tuple(out)
      total=0
     t_food=0
     t_entertainment=0
     t_business=0
     t_rent=0
     t_EMI=0
     t_other=0
   
     for x in expense:
         total += x[4]
         if x[6] == "food":
             t_food += x[4]
          
         elif x[6] == "entertainment":
             t_entertainment  += x[4]
      
         elif x[6] == "business":
             t_business  += x[4]
         elif x[6] == "rent":
             t_rent  += x[4]
         
         elif x[6] == "EMI":
             t_EMI  += x[4]
       
         elif x[6] == "other":
             t_other  += x[4]
          
     print(total)
      
     print(t_food)
     print(t_entertainment)
     print(t_business)
     print(t_rent)
     print(t_EMI)
     print(t_other)
   
     return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                          t_food = t_food,t_entertainment =  t_entertainment,
                          t_business = t_business,  t_rent =  t_rent,
                          t_EMI =  t_EMI,  t_other =  t_other )
   
 
@app.route("/month")
def month():
     query = "SELECT DATE(date)   , SUM(amount) FROM expenses  WHERE email = '{}' AND MONTH(DATE(date)) = MONTH(NOW()) GROUP BY DATE(date) ORDER BY DATE(date)".format(str(session['id']))
     out = ibm_db.exec_immediate(conn,query)
     account = ibm_db.fetch_tuple(out)
     texpense = []
     list2 = []
     while account!=False:
       list2.append(account[0])
       list2.append(account[1])
       texpense.append(list2.copy())
       list2.clear()
       account = ibm_db.fetch_tuple(out)
    
     #cursor = mysql.connection.cursor()
     #cursor.execute('SELECT * FROM expenses WHERE userid = % s AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id'])))
     query2 = "SELECT * FROM expenses WHERE email = '{}' AND MONTH(DATE(date)) = MONTH(NOW()) ORDER BY date DESC".format(str(session['id']))
     #expense = cursor.fetchall()
     #print(expense)
     out = ibm_db.exec_immediate(conn,query2)
     account = ibm_db.fetch_tuple(out)
     expense = []
     list2 = []
     while account!=False:
       list2.append(account[0])
       list2.append(account[1])
       list2.append(account[2])
       list2.append(account[3])
       list2.append(account[4])
       list2.append(account[5])
       list2.append(account[6])
       expense.append(list2.copy())
       list2.clear()
       account = ibm_db.fetch_tuple(out)
      total=0
     t_food=0
     t_entertainment=0
     t_business=0
     t_rent=0
     t_EMI=0
     t_other=0
   
     for x in expense:
         total += x[4]
         if x[6] == "food":
             t_food += x[4]
          
         elif x[6] == "entertainment":
             t_entertainment  += x[4]
      
         elif x[6] == "business":
             t_business  += x[4]
         elif x[6] == "rent":
             t_rent  += x[4]
         
         elif x[6] == "EMI":
             t_EMI  += x[4]
       
         elif x[6] == "other":
             t_other  += x[4]
          
     query = "SELECT limitamt FROM limits WHERE email = '{}' ORDER BY id DESC LIMIT 1".format(session['id'])
   #x= cursor.fetchone()
     out = ibm_db.exec_immediate(conn,query)
     x = ibm_db.fetch_tuple(out)
     s = x[0]
     if(total>s):
       sendmail("You have exceeded your monthly limit! Please visit the history section to know more about your expenses.", session['id'])
     print(total)
      
     print(t_food)
     print(t_entertainment)
     print(t_business)
     print(t_rent)
     print(t_EMI)
     print(t_other)
 
 
   
     return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                          t_food = t_food,t_entertainment =  t_entertainment,
                          t_business = t_business,  t_rent =  t_rent,
                          t_EMI =  t_EMI,  t_other =  t_other )
       
@app.route("/year")
def year():
     query = "SELECT MONTH(date)   , SUM(amount) FROM expenses  WHERE email = '{}' AND YEAR(DATE(date)) = YEAR(NOW()) GROUP BY MONTH(date) ORDER BY MONTH(date)".format(str(session['id']))
     out = ibm_db.exec_immediate(conn,query)
     account = ibm_db.fetch_tuple(out)
     texpense = []
     list2 = []
     while account!=False:
       list2.append(account[0])
       list2.append(account[1])
       texpense.append(list2.copy())
       list2.clear()
       account = ibm_db.fetch_tuple(out)
    
     query2 = "SELECT * FROM expenses WHERE email = '{}' AND YEAR(DATE(date)) = YEAR(NOW()) ORDER BY date DESC".format(str(session['id']))
 
     out = ibm_db.exec_immediate(conn,query2)
     account = ibm_db.fetch_tuple(out)
     expense = []
     list2 = []
     while account!=False:
       list2.append(account[0])
       list2.append(account[1])
       list2.append(account[2])
       list2.append(account[3])
       list2.append(account[4])
       list2.append(account[5])
       list2.append(account[6])
       expense.append(list2.copy())
       list2.clear()
       account = ibm_db.fetch_tuple(out)
      total=0
     t_food=0
     t_entertainment=0
     t_business=0
     t_rent=0
     t_EMI=0
     t_other=0
   
     for x in expense:
         total += x[4]
         if x[6] == "food":
             t_food += x[4]
          
         elif x[6] == "entertainment":
             t_entertainment  += x[4]
      
         elif x[6] == "business":
             t_business  += x[4]
         elif x[6] == "rent":
             t_rent  += x[4]
         
         elif x[6] == "EMI":
             t_EMI  += x[4]
       
         elif x[6] == "other":
             t_other  += x[4]
          
     print(total)
      
     print(t_food)
     print(t_entertainment)
     print(t_business)
     print(t_rent)
     print(t_EMI)
     print(t_other)
 
     return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                          t_food = t_food,t_entertainment =  t_entertainment,
                          t_business = t_business,  t_rent =  t_rent,
                          t_EMI =  t_EMI,  t_other =  t_other )
 
@app.route('/logout')
 
def logout():
  session.pop('loggedin', None)
  session.pop('id', None)
  session.pop('username', None)
  return render_template('home.html')
 
          
if __name__ == "__main__":
   app.run(debug=True)