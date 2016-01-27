from flask import Flask, render_template, request, jsonify

from flask.ext.mongoengine import MongoEngine

import json
from datetime import datetime
from gcm import GCM

app=Flask(__name__,template_folder="common",static_folder="common",static_url_path="")

app.config["MONGODB_SETTINGS"]={'db' : "ViralMint"}
#app.config["SECRET_KEY"] = "K33pTh1sS3cr3t"
db = MongoEngine(app)

#globals
#notificationTitle =''
#notificationBody = ''


class Subscriptions(db.Document):
	registrationId = db.StringField(max_length = 1000, required = True)
	subscriptionList = db.ListField()

class Notifications(db.Document):
	notificationTitle = db.StringField(required =True)
	notificationBody = db.StringField(max_length = 1000)
	timestamp = db.DateTimeField(required = True)
	registrationIds = db.ListField(db.StringField(max_length=1000))



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
	else:
		registrationId = endpoint



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
	else:
		registrationId = endpoint


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
	#print endpoint
	#print subscriptionList

	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
		#print "Registration ID (Subscribe): ", registrationId
		endpoint = 'https://android.googleapis.com/gcm/send'
	else:
		registrationId = endpoint


	subscription = Subscriptions()

	subscription.registrationId = registrationId
	subscription.subscriptionList = subscriptionList
	subscription.save()

	return jsonify({"Response":"success"})


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
	else:
		registrationId = endpoint

	subscription = Subscriptions.objects(registrationId = registrationId)
	subscription.delete()

	return jsonify({"Response" : "success"})


@app.route('/sendgcm',methods=['POST'])
def processGCMRequest():
    
    apiKey="AIzaSyBsyNVM0bH--tz4GvUmy7xagjTgfwwZKGg"
    
    gcm = GCM(apiKey)
    
    data = request.json

    #global notificationTitle
    #global notificationBody

    notificationTitle = data['notificationTitle']
    notificationBody = data['notificationBody']
    tags = data['tags']

    #print "Title: ", notificationTitle

    allSubscriptions = Subscriptions.objects.all()

    regIdList = []

    for subscription in allSubscriptions:
    	if( len(set(tags).intersection(set(subscription.subscriptionList)))):
    		regIdList.append(subscription.registrationId)


    if(len(regIdList) !=0):
	    newNotification = Notifications()

	    newNotification.notificationTitle = notificationTitle
	    newNotification.notificationBody = notificationBody
	    newNotification.timestamp = datetime.now()
	    newNotification.registrationIds = regIdList
	    newNotification.save()

    #print regIdList

    response = gcm.json_request(registration_ids=regIdList,data=data)
    return jsonify({"notification_title" : notificationTitle, "notification_text" : notificationBody})



@app.route('/sendrequest', methods=['GET','POST'])
def processNotificationRequest():

	data = request.json

	endpoint = data["Endpoint"]

	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
	else:
		registrationId = endpoint

	notificationList = Notifications.objects(registrationIds__contains = registrationId)

	notification = notificationList[len(notificationList)-1]

	notificationTitle = notification.notificationTitle
	notificationBody = notification.notificationBody

	#print notification.notificationTitle
	#print notification.notificationBody
	#notification = Notifications.objects(registrationIds__contains = registrationId).last()

	#for notification in Notifications.objects(registrationIds__contains = registrationId):
	#	print notification.notificationTitle
	#	print notification.notificationBody


	#global notificationTitle
	#global notificationBody

	#print notificationTitle
	#print notificationBody

	return jsonify({
		"title": notificationTitle,
		"body": notificationBody,
		"icon":"notifications.png",
		"tag":"simple-push-demo-notification-tag",
		"url":"https://www.google.com"		
	})

@app.route('/getNotifications',methods=['POST'])
def getNotificationList():

	data = request.json

	endpoint = data["Endpoint"]

	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
	else:
		registrationId = endpoint

	notificationList = Notifications.objects(registrationIds__contains = registrationId)

	return jsonify({"Notifications":notificationList})




if __name__=="__main__":
	app.run(host="0.0.0.0", debug = True)
    
    
