from flask import Flask, jsonify
from pymongo import MongoClient
import json
with open('users.json') as file:
	tabla_usuarios= json.load(file)
app = Flask(__name__)


client = MongoClient() #localhost 27017
db = client.caca #mi base de datos se llama test
users = db.users #dentro de test, una coleccion es users
#users.insert_many(tabla_usuarios)
tweets = db.tweets #dentro de test, otra coleccion es tweets



@app.route("/")
def hello():
    return "Hello World!"



@app.route("/users/<id>")
def find_users(id=None):	
	results = users.find({"id":int(id)},{"_id":0})

										# esta id que genera mongo no es serializable por python, por lo que pongo _id: 0 para que no lo muestre
					# nombre que se muestra
	return jsonify("users", [user for user in results])



@app.route("/tweets/<mid>")
def find_tweets(mid=None):
	pass

@app.route("/msg")
def find_tweets_by_user():
	pass



if __name__ == '__main__':
	app.run(port=2000)