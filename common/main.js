var pushEnabled = false;     //global variable to handle subscription

window.addEventListener('load',function(){
    var pushButton = document.querySelector('#pushEnable-Button');

    pushButton.addEventListener('click',function(){
        
        if(pushEnabled){
            unsubscribe();  //unsubscribe if already subscribed
        }else{
            subscribe();    //else new subscription
        }
    });
    
    if('serviceWorker' in navigator){
        navigator.serviceWorker.register('serviceworker.js').then(initialiseState).catch(function(err){
            console.error('Error occured in registering service worker script',err);
        });
        
        console.log('Service worker registered');
    }else{
        console.warn("Service workers not supported in browser");
    }
});


function initialiseState(){
    
    if(!('showNotification' in ServiceWorkerRegistration.prototype )){
        console.warn("Notifications are not supported");
        return;
    }
    
    if(Notification.permission === 'denied'){
        console.warn("Notifications blocked by user");
        return;
    }
    
 navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
        
        serviceWorkerRegistration.pushManager.getSubscription().then(function(subscription){
            
            var pushButton = document.querySelector('#pushEnable-Button');
            pushButton.disabled = false;

            if(!subscription){
                return;
            }
            
            
            pushButton.textContent = 'Disable Push Notifications';
            pushEnabled = true;
	    
            //No need to send subscription status to server when page
            //is refreshed
            //sendSubscriptionToServer(subscription);
            
            $.ajax({

                url: '/getSubscriptionList',
                type:'POST',
                data : JSON.stringify({"Endpoint":subscription.endpoint}),
                dataType:'json',
                contentType:'application/json',
                accepts:'application/json',

                success:function(response){
                    console.log(response);
                    
                    for(var i=0;i<response.subscriptionList.length;i++){
                        
                        var checkboxId = response.subscriptionList[i];
                        document.getElementById(checkboxId).checked = true;
                        //console.log(checkboxId);
                    }
                },

                error:function(error){
                    return false;
                }
            });

	    
        }).catch(function(err){
            console.warn('Error during subscription : ',err);
        });
     
     
    });
}

function subscribe(){
    console.log("In subscribe ...")
    
    var pushButton = document.querySelector('#pushEnable-Button');

    //Array holding the subscribed items.
    //update=[]
    subscribedItems = [];
    
        
    var itemList = document.getElementsByClassName("item");
    
    //console.log(itemList.length);
    
    for(var i=0;i< itemList.length;i++){
        
        if( itemList[i].checked){
            subscribedItems.push(itemList[i].name);
        }
    }
    
    //console.log(subscribedItems);
    
    navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
        serviceWorkerRegistration.pushManager.subscribe({userVisibleOnly:true}).then(function(subscription){
            pushEnabled = true;
            pushButton.textContent = 'Disable Push Notifications';
            pushButton.disabled = false;
            
            console.log(subscription.endpoint);
            
            return sendSubscriptionToServer(subscription.endpoint, subscribedItems);
            
        }).catch(function(err){
            if(Notification.permission === 'denied'){
                console.warn('Permission denied ');
                pushButton.disabled = true;
                
            }else{
                console.error('Unable to push notification',err);
                pushButton.disabled = false;
                pushButton.textContent = 'Enable Push Notifications';
            }
        });
    });
}


function unsubscribe(){
    console.log('In unsubscribe ...');

    var pushButton = document.querySelector('#pushEnable-Button');
	pushButton.disabled = true;

    navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
	    serviceWorkerRegistration.pushManager.getSubscription().then(function(pushSubscription){
		if(!pushSubscription){
		    pushEnabled = false;
		    pushButton.disabled = false;
		    pushButton.textContent = 'Enable Push Notifications';
		    return;
		}

		pushSubscription.unsubscribe().then(function(successful){
		    pushButton.disabled = false;
		    pushButton.textContent = 'Enable Push Notifications';

		    pushEnabled = false;

		    sendUnsubscriptionToServer(pushSubscription.endpoint);

		}).catch(function(err){

		    console.log('Unsubscription error:',err);

		    pushButton.disabled = false;
		    pushButton.textContent = 'Enable Push Notifications';
        });
            
        }).catch(function(e){
           console.error('Error thrown while unsubscribing from push messaging');
        });
    });
}


function sendGCMRequest(){
    
    console.log("in GCM request")
    
    
    //tags holds the tags relevant to which the admin wants to send info
    var tags = []
    
    var tagList = document.getElementsByClassName("tag");
    
    for(var i=0;i<tagList.length;i++){
        
        if(tagList[i].checked){
            tags.push(tagList[i].name);
        }
    }
    
    var notificationTitle=document.getElementById('notificationTitle').value;
    var notificationBody=document.getElementById('notificationBody').value;

    $.ajax({
        
        url: '/sendgcm',
        type:'POST',
	data : JSON.stringify({"notificationTitle" : notificationTitle, "notificationBody" : notificationBody,"tags" : tags}),
        dataType:'json',
        contentType:'application/json',
        accepts:'application/json',

        success:function(response){
            return true;
        },
        
        error:function(error){
            return false;
        }
    });

}


function sendSubscriptionToServer(endpoint, subscribedItems){
    $.ajax({
        url: '/subscribe',
        data: JSON.stringify({"Endpoint":endpoint, "subscribedItems" : subscribedItems}),
        type:'POST',
        dataType:'json',
        contentType:'application/json',
        accepts:'application/json',
        
        success:function(response){
            return true;
        },
        
        error:function(error){
            return false;
        }
    });
}

function sendUnsubscriptionToServer(endpoint){
    $.ajax({
	url: '/unsubscribe',
	data: JSON.stringify({"Endpoint":  endpoint}),
	type: 'POST',
	dataType: 'json',
	contentType: 'application/json',
	accepts: 'application/json',

	success:function(response){
	    return true;
	},

	error:function(error){
	    return false;
	}
    });
}

function sendUpdatedItemsToServer(endpoint,updatedItems){

    $.ajax({
	url: '/updateSubscription',
	data: JSON.stringify({"Endpoint":  endpoint, "updatedItems":updatedItems}),
	type: 'POST',
	dataType: 'json',
	contentType: 'application/json',
	accepts: 'application/json',

	success:function(response){
	    return true;
	},

	error:function(error){
	    return false;
	}
    });
}



function sendUpdatedItems(){
    console.log("In update subscription ...")
    updatedItems = [];
    
    navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
        serviceWorkerRegistration.pushManager.getSubscription().then(function(subscription){
            if(!subscription){
                pushEnabled =false;
                pushButton.disabled = false;
                pushButton.textContent = 'Enable Push Notifications';
                console.error("Error : push subscription failed");            
                return;
                
            }

            var itemList = document.getElementsByClassName("item");

            for(var i=0;i<itemList.length;i++){
                if(itemList[i].checked){
                    updatedItems.push(itemList[i].name);
                }
            }
    
            var endpoint = subscription.endpoint;
            
            return sendUpdatedItemsToServer(endpoint,updatedItems);
                        
        }).catch(function(err){
            console.log(err);
        })
    });
}