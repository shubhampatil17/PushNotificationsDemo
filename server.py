from flask import Flask, render_template, request, jsonify

from flask.ext.mongoengine import MongoEngine

import json
from datetime import datetime
from gcm import GCM

app=Flask(__name__,template_folder="common",static_folder="common",static_url_path="")

app.config["MONGODB_SETTINGS"]={'db' : "PushNotificationsDB"}
db = MongoEngine(app)



class Subscriptions(db.Document):
	registrationId = db.StringField(max_length = 1000, required = True)
	subscriptionList = db.ListField(default=[])
	pushAllowed = db.StringField(default="true")

class Notifications(db.Document):
	notificationTitle = db.StringField(required =True)
	notificationBody = db.StringField(max_length = 1000)
	registrationIds = db.ListField(db.StringField(max_length=1000))



@app.route('/')
def initialiseTemplate():
	return render_template('notificationPanel.html')
    

@app.route('/getSubscriptionData',methods=['POST'])
def sendSubscriptionData():

	data = request.json	
	endpoint = data["Endpoint"]

	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
	else:
		registrationId = endpoint



	for subscription in Subscriptions.objects(registrationId = registrationId):
		subscriptionList = subscription.subscriptionList
		pushAllowed = subscription.pushAllowed		

	return jsonify({"subscriptionList" : subscriptionList, "pushAllowed":pushAllowed})


@app.route('/subscribe', methods=['POST'])
def processSubscriptionRequest():

	data = request.json

	endpoint = data["Endpoint"]
	subscriptionList = data["subscribedItems"]
	pushAllowed = data["pushAllowed"]

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
	subscription.pushAllowed = pushAllowed
	subscription.save()

	return jsonify({"Response":"success"})


#Function used to delete entry from database on unsubscription
@app.route('/unsubscribe', methods = ['POST'])
def unsubscribeFromServer():
	data = request.json
	endpoint = data['Endpoint']

	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
		endpoint = 'https://android.googleapis.com/gcm/send'
	else:
		registrationId = endpoint

	subscription = Subscriptions.objects(registrationId = registrationId)
	subscription.delete()

	return jsonify({"Response" : "success"})


@app.route('/updateSubscription',methods=['POST'])
def updateSubscriptionList():

	data = request.json

	endpoint = data["Endpoint"]
	updatedList = data["updatedItems"]
	pushAllowed = data["pushAllowed"]

	if endpoint.startswith('https://android.googleapis.com/gcm/send'):
		endpointParts = endpoint.split('/')
		registrationId = endpointParts[len(endpointParts) - 1]
	else:
		registrationId = endpoint


	for subscription in Subscriptions.objects(registrationId = registrationId):
		subscription.subscriptionList = updatedList
		subscription.pushAllowed = pushAllowed
		subscription.save()

	return jsonify({"Response":"success"})

@app.route('/sendgcm',methods=['POST'])
def processGCMRequest():
    
    apiKey="AIzaSyDTJukW0BARTSXHRiWPCt8y_e17A9PuYfg"
    
    gcm = GCM(apiKey)
    
    data = request.json

    notificationTitle = data['notificationTitle']
    notificationBody = data['notificationBody']
    tags = data['tags']

    allSubscriptions = Subscriptions.objects.all()

    regIdList = []

    for subscription in allSubscriptions:
    	if( len(set(tags).intersection(set(subscription.subscriptionList))) and subscription.pushAllowed == "true"):
    		regIdList.append(subscription.registrationId)


    if(len(regIdList) !=0):
	    newNotification = Notifications()

	    newNotification.notificationTitle = notificationTitle
	    newNotification.notificationBody = notificationBody
	    newNotification.registrationIds = regIdList
	    newNotification.save()
	
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

	notificationList.delete()

	return jsonify({
		"title": notificationTitle,
		"body": notificationBody,
		"icon":"notifications.png",
		"tag":"simple-push-demo-notification-tag",
		"url":"https://github.com/shubhampatil17"		
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
    
    
'''
1) Delete endpoints from notification table when unsubscribed from server
2) push all notifications in the user panel on front end
3) Seperate user panel and admin panel
4) Host on Heroku.
5) Introduce Bootstrap and Materialize to enrich GUI.
'''
