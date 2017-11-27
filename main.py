from flask import Flask, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
from flask import request
from datetime import datetime
from math import log

import json

with open('users.json') as file:
    users_json = json.load(file)
with open('messages.json')as file:
    msgs_json = json.load(file)

#####################################
#####################################
#####################################
#####################################
# OBJETOS PARA BUSQUEDA DE TEXTOS

# primero enumeramos los mensajes
# no es el id oficial, es solo algo intero para el text search

dic_msgs = dict()  # diccionario de relacion llave - mensaje
id = 0
for i in msgs_json:
    dic_msgs[id] = i
    id += 1
nro_docs = id

# print(dic_msgs)

lemario = set()  # conjunto de palabras en nuestro lemario
for i in msgs_json:
    for palabra in i["message"].split(" "):
        lemario.add(palabra)

dic_palabras = dict()  # diccionario de relacion llave - palabra
idp = 0
for i in lemario:
    dic_palabras[idp] = i
    idp += 1
nro_words = idp

# print(lemario)

BigTable = []
score = dict()

for j in range(nro_words):
    score[j] = 0  # contador de apariciones en documentos

for i in range(nro_docs):  # filas son id de mensajes/documentos

    fila = []  # fila para documento de id = i

    for j in range(nro_words):  # columnas son id de las palabras

        rep = 0  # numero de apariciones de palabra de id = j en documento de id = i
        aparece = False

        for palabra in dic_msgs[i]["message"].split(" "):

            if palabra == dic_palabras[j]:
                rep += 1
                aparece = True

        if aparece:
            score[j] += 1

        fila.append(rep)  # la entrada es el numero de apariciones de la palabra en el texto

    BigTable.append(fila)

# memo: [27/11/17 15:58] stgo armstrong
# estoy conciente q hay formatos mucho mas eficientes de guardar una matriz sparse,
# pero este es un ejemplo de juguete asi q filo

# print(dic_palabras)
# print(score)

# print(BigTable)



# F I N
#####################################
#####################################
#####################################
#####################################



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
    lon = request.args.get('long', None)
    if (base and top and lat and lon):
        # http://localhost:2000/users/1/search?idate=2016-01-01&fdate=2016-02-02&lat=-33.05&long=-71.616667
        results = msgs.find(
            {"date": {'$lt': top, '$gte': base}, "sender": int(uid), "lat": float(lat), "long": float(lon)}, {"_id": 0})
        return jsonify("msgs", [msg for msg in results])
    elif (base and top):
        # http://localhost:2000/users/1/search?idate=2016-01-01&fdate=2016-02-02

        results = msgs.find({"date": {'$lt': top, '$gte': base}, "sender": int(uid)}, {"_id": 0})
        return jsonify("msgs", [msg for msg in results])
    elif (lat and lon):
        # http://localhost:2000/users/1/search?lat=-33.05&long=-71.616667
        results = msgs.find({"sender": int(uid), "lat": float(lat), "long": float(lon)}, {"_id": 0})
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
    lon = request.args.get('long', None)

    list = [base, top, lat, lon]

    if all([i != None for i in list]):
        # http://localhost:2000/tweets/1/16/search?idate=2015-08-28&fdate=2015-08-28&lat=-33.05&long=-71.616667

        tuits = msgs.find({"sender": int(mid), "receptant": int(uid), "lat": float(lat),
                           "long": float(lon), "date": {'$lt': top, '$gte': base}}, {"_id": 0})

    elif top != None and base != None and (lat == None or lon == None):
        tuits = msgs.find({"sender": int(mid), "receptant": int(uid), "date": {'$lt': top, '$gte': base}}, {"_id": 0})

    elif lat != None and lon != None and (base == None or top == None):
        tuits = msgs.find({"sender": int(mid), "receptant": int(uid), "lat": float(lat),
                           "long": float(lon)}, {"_id": 0})

    else:

        tuits = msgs.find({"sender": int(mid), "receptant": int(uid)}, {"_id": 0})

    tuits = [msg for msg in tuits]
    return jsonify(msgs=tuits)


# BUSQUEDA TEXTOS
@app.route("/msgs/textsearch", methods=['GET'])
def text_search():
    text = request.args.get('text', None)

    # PROTOCOLO PROPIO DE TF - IDF
    # EN NUESTRO PROTOCOLO EL SCORE DE UN DOCUMENTO ES LA SUMA DEL
    # VECTOR DE TF_IDF's DE LA BUSQUEDA EN ESE TEXTO
    if text:
        vector = [i for i in text.split(" ")]

        arg_max = 0  # por defecto el mejor documento es el con id 0
        max_score = 0  # el mejor score es cero
        arg_max2 = 0  # SEGUNDO LUGAR
        max_score2 = 0  # SEGUNDO LUGAR
        arg_max3 = 0  # TERCERO
        max_score3 = 0  # TERCERO

        for i in range(nro_docs):
            doc_score = 0

            for palabra in vector:

                if palabra in lemario:
                    id = None
                    for k in range(nro_words):
                        if dic_palabras[k] == palabra:
                            id = k
                    if id:
                        doc_score += BigTable[i][id] * log(nro_docs / score[id])

            if doc_score >= max_score:
                arg_max = i
                max_score = doc_score

            elif doc_score >= max_score2:
                arg_max2 = i
                max_score2 = doc_score

            elif doc_score >= max_score3:
                arg_max3 = i
                max_score3 = doc_score

        pri = msgs.find({"message": dic_msgs[arg_max]["message"]}, {"_id": 0})
        seg = msgs.find({"message": dic_msgs[arg_max2]["message"]}, {"_id": 0})
        ter = msgs.find({"message": dic_msgs[arg_max3]["message"]}, {"_id": 0})

        pri = [i for i in pri]
        seg =  [i for i in seg]
        ter = [i for i in ter]

        if max_score == 0:
            pri = "-"

        if max_score2 == 0:
            seg = "-"

        if max_score3 == 0:
            ter = "-"

        return jsonify(primero = pri[0], score = max_score, segundo = seg[0] , score2 = max_score2, tercero = ter[0],  score3 = max_score3)


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
