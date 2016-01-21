from flask import Flask, render_template, request, jsonify
import requests
from flask.ext.mongoengine import MongoEngine
import requests
import urllib3
import json
from gcm import GCM

#Global variables
notification_title = ''
notification_text = ''

app=Flask(__name__,template_folder="common",static_folder="common",static_url_path="")

app.config["MONGODB_SETTINGS"]={'DB' : "ViralMint"}
app.config["SECRET_KEY"] = "K33pTh1sS3cr3t"
db = MongoEngine(app)


class Subscriptions(db.Document):
        endpoint = db.StringField(max_length = 1000, required = True)
        relevant_objects = db.ListField(required = True)

complete_updates = ['shoes', 'shirts','tees', 'trousers', 'jeans', 'traditionals']


@app.route('/')
def initialiseTemplate():
	return render_template('frontend.html')
    
@app.route('/sendendpoint', methods=['POST'])
def processSubscriptionRequest():
	data = request.json
	print "Data : ", data
	endpoint = data['Endpoint']
        relevant_objects = data['Objects']
	#subscriptionId= data['SubscriptionId']
    
	print endpoint
	#print subscriptionId
	if endpoint.startswith('https://android.googleapis.com/gcm/send'):

		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
		print "Registration ID: ", registrationId
		endpoint = 'https://android.googleapis.com/gcm/send'
                
        retrieve_regid = Subscriptions.objects(endpoint = registrationId)

        if(len(retrieve_regid) == 0):
                sub = Subscriptions()
                sub.endpoint = registrationId
                if(len(relevant_objects) == 0):
                        sub.relevant_objects = []
                else:
                        sub.relevant_objects = relevant_objects
                sub.save()

        else:
                print "ID already exists, Update requested data"
                return render_template(update_requests.html, relevant_objects = retrieve_regid.relevant_objects)

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


@app.route('/sendgcm',methods=['GET','POST'])
def processGCMRequest():
    
    apiKey="AIzaSyBsyNVM0bH--tz4GvUmy7xagjTgfwwZKGg"
    
    gcm = GCM(apiKey)
    
    data = request.json

    global notification_title
    notification_title = data['notification_title']
    global notification_text
    notification_text = data['notification_text']
    tags = data['tags']

    print "Title: ", notification_title

    all_entries = Subscriptions.objects.all()
    regIdList = []
    for x in all_entries:
           # print "Testing", x.endpoint, x.relevant_objects
            if(set(tags).issubset(set(x.relevant_objects))):
                    regIdList.append(x.endpoint)

    #regIdList = [x.endpoint for x in all_entries if len(list((set(tags) - set(x.relevant_objects))) != 0 ]
    print regIdList
    response = gcm.json_request(registration_ids=regIdList,data=data)
   # processNotificationRequest(notification_title, notification_text)    
    return jsonify({"notification_title" : notification_title, "notification_text" : notification_text})


@app.route('/sendrequest', methods=['GET', 'POST'])
def processNotificationRequest():

        return jsonify({

			"title": notification_title,
			"body": notification_text,
			"icon":"notifications.png",
			"tag":"simple-push-demo-notification-tag",
			"url":"https://www.google.com"		
		})

if __name__=="__main__":
	app.run(debug = True)
    
    
