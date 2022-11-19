from flask import Flask, render_template, request, redirect, session
import re
import dateutil.parser
 
app = Flask(__name__)

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
   return render_template('signup.html', msg = msg)
  
@app.route("/signin")
def signin():
   return render_template("login.html")
 
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
 
   print(date + " " + expensename + " " + amount + " " + paymode + " " + category)
  
   return redirect("/display")
 
@app.route("/display")
def display():
   return render_template('display.html' ,expense = list1)
                        
@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete(id): 
    return redirect("/display")
 
@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
   return render_template('edit.html', expenses = row)
 
@app.route('/update/<id>', methods = ['POST'])
def update(id):
     return redirect("/display")
 
@app.route("/limitn")
def limitn():
   query = "SELECT limitamt FROM limits WHERE email = '{}' ORDER BY id DESC LIMIT 1".format(session['id'])
   out = ibm_db.exec_immediate(conn,query)
   x = ibm_db.fetch_tuple(out)
   s = x
  
   return render_template("limit.html" , y= s)
 
          
if __name__ == "__main__":
   app.run(debug=True)