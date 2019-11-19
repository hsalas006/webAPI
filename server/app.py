from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import bcrypt
import json
from bson import json_util

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ApiGenDatabase
users = db["Users"]
functions = db["Funtions"]

def toJson(data):
    return json.dumps(data, default=json_util.default)

class Register(Resource):
    def post(self):
        postedData = request.get_json()

        email= postedData["email"]
        password= postedData["password"]

        if UserExist(email):
            retJson = {
                "status": 409,
                "msg": "the user already exists"
            }
            return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "Email": email,
            "Password": hashed_pw,
            "Sentence": ""
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }

        return jsonify(retJson)

    def get(self):
        postedData = request.get_json()

        email= postedData["email"]

        resp = users
        
        return jsonify(resp)

def verifyPw(email, password):
    if not UserExist(email):
        return False
        
    hashed_pw = users.find({
        "Email": email
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def UserExist(email):
    if users.find({"Email": email}).count() == 0:
        return False
    else:
        return True


class Function(Resource):
    def post(self):
        postedData = request.get_json()

        userID= postedData["userID"]
        description= postedData["description"]
        tags= postedData["tags"]
        functionName= postedData["functionName"]
        codeJS= postedData["codeJS"]
        codeRef= postedData["codeRef"]

        if functionExist(functionName):
            retJson = {
                "status": 409,
                "msg": "name of the funtion already exists"
            }
            return jsonify(retJson)

        functions.insert({
            "UserId": userID,
            "Description": description,
            "Tags": tags,
            "Name": functionName,
            "Code": codeJS,
            "Reference": codeRef
        })

        retJson = {
            "status": 200,
            "msg": "You successfully add a new function at the API"
        }

        return jsonify(retJson)

    def get(self):
        postedData = request.get_json()

        key = postedData["key"]
        value = postedData["value"]

        function = functions.find_one({key:value})

        if not function:
            retJson = {
                "status": 301,
                "msg": "Function dont found"
            }
            return jsonify(retJson)
        
        return toJson(function)

    def patch(self):
        pass

    def delete(self):
        pass

def functionExist(name):
    if functions.find({"Name": name}).count() == 0:
        return False
    else:
        return True

def getFunction(name):
    function = functions.find({"Name":name})
    return function

def findRef(references):
    if len(references) == 1:
        return references.code
    else:
        elem = references.pop()
        refCode = functions.find({"Name": elem})
        if len(refCode.Reference) > 0:
            findRef(refCode.Reference)
        

class ExportByURL(Resource):
    def get(self, id):
        function = functions.find({"_id": id})

        if not function:
            retJson = {
                "status": 301,
                "msg": "Function dont found"
            }
            return jsonify(retJson)

        refList = []

        if len(function.Reference) > 0:
            data={}
            for ref in function.Reference:
                refCode = functions.find({"Name": ref})
                data[ref] = refCode
            


        

api.add_resource(Register, '/register')
api.add_resource(Function, '/functions')
api.add_resource(ExportByURL, '/api.py?id=<int:id>')

if __name__=="__main__": 
    app.run(host='0.0.0.0')