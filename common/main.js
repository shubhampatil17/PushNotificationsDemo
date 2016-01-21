var pushEnabled = false;

window.addEventListener('load',function(){
    var pushButton = document.querySelector('#push-Button');

    pushButton.addEventListener('click',function(){
        
        if(pushEnabled){
            unsubscribe();
        }else{
            subscribe();
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
        console.warn("Notifications not supported");
        return;
    }
    
    if(Notification.permission === 'denied'){
        console.warn("Notifications blocked by user");
        return;
    }
    
 navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
        
        serviceWorkerRegistration.pushManager.getSubscription().then(function(subscription){
            
            var pushButton = document.querySelector('#push-Button');
            pushButton.disabled = false;

	    console.log(subscription)
            if(!subscription){
                return;
            }
            
            
            pushButton.textContent = 'Disable Push Notifications';
            pushEnabled = true;
	    sendSubscriptionToServer(subscription);
	    
        }).catch(function(err){
            console.warn('Error during subscription : ',err);
        });
 });

   // console.log("State initialized")
}

function subscribe(){
    
    var pushButton = document.querySelector('#push-Button');

    //Array holding the requested updates
    updates = [];
    
    var shoes = document.getElementById('shoes');
    var shirts = document.getElementById('shirts');
    var tees = document.getElementById('tees');
    var jeans = document.getElementById('jeans');
    var trousers = document.getElementById('trousers');
    var traditionals = document.getElementById('traditionals');

    if(shoes.checked)
	updates.push('shoes');
    if(shirts.checked)
	updates.push('shirts');
    if(tees.checked)
	updates.push('tees');
    if(jeans.checked)
	updates.push('jeans');
    if(trousers.checked)
	updates.push('trousers');
    if(traditionals.checked)
	updates.push('traditionals');
    
    pushButton.disabled = true;
           
navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
       
serviceWorkerRegistration.pushManager.subscribe({userVisibleOnly:true}).then(function(subscription){
            pushEnabled = true;
            pushButton.textContent = 'Disable Push Notifications';
            pushButton.disabled = false;
            
            console.log(subscription.endpoint);
            
            return sendSubscriptionToServer(subscription, updates);
            
        }).catch(function(err){
            if(Notification.permission === 'denied'){
                console.warn('Permission denied ');
                pushButton.disabled = true;
            }else{
                console.error('Unable to push notification',err);
                pushButton.disabled = false;
                pushButton.textContent = 'Enable Push Messages';
            }
        });
    });
}


function unsubscribe(){
    console.log('In unsubscribe');
	var pushButton = document.querySelector('#push-Button');
	pushButton.disabled = true;

    navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
	    serviceWorkerRegistration.pushManager.getSubscription().then(function(pushSubscription){
		if(!pushSubscription){
		    pushEnabled = false;
		    pushButton.disabled = false;
		    pushButton.textContent = 'Enable push notifications';
		    return;
		}

		var subscriptionId = pushSubscription.subscriptionId;

		pushSubscription.unsubscribe().then(function(successful){
		    pushButton.disabled = false;
		    pushButton.textContent = 'Enable push notifications';

		    pushEnabled = false;

		    sendUnsubscriptionToServer(pushSubscription);

		}).catch(function(e){

		    console.log('Unsubscription error:',e);

		    pushButton.disabled = false;
		    pushButton.textContent = 'Enable push notifications';
        });
            
        }).catch(function(e){
           console.error('Error thrown while unsubscribing from push messaging');
        });
    });
}

function sendSubscriptionToServer(subscription, updates){
    $.ajax({
        url: '/sendendpoint',
        data: JSON.stringify({"Endpoint":subscription.endpoint, "Objects" : updates}),
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

function sendUnsubscriptionToServer(subscription){
    $.ajax({
	url: '/unsubscribe',
	data: JSON.stringify({"Endpoint": subscription.endpoint}),
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

function sendGCMRequest(){
    console.log("in GCM request")
    //tags holds the tags relevant to which the admin wants to send info
    var tags = []
    var shoes_dashboard = document.getElementById('shoes_dashboard')
    if(shoes_dashboard.checked)
	tags.push('shoes')
    var notification_title = document.getElementById('notification_title').value
    var notification_text = document.getElementById('notification_text').value
    console.log(tags)

    $.ajax({
        url: '/sendgcm',
        type:'POST',
	data : JSON.stringify({"notification_title" : notification_title, "notification_text" : notification_text,"tags" : tags}),
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
