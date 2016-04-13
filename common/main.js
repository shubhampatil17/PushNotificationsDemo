var app = angular.module("pushNotifications",[]).controller("pushNotController", function($scope, $http, $window){

    $scope.pushEnabled = false;

    $window.addEventListener("load",function(){
        console.log("Loading window ...");
        var subscribeButton = $("#subscribeBtn");
        
        
        subscribeButton.change(function(){
            
            if($scope.pushEnabled){
                $scope.unsubscribe();
            }else{
                $scope.subscribe();
            }
        });
        
        if('serviceWorker' in navigator){
            console.log("Service workers are supported in browser");
            navigator.serviceWorker.register("serviceworker.js").then($scope.initialiseState).catch(function(err){
                console.error("Error occured in registering service worker script :",err);
            });
            
        }else{
            console.warn("Service workers not supported in browser");
        }
    });
    
    $scope.initialiseState = function(){
        console.log("In initialise State. Service worker registered");
        
        if(!('showNotification' in ServiceWorkerRegistration.prototype)){
            console.warn("Notifications are not supported");
            return;
        }
        
        if(Notification.permission == "denied"){
            console.warn("Notifications blocked by user");
            return;
        }
        
        navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
           serviceWorkerRegistration.pushManager.getSubscription().then(function(subscription){
               $("#subscribeBtn")[0].checked = false;
               $("#allowPushBtn")[0].checked = false;
               
               if(!subscription){
                   $("#subTagBox")[0].style.display = "none";
                   $("#allowPushBtnBox")[0].style.display = "none";
                   return;
               }
               
               $("#subTagBox")[0].style.display = "block";
               $("#allowPushBtnBox")[0].style.display = "block";
               $("#subscribeBtn")[0].checked = true;
               $("#allowPushBtn")[0].checked = true;
               $scope.pushEnabled = true;
               
                //No need to send subscription status to server when page is refreshed
                //sendSubscriptionToServer(subscription);
               
                $http({
                    method : "POST",
                    url : "/getSubscriptionData",
                    data : {"Endpoint":subscription.endpoint}
                    
                }).then(function(response){
                    console.log(response);
                    
                    for(var i=0;i<response.data.subscriptionList.length;i++){
                        var checkboxId = response.data.subscriptionList[i];
                        document.getElementById(checkboxId).checked = true;
                    }
                    
                    if(response.data.pushAllowed == "true"){
                        $("#allowPushBtn")[0].checked = true;
                    }else{
                        $("#allowPushBtn")[0].checked = false;
                    }
                    
                }, function(error){
                    return false;
                });
           }) 
        }).catch(function(err){
           console.warn("Error during subscription : ", err); 
        });
        
    }
    
    $scope.subscribe = function(){
        console.log("In subscribe ...")
        
        //Array holding the subscribed items.
        subscribedItems = []
        
        var itemList = document.getElementsByClassName("item");
        
        for(var i=0;i<itemList.length;i++){
            if(itemList[i].checked){
                subscribedItems.push(itemList[i].name);
            }
        }
        
        //console.log(subscribedItems);
        
        navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
            serviceWorkerRegistration.pushManager.subscribe({
                userVisibleOnly : true
            }).then(function(subscription){
                
                console.log(subscription.endpoint);

                
                var pushAllowed = "true"
                $scope.sendSubscriptionToServer(subscription.endpoint,subscribedItems, pushAllowed )                
            }).catch(function(err){
                
                if(Notification.permission == "denied"){
                    console.warn("Permission denied");
                }else{
                    console.error("Unable to push notification",err);
                    $("#subscribeBtn")[0].checked = false;
                }
            });
        });
        
    }
    
    

    $scope.sendSubscriptionToServer = function(endpoint, subscribedItems, pushAllowed){
        $http({
            method : "POST",
            url : "/subscribe",
            data : {"Endpoint":endpoint,"subscribedItems": subscribedItems,"pushAllowed":pushAllowed}
        }).then(function(response){

                $scope.pushEnabled = true;
                $("#subscribeBtn")[0].checked = true;
                $("#allowPushBtn")[0].checked = true;

                $("#subTagBox")[0].style.display = "block";
                $("#allowPushBtnBox")[0].style.display = "block";
                return true;
            
        },function(error){
            return false;
        });
    }
    
    
        
    $scope.unsubscribe = function(){
        console.log('In unsubscribe ...');        
        navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
            serviceWorkerRegistration.pushManager.getSubscription().then(function(pushSubscription){
                if(!pushSubscription){
                    $scope.pushEnabled = false;
                    $("#subscribeBtn")[0].checked = false;
                    $("#subTagBox")[0].style.display = "none";
                    $("#allowPushBtnBox")[0].style.display = "none";
                    return;
                }
                
                pushSubscription.unsubscribe().then(function(successful){
                    $scope.sendUnsubscriptionToServer(pushSubscription.endpoint);
                    
                }).catch(function(err){
                    console.error("Unsubscription error :",err);
                    $("#subscribeBtn")[0].checked = false;
                })
            }).catch(function(e){
                console.error('Error thrown while unsubscribing from push messaging');    
            })
        })
    }
    
    

    $scope.sendUnsubscriptionToServer = function(endpoint){
        $http({
            method : "POST",
            url : "/unsubscribe",
            data : {"Endpoint":endpoint}
        }).then(function(response){

            $("#subscribeBtn")[0].checked = false;

            $scope.pushEnabled = false;

            $("#subTagBox")[0].style.display = "none";
            $("#allowPushBtnBox")[0].style.display = "none";

            return true;
            
        },function(error){
            return false;
        });
    }
    
    $scope.sendUpdatedItemsToServer = function(endpoint, updatedItems, pushAllowed){
        $http({
            method : "POST",
            url : "/updateSubscription",
            data : {"Endpoint":endpoint,"updatedItems":updatedItems, "pushAllowed":pushAllowed}
            
        }).then(function(response){
            return true;
        },function(error){
            return false;
        });
    }
    
    $scope.sendUpdatedItems = function(){
        console.log("In Update Subscription ...");
        updatedItems = [];
        
        navigator.serviceWorker.ready.then(function(serviceWorkerRegistration){
            serviceWorkerRegistration.pushManager.getSubscription().then(function(subscription){
                if(!subscription){
                    $scope.pushEnabled  = false;
                    $("#subscribeBtn")[0].checked = false;
                    $("#subTagBox")[0].style.display = "none";
                    $("#allowPushBtnBox")[0].style.display = "none";
                    
                    console.error("Error : push subscription failed");
                    return ;
                }
                
                var itemList = document.getElementsByClassName("item");
                
                for(var i=0;i<itemList.length;i++){
                    if(itemList[i].checked){
                        updatedItems.push(itemList[i].name);
                    }
                }
                
                var endpoint = subscription.endpoint;
                
                var pushAllowed = $("#allowPushBtn")[0].checked.toString();
                
                return $scope.sendUpdatedItemsToServer(endpoint, updatedItems, pushAllowed);
                
            }).catch(function(err){
                console.log(err);
            })
        })
    }

    $scope.sendGCMRequest = function(){
        console.log("In GCM Request");
        
        //tags holds the tags relevant to which the admin wants to send info
        var tags = [];
        var tagList = document.getElementsByClassName("tag");
        
        for(var i=0;i<tagList.length;i++){
            if(tagList[i].checked){
                tags.push(tagList[i].name);
            }
        }
        
        var notificationTitle = $("#notificationTitle")[0].value;
        var notificationBody = $("#notificationBody")[0].value;
        
        if(tags.length==0 || notificationTitle=="" || notificationBody == ""){
            
            Materialize.toast("Error ! Something missing on Publisher's Side.", 2000, "rounded");
            return;
        }
        
        console.log(notificationBody);
        $http({
            method : "POST",
            url : "/sendgcm",
            data : {"notificationTitle":notificationTitle, "notificationBody":notificationBody,"tags":tags}
        }).then(function(response){
            return true;    
        },function(error){
            return false;
        });
    }
    
})