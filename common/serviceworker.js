var title, body, icon, tag, url;

self.addEventListener('push', function(event) {  
    
    console.log('Received a push event message', event);
        
    event.waitUntil(
        
        fetch("/sendrequest").then(function(response){
            
            if(response.status !== 200){
                console.log("Error");
                return;
            }
            
            response.json().then(function(data){
                title = data['title'];
                body = data['body'];
                icon = data['icon'];
                tag = data['tag'];
                url = data['url'];
                
                self.registration.showNotification(title,{
                    body: body,
                    icon: icon,
                    tag: tag
                })
            });
        })
    );
    

});


self.addEventListener('notificationclick',function(event){
    event.notification.close();
    
    event.waitUntil(
        clients.matchAll({
            includeUncontrolled:true,
            type:"window"
        }).then(function(clientList){
            
            console.log(clientList);
            
            for(var i=0;i<clientList.length;i++){
                    var client=clientList[i];
                if(client.url=== url && "focus" in client)
                    return client.focus();
            }
            
            if(clients.openWindow){
                return clients.openWindow(url);
            }
        })
    );
});


