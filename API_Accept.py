# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 14:54:26 2019

@author: INFO-DSK-04
"""

#pip install flask 
#import main Flask class and request object 
from flask import Flask, request, render_template, session, redirect #send_file, Response, jsonify, render_template 
import pandas as pd
from werkzeug.exceptions import HTTPException,BadRequest
import alertgenerator




app = Flask(__name__) #create the Flask app


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return 'Bad Request!', 400
# or, without the decorator
#app.register_error_handler(400, handle_bad_request)


@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    #return render_template("500_generic.html", e=e), 500
    return 'Oops! Internal Error Occurred.', 500

from datetime import datetime
@app.route('/accept_data/', methods=['POST']) #allow POST requests 
def alertstatus():
    print(datetime.now())
    #data =[]
    #global data
    #requirement id and search folder name should be provided in the request 
    #print(request.json)
    #dicti = json.dumps(request.json)
    #dicti = json.loads(dicti)
    dicti = request.json.get('data')
# =============================================================================
#     if len(data)<3:
#         data.append(data1)
#     else:
#         del data[0]
#         data.append(data1)
# =============================================================================
 
    alertdata = alertgenerator.startprocess(dicti)
    #time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    alertdata.to_csv(r"C:\Users\INFO-DSK-04\Desktop\Asset_Data\Alerts Data\Alerts_Generated.csv",index=False) 
    print(alertdata)
    
    #print(alertdata)
    #data =[]
    return 'OK', 200 


@app.route('/show_alerts/', methods=("POST", "GET"))
def show_alerts_table():
    #dicti = request.json.get('data')
    #alertdata = alertgenerator.startprocess(dicti)
    alertdata = pd.read_csv(r"C:\Users\INFO-DSK-04\Desktop\Asset_Data\Alerts Data\Alerts_Generated.csv")
    alrt = alertgenerator.sendalerts(alertdata)

    #return alertdata.to_html(header="true", table_id="table")
    #return render_template('simple.html',  tables=[alertdata.to_html(classes='data')], titles=alertdata.columns.values)
    return alrt, 200



@app.errorhandler(404)
def not_found(error):
    #return render_template('error.html'), 404
    return 'Page Not Found!', 404

@app.route('/', methods=['GET'])
def home():
    return '''<h1>This is Asset Connect Driver Behavior API</h1>
<br>
<p>A prototype API for pushing and pulling data for Driver Behavior.</p>'''



if __name__ == '__main__':
    app.run(debug=True, port=5000) #run app in debug mode on port 5000