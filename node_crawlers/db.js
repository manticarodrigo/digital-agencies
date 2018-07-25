var MongoClient = require('mongodb').MongoClient;

const MONGODB_DB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const MONGODB_DB = process.env.MONGODB_DB || 'digital_agencies';
const MONGODB_RAW_COLLECTION = process.env.MONGODB_RAW_COLLECTION || 'profiles_raw';
const MONGODB_MERGED_COLLECTION = process.env.MONGODB_MERGED_COLLECTION || 'profiles_merged';

var url = MONGODB_DB_URI;

var _client;
var _db;

module.exports = {

  connectToServer: function(callback) {
    MongoClient.connect(url, function(err, client) {
      _client = client;
      _db = client.db(MONGODB_DB);
      return callback(err);
    });
  },

  getClient: function() {
    return _client;
  },

  getDb: function() {
    return _db;
  },

  updateItem: function(obj) {
    let unique_key = obj.id ? 'id' : 'name';
    _db.collection(MONGODB_RAW_COLLECTION).update(
        {
            unique_key: obj[unique_key],
            'provider': obj.provider
        },
        obj,
        { upsert: true },
        function(err, data) {
            if (err) {
                console.log(err);
            } else {
                console.log("document inserted");
            }
    });
  }
};

