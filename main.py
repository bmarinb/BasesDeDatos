from flask import Flask, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
import json
with open('users.json') as file:
	users_json= json.load(file)
with open('messages.json')as file:
	msgs_json = json.load(file)
app = Flask(__name__)


client = MongoClient() #localhost 27017
db = client.grupo11 #mi base de datos se llama test
users = db.users #dentro de test, una coleccion es users
# users.insert_many(users_json)
msgs = db.msgs #dentro de test, otra coleccion es tweets
# msgs.insert_many(msgs_json)
@app.route("/")
def hello():
    return "Hello World!"



@app.route("/users/<id>")
def find_users(id=None):	
	result = {}
	artist = users.find({"id":int(id)},{"_id":0})
	artist = next(artist)
	artist_msgs = msgs.find({"sender":int(id)},{"_id":0})
	artist_msgs = [msg for msg in artist_msgs]	
	return jsonify(artist=artist, msgs=artist_msgs)	


@app.route("/msgs/<mid>")
def find_msgs(mid=None):
	a = int('5a14f1e3e3928a3d598f67df',16)
	msg_id = hex(a+int(mid))
	msg_id = msg_id[2:]
	results = msgs.find({"_id": ObjectId(msg_id)},{"_id":0})
	return jsonify("msgs", [msg for msg in results])	




if __name__ == '__main__':
	app.run(port=2000)