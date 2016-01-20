from flask import Flask, render_template, request, jsonify

import requests
import urllib3
import json
from gcm import GCM

app=Flask(__name__,template_folder="common",static_folder="common",static_url_path="")

regIdList=[]

@app.route('/')
def initialiseTemplate():
	return render_template('frontend.html')
    
@app.route('/sendendpoint', methods=['POST'])
def processSubscriptionRequest():
	data = request.json
	endpoint = data['Endpoint']
	#subscriptionId= data['SubscriptionId']
    
	print endpoint
	#print subscriptionId
    
	if endpoint.startswith('https://android.googleapis.com/gcm/send'):

		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
		endpoint = 'https://android.googleapis.com/gcm/send'
                
    	if registrationId not in regIdList:
        	regIdList.append(registrationId)
        
	return jsonify({"Response":"abc"})


@app.route('/sendgcm',methods=['GET','POST'])
def processGCMRequest():
    
    apiKey="AIzaSyBsyNVM0bH--tz4GvUmy7xagjTgfwwZKGg"
    
    gcm = GCM(apiKey)
    data ={"title":"New Notification","body":"Message Body "}
    
    response = gcm.json_request(registration_ids=regIdList,data=data)
        
    return jsonify({"Response":"abc"})


@app.route('/sendrequest',methods=['GET'])
def processNotificationRequest():

	data = request.json

	return jsonify({

			"title":"This is title",
			"body":"This is body",
			"icon":"notifications.png",
			"tag":"simple-push-demo-notification-tag",
			"url":"https://www.google.com"		
		})



if __name__=="__main__":
	app.run(debug = True)
    
    
