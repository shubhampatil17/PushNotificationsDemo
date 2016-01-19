from flask import Flask, render_template, request, jsonify
from flask.ext.mongoengine import MongoEngine
import requests
import urllib3
import json
from gcm import GCM

app=Flask(__name__,template_folder="common",static_folder="common",static_url_path="")

app.config["MONGODB_SETTINGS"]={'DB' : "ViralMint"}
app.config["SECRET_KEY"] = "K33pTh1sS3cr3t"
db = MongoEngine(app)


class Subscriptions(db.Document):
        endpoint = db.StringField(max_length = 1000, required = True)
        relevant_objects = db.StringField(required = True)

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
                print "Registration ID: ", registrationId
		endpoint = 'https://android.googleapis.com/gcm/send'
                
    	if registrationId not in regIdList:
        	regIdList.append(registrationId)

        retrieve_regid = Subscriptions.objects(endpoint = registrationId)

        if(len(retrieve_regid) == 0):
                sub = Subscriptions()
                sub.endpoint = registrationId
                sub.relevant_objects = '1000001'
                sub.save()

        else:
                print "ID already exists"
                
        return jsonify({"Response":"abc"})

#Function used to delete entry from database on unsubscription
@app.route('/unsubscribe', methods = ['POST'])
def UnsubscribeFromServer():
        data = request.json
        print "Data for unsubscription: ", data
        endpoint = data['Endpoint']

        endpointParts = endpoint.split('/')
        registrationId = endpointParts[-1]
        print "Registration ID to delete is :", registrationId
        sub = Subscriptions.objects(endpoint = registrationId)
        sub.delete()

        return jsonify({"Response" : "abc"})


@app.route('/sendgcm',methods=['POST'])
def processGCMRequest():
    
    apiKey="AIzaSyBsyNVM0bH--tz4GvUmy7xagjTgfwwZKGg"
    
    gcm = GCM(apiKey)
    data ={"Message":"this is a notification"}
    
    response = gcm.json_request(registration_ids=regIdList,data=data)
        
    return jsonify({"Response":"abc"})


if __name__=="__main__":
	app.run(debug = True)
    
    
