from flask import Flask, render_template, request, jsonify

from flask.ext.mongoengine import MongoEngine

import json
from gcm import GCM

#Global variables
notificationTitle = ''
notificationBody = ''

app=Flask(__name__,template_folder="common",static_folder="common",static_url_path="")

app.config["MONGODB_SETTINGS"]={'db' : "ViralMint"}
#app.config["SECRET_KEY"] = "K33pTh1sS3cr3t"
db = MongoEngine(app)


class Subscriptions(db.Document):
	registrationId = db.StringField(max_length = 1000, required = True)
	subscriptionList = db.ListField()

#complete_updates = ['shoes', 'shirts','tees', 'trousers', 'jeans', 'traditionals']



@app.route('/')
def initialiseTemplate():
	return render_template('frontend.html')
    

@app.route('/getSubscriptionList',methods=['POST'])
def sendSubscriptionList():

	data = request.json	
	endpoint = data["Endpoint"]

	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]


	for subscription in Subscriptions.objects(registrationId = registrationId):
		subscriptionList = subscription.subscriptionList		

	return jsonify({"subscriptionList" : subscriptionList})


@app.route('/updateSubscription',methods=['POST'])
def updateSubscriptionList():

	data = request.json

	endpoint = data["Endpoint"]
	updatedList = data["updatedItems"]

	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]

	for subscription in Subscriptions.objects(registrationId = registrationId):
		subscription.subscriptionList = updatedList
		subscription.save()

	return jsonify({"Response":"success"})


@app.route('/subscribe', methods=['POST'])
def processSubscriptionRequest():

	data = request.json

	endpoint = data["Endpoint"]
	subscriptionList = data["subscribedItems"]
	#subscriptionId= data['SubscriptionId']
    
	#print subscriptionId
	print endpoint
	print subscriptionList

	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
		#print "Registration ID (Subscribe): ", registrationId
		endpoint = 'https://android.googleapis.com/gcm/send'

	subscription = Subscriptions()

	subscription.registrationId = registrationId
	subscription.subscriptionList = subscriptionList
	subscription.save()

	return jsonify({"Response":"success"})

'''
    retrieve_regid = Subscriptions.objects(registrationId = registrationId)

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
'''

#Function used to delete entry from database on unsubscription
@app.route('/unsubscribe', methods = ['POST'])
def unsubscribeFromServer():
	data = request.json
	#print "Data for unsubscription: ", data
	endpoint = data['Endpoint']

	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
		#print "Registration ID (delete): ", registrationId
		endpoint = 'https://android.googleapis.com/gcm/send'


	subscription = Subscriptions.objects(registrationId = registrationId)
	subscription.delete()

	return jsonify({"Response" : "success"})


@app.route('/sendgcm',methods=['POST'])
def processGCMRequest():
    
    apiKey="AIzaSyBsyNVM0bH--tz4GvUmy7xagjTgfwwZKGg"
    
    gcm = GCM(apiKey)
    
    data = request.json

    global notificationTitle
    notificationTitle = data['notificationTitle']
    global notificationBody
    notificationBody = data['notificationBody']
    tags = data['tags']

    print "Title: ", notificationTitle

    allSubscriptions = Subscriptions.objects.all()

    regIdList = []

    for subscription in allSubscriptions:
    	if( len(set(tags).intersection(set(subscription.subscriptionList)))):
    		regIdList.append(subscription.registrationId)

    print regIdList

    response = gcm.json_request(registration_ids=regIdList,data=data)
    return jsonify({"notification_title" : notificationTitle, "notification_text" : notificationBody})

'''
    for x in all_entries:
    	# print "Testing", x.endpoint, x.relevant_objects
    	if(set(tags).issubset(set(x.relevant_objects))):
    		regIdList.append(x.endpoint)
'''

    #regIdList = [x.endpoint for x in all_entries if len(list((set(tags) - set(x.relevant_objects))) != 0 ]
	# processNotificationRequest(notification_title, notification_text)    


@app.route('/sendrequest', methods=['GET','POST'])
def processNotificationRequest():

	global notificationTitle
	global notificationBody

	print notificationTitle
	print notificationBody

	return jsonify({
		"title": notificationTitle,
		"body": notificationBody,
		"icon":"notifications.png",
		"tag":"simple-push-demo-notification-tag",
		"url":"https://www.google.com"		
	})


if __name__=="__main__":
	app.run(host="0.0.0.0", debug = True)
    
    
