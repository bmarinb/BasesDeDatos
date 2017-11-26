from flask import Flask, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
from flask import request
from datetime import datetime

import json

with open('users.json') as file:
    users_json = json.load(file)
with open('messages.json')as file:
    msgs_json = json.load(file)

app = Flask(__name__)

client = MongoClient()  # localhost 27017
db = client.grupo11  # mi base de datos se llama test
users = db.users  # dentro de test, una coleccion es users
users.insert_many(users_json)
msgs = db.msgs  # dentro de test, otra coleccion es tweets

msgs.insert_many(msgs_json)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/users/<id>")
def find_users(id=None):
    result = {}
    artist = users.find({"id": int(id)}, {"_id": 0})
    artist = next(artist)
    artist_msgs = msgs.find({"sender": int(id)}, {"_id": 0})
    artist_msgs = [msg for msg in artist_msgs]
    return jsonify(artist=artist, msgs=artist_msgs)


@app.route("/msgs/<mid>")
def find_msgs(mid=None):
    a = int('5a14f1e3e3928a3d598f67df', 16)
    base = request.args.get('idate', None)
    print(base)
    msg_id = hex(a + int(mid))
    msg_id = msg_id[2:]
    results = msgs.find({"_id": ObjectId(msg_id)}, {"_id": 0})
    return jsonify("msgs", [msg for msg in results])

@app.route("/users/<uid>/search", methods=['GET'])
def find_msgs_date(uid=None):
    base = request.args.get('idate', None)
    top = request.args.get('fdate', None)
    lat = request.args.get('lat', None)
    lon =  request.args.get('long', None)
    if (base and top and lat and lon):
        #http://localhost:2000/users/1/search?idate=2016-01-01&fdate=2016-02-02&lat=-33.05&long=-71.616667
        results = msgs.find({"date": {'$lt': top, '$gte': base}, "sender": int(uid), "lat":float(lat), "long":float(lon)}, {"_id": 0})
        return jsonify("msgs", [msg for msg in results]) 
    elif(base and top):
        #http://localhost:2000/users/1/search?idate=2016-01-01&fdate=2016-02-02

        results = msgs.find({"date": {'$lt': top, '$gte': base}, "sender": int(uid)}, {"_id": 0})
        return jsonify("msgs", [msg for msg in results]) 
    elif(lat and lon):
        #http://localhost:2000/users/1/search?lat=-33.05&long=-71.616667
        results = msgs.find({"sender": int(uid), "lat":float(lat), "long":float(lon)}, {"_id": 0})
    else:
        return find_users(uid)


@app.route("/tweets/<mid>/<uid>")
def find_tweets_by_user(mid=None, uid=None):
    tuits = msgs.find({"sender": int(mid), "receptant": int(uid)}, {"_id": 0})
    tuits = [msg for msg in tuits]
    return jsonify(msgs=tuits)


@app.route("/tweets/<mid>/<uid>/search", methods=['GET'])
def filter_tweets_by_user(mid=None, uid=None):
    
    base = request.args.get('idate', None)
    top = request.args.get('fdate', None)
    lat = request.args.get('lat', None)
    lon =  request.args.get('long', None)

    list = [base,top,lat,lon]

    if all([i != None for i in list]):
        #http://localhost:2000/tweets/1/16/search?idate=2015-08-28&fdate=2015-08-28&lat=-33.05&long=-71.616667

        tuits = msgs.find({"sender": int(mid), "receptant": int(uid), "lat": float(lat),
         "long": float(lon),"date": {'$lt': top, '$gte': base}}, {"_id": 0})

    elif top != None and base != None and (lat == None or lon == None):
        tuits = msgs.find({"sender": int(mid), "receptant": int(uid), "date": {'$lt': top, '$gte': base}}, {"_id": 0})

    elif lat != None and lon != None and (base == None or top == None):
        tuits = msgs.find({"sender": int(mid), "receptant": int(uid),  "lat": float(lat),
         "long": float(lon)}, {"_id": 0})

    else:
        
        tuits = msgs.find({"sender": int(mid), "receptant": int(uid)}, {"_id": 0})

    tuits = [msg for msg in tuits]
    return jsonify(msgs=tuits)

"""
@app.route("/tweets/<mid>/<uid>/<date>")
def filter_date(date=None, mid=None, uid=None):
    if date != "any":
        tuits = msgs.find({"sender": int(mid), "receptant": int(uid), "date": date}, {"_id": 0})
    else:
        tuits = msgs.find({"sender": int(mid), "receptant": int(uid)}, {"_id": 0})
    tuits = [msg for msg in tuits]
    return jsonify(msgs=tuits)

"""

if __name__ == '__main__':
    app.run(port=2000)
