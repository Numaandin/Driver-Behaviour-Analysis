# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 18:53:50 2019

@author: INFO-DSK-04
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 14:54:26 2019

@author: INFO-DSK-04
"""

#pip install flask 
#import main Flask class and request object 
from flask import Flask, request #send_file, Response, jsonify, render_template 
from werkzeug.exceptions import HTTPException,BadRequest
import alertgenerator
import json 



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

@app.route('/send_data/', methods=['GET']) #allow POST requests 
def alertstatus():
    #requirement id and search folder name should be provided in the request 
    json_str = {'data_string' : request.json['data_string']}
    
    data = json.loads(json_str)
    alertdata = alertgenerator.startprocess(data)
    print(alertdata)

    return 'OK', 200 
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