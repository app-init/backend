var mongodb = require('mongodb');
var MongoClient = mongodb.MongoClient;

collection.insert([object], function (err, result) {
	if (err) {
		console.log(err);
	} else {
		console.log('Inserted %d documents into collection. Documents inserted at: ', result.length, result);
	}
	db.close();
});

collection.find({identifier: ''}).toArray(function (err, result) {
  if (err) {
    console.log(err);
  } else if (result.length) {
    console.log('Found:', result);
  } else {
    console.log('No document found with that criteria.');
  }
  db.close();
});
