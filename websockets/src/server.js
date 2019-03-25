var mongo = require('./lib/index');
var sys = require('sys');
var events = require('events');
var moment = require('moment');
var deepcopy = require('deepcopy');
var https = require('https');
var fs = require('fs');

var settings = {};

process.argv.forEach(function (val, index, array) {
   if (val == "--ip") {
      settings.host = String(array[index +1]);
   }

   if (val == "--port") {
      settings.port = array[index +1];
   }

   if (val == "--ssl-cert") {
      settings.sslCert = String(array[index +1]);
   }

   if (val == "--ssl-key") {
      settings.sslKey = String(array[index +1]);
   }

   if (val == "--out") {
      settings.stdOut = String(array[index +1]);
      process.__defineGetter__('stdout', function() {
         return fs.createWriteStream(settings.stdOut);
      });
   }
   if (val == "--error") {
      settings.stdErr = String(array[index +1]);
      process.__defineGetter__('stderr', function() {
         return fs.createWriteStream(settings.stdErr);
      });
   }
});

//var options = {
   //key: fs.readFileSync(settings.sslKey),
   //cert: fs.readFileSync(settings.sslCert),
//};

//var tasks = require('./tasks/main');

//StreamLibrary.protoype.__proto__ = EventEmitter.prototype;
var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);

http.listen(settings.port, function(){
  console.log('listening on *:3000');
});

var clients = {};

io.on('connection', function(socket) {
   console.log("Client trying to connect");
   function connection(data) {
      if (typeof clients[data.user] === 'undefined') {
         clients[data.user] = {
            socket: [String("/#" + data.socketId)],
         };
         str = String(data.user + " connected on " + data.socketId);
         console.log(str);
      } else {
         var clientSockets = clients[data.user];
         var found = false;
         for (var i in clientSockets.socket) {
            if (data.socketId == clientSockets.socket[i]) {
               found = true;
            }
         }

         if (!found) {
            clients[data.user].socket.push(String("/#" + data.socketId));
            
            str = String(data.user + " connected on " + data.socketId);
            console.log(str);
         }
      }

      console.log(socket.handshake.address);
      console.log(data.socketId);
   };

   function disconnect(data) {
      var uidKeys = Object.keys(clients);

      console.log("disconnect happened");
      for(var i = 0; i < uidKeys.length; i++) {
         var uid = uidKeys[i];
         var clientSocket = clients[uid].socket;
         var index = clientSocket.indexOf(this.id);

         if (index >= 0) {
            clients[uid].socket.splice(index, 1);
         }

         if (data === uid) {
            clients[uid].socket.splice(index, 1);
         }
      }
   };

   function readNotification(data) {
         mongo.readNotification(data.id, data.uid, data.type);
   };

   function notification(data) {
      data = setupNotificiation(data); 
      
      if (data) {
         //mongo.addNotification(data);

         var clientUids = Object.keys(clients);
         for (var i = 0; i < clientUids.length; i++) {
            var uid = clientUids[i];
            
            if (typeof data.cc !== 'undefined' && typeof data.cc[uid] !== 'undefined' && 
                  !(typeof data.to != "undefine" && data.cc[uid] in data.to)) {
                  var copy = deepcopy(data);
                  var clientSocket = clients[uid].socket;
                  
                  copy.toastr.type = "info";
                  copy.type = "info";

                  if (copy.application == 'support-exceptions' && copy.message.action == 'add') {
                     copy.message.body = "You have been cc'ed on #" + copy.message.id +  " Support Exception";
                  } 
                  
                  for (var x = 0; x < clientSocket.length; x++) {
                     io.sockets.connected[clientSocket[x]].emit('notification', copy);
                  }

            } else if (typeof data.to[uid] !== 'undefined') {
                  var clientSocket = clients[uid].socket;
                  console.log(io.sockets.connected); 
                  console.log(clientSocket); 
                  console.log(clients); 
                  for (var x = 0; x < clientSocket.length; x++) {
                     io.sockets.connected[clientSocket[x]].emit('notification', data);
                  }
            }
         }
      }
   };
   
   function setupNotificiation(data) {
      data.toastr = {
            "closeButton": true,
            "debug": false,
            "progressBar": false,
            "positionClass": "toast-top-right",
            "showDuration": "1000",
            "hideDuration": "1000",
            "timeOut": "7000",
            "extendedTimeOut": "1000",
            "showEasing": "swing",
            "hideEasing": "linear",
            "showMethod": "fadeIn",
            "hideMethod": "fadeOut"
      };

      if (data.type == 'info') {
         data.toastr.closeButton = false;
         data.toastr.progressBar = true;
         data.toastr.timeOut = "7000";
      } else if (data.type == 'success') {
         data.toastr.closeButton = false;
         data.toastr.progressBar = true;
         data.toastr.timeOut = "7000";
      } else if (data.type == 'warning') {
         data.toastr.closeButton = false;
         data.toastr.timeOut = "9500";
      } else if (data.type == 'error') {
         data.toastr.timeOut = "0";
         data.toastr.extendedTimeOut = "0";
      } else {
         //io.emit('error', data);
      }
     
      //only used to send a notification system wide. 
      if (typeof data.to === 'undefined') {      	
         if (data.broadcast == true) {
            io.emit('notification', data);

         } else {
            //here will be an error "to be written"
            //data.type = 'error'
            io.emit('error', data);
         }

         return false;

      } else {
      
      }

      return data;
   };

   socket.on('connection', connection);
   socket.on('disconnect', disconnect);
   socket.on('read-notification', readNotification);

   socket.on('notification', notification);
   // socket.on('error', function(data) {
   // 	data.toastr = {
      //      "closeButton": true,
      //      "debug": false,
      //      "progressBar": false,
      //      "positionClass": "toast-top-right",
      //      "showDuration": "1000",
      //      "hideDuration": "1000",
      //      "timeOut": "0",
      //      "extendedTimeOut": "0",
      //      "showEasing": "swing",
      //      "hideEasing": "linear",
      //      "showMethod": "fadeIn",
      //      "hideMethod": "fadeOut"
   //   };
   //   data.type = 'error';
   //   data['event'] = 'error';
   //   data.message.body = "Unrecognized error occurred.";
   //   data.message.title = "Unknown error.";
   //   data.state.name = 'dashboard.error';
   //   data.state.params = '';
   //   data.toastr.closeButton = false;
   //   data.toastr.timeOut = "0";
   //   data.toastr.extendedTimeOut = "0";
   // 	io.emit('error', data);
   // });

});
