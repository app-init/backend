var mongodb = require('mongodb');
var MongoClient = mongodb.MongoClient;
var ObjectId = mongodb.ObjectID
var hostname = 'cee-tools-devel-mongodb';
var port = '27017'
var url = 'mongodb://' + hostname +':'+ port +'/cee-tools';

module.exports.addNotification = function (data) {
	MongoClient.connect(url, function(err, db) {
		if (err) {
			console.log('Unable to connect to server.  Error', err);
		} else {
			console.log('Connection established to', url);
			
			notification = db.collection('notifications');

			notification.insert(data, function (err, result) {
				if (err) {
					console.log(err);
               db.close();
				}

				db.close();
			});
		}
	});
}

module.exports.readNotification = function (id, uid, type) {
	MongoClient.connect(url, function(err, db) {
		if (err) {
			console.log('Unable to connect to server.  Error', err);
		} else {
			console.log('Connection established to', url);
			
			notification = db.collection('notifications');
            
            notification.findOne({"_id": id}, function(err, doc) {
                if ((typeof doc !== 'undefined' && doc != null ) && type === "to") {
                    if (typeof doc.to[uid] !== 'undefined') {
                        var update = {
                            "$set": {
                                "to": doc.to,
                            }
                        };

                        update['$set']['to'][uid] = {
                            is_read: true,
                        }


                        notification.update({"_id":id}, update, function (err, result) {
                            if (err) {
                                console.log(err);
                                db.close();
                            }

                            db.close();
                        });
                    }
                } else {
                    if ((typeof doc !== 'undefined' && doc != null) && typeof doc.cc[uid] !== "undefined") {
                        var update = {
                            "$set": {
                                "cc": doc.cc,
                            }
                        };

                        update['$set']['cc'][uid] = {
                            is_read: true,
                        }

                        notification.update({"_id":id}, update, function (err, result) {
                            if (err) {
                                console.log(err);
                                db.close();
                            }

                            db.close();
                        });
                    }
                }
            });


		}
	});
}


/*module.exports.getNotification = function(id) {
	MongoClient.connect(url, function(err, db) {
		if (err) {
			console.log('Unable to connect to server.  Error', err);
		} else {
			console.log('Connection established to', url);
			
			notification = db.collection('notification');

			notification.find({"_id": ObjectId(id)}).toArray(function (err, result) {
			  if (err) {
			    console.log(err);
			  } else if (result.length) {
			    console.log('Found:', result);
			  } else {
			    console.log('No document found with that criteria.');
			  }
			  db.close();
			});

		}
	});	
}*/

// function remove_notification(id) {
// 	MongoClient.connect(url, function(err, db) {
// 		if (err) {
// 			console.log('Unable to connect to server.  Error', err);
// 		} else {
// 			console.log('Connection established to', url);
			
// 			notification = db.collection('notification');

// 			notification.update({"_id": ObjectId(id)}, {$pull: {ObjectId(id)}}, function (err, numUpdated) {
// 				if (err) {
// 					console.log(err);
// 				} else if (numUpdated) {
// 					console.log('Pull successful. %d pulled.', numUpdated);
// 				} else {
// 					console.log('No document of that description found.');
// 				}
// 				db.close();
// 			});
// }

// function update_notification(id, notificationObject) {
// 	MongoClient.connect(url, function(err, db) {
// 		if (err) {
// 			console.log('Unable to connect to server.  Error', err);
// 		} else {
// 			console.log('Connection established to', url);
			
// 			events = db.collection('events');
// 			users = db.collection('users');

// 			events.update({"_id": ObjectId(id)}, {$set: {enabled: false}}, function (err, numUpdated) {
// 				if (err) {
// 					console.log(err);
// 				} else if (numUpdated) {
// 					console.log('Update successful. %d updated.', numUpdated); 
// 				} else {
// 					console.log('No document of that description found.');
// 				}
// 			});

// 			//will need to open update the pointer on the user collection.
// 			//might only have to return the new notification object and the pointer will
// 			//stay the same.
// 			//DON'T WORRY ABOUT THIS PART MOWENS WILL TAKE CARE OF IT!!!!!!!!
// 			db.close();
			
// 		}
// 	});
// }
