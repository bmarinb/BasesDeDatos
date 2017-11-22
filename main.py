from flask import Flask, jsonify
from pymongo import MongoClient
import json
with open('users.json') as file:
	users_json= json.load(file)
with open('messages.json')as file:
	msgs_json = json.load(file)
app = Flask(__name__)


client = MongoClient() #localhost 27017
db = client.grupo11 #mi base de datos se llama test
users = db.users #dentro de test, una coleccion es users
#users.insert_many(users_json)
msgs = db.msgs #dentro de test, otra coleccion es tweets
msgs.insert_many(msgs_json)
@app.route("/")
def hello():
    return "Hello World!"



@app.route("/users/<id>")
def find_users(id=None):	
	results = users.find({"id":int(id)},{"_id":0})


	return jsonify("users", [user for user in results])



@app.route("/msgs/<mid>")
def find_msgs(mid=None):
	results = msgs.find({"id":int(mid)},{"_id":0})

	return jsonify("msgs", [msg for msg in results])	




if __name__ == '__main__':
	app.run(port=2000)