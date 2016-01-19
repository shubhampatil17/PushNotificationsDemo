from flask import Flask, render_template, request, jsonify
from flask.ext.mongoengine import MongoEngine
import requests
import urllib3
import json
from gcm import GCM

app=Flask(__name__,template_folder="common",static_folder="common",static_url_path="")
db = MongoEngine(app)

regIdList=[]

@app.route('/')
def initialiseTemplate():
	#return app.send_static_file('frontend.html')
    	return render_template('frontend.html')
    
@app.route('/sendendpoint', methods=['POST'])
def processSubscriptionRequest():
	data = request.json
        print "Data : ", data
	endpoint = data['Endpoint']
    
	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
        	endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
		endpoint = 'https://android.googleapis.com/gcm/send'
                
    	if registrationId not in regIdList:
        	regIdList.append(registrationId)
        
	return jsonify({"Response":"abc"})


@app.route('/sendgcm',methods=['POST'])
def processGCMRequest():
    
    apiKey="AIzaSyBsyNVM0bH--tz4GvUmy7xagjTgfwwZKGg"
    
    gcm = GCM(apiKey)
    data ={"Message":"this is a notification"}
    
    response = gcm.json_request(registration_ids=regIdList,data=data)
    
    print response
    
    return jsonify({"Response":"abc"})


if __name__=="__main__":
	app.run(debug = True)
    
    
