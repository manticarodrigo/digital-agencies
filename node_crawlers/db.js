var MongoClient = require('mongodb').MongoClient;

const MONGODB_SERVER = process.env.MONGODB_SERVER || 'localhost';
const MONGODB_PORT = process.env.MONGODB_PORT || 27017;
const MONGODB_DB = process.env.MONGODB_DB || 'digital_agencies';
const MONGODB_RAW_COLLECTION = process.env.MONGODB_RAW_COLLECTION || 'profiles_raw';
const MONGODB_MERGED_COLLECTION = process.env.MONGODB_MERGED_COLLECTION || 'profiles_merged';

var url = `mongodb://${MONGODB_SERVER}:${MONGODB_PORT}/`;

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
};

