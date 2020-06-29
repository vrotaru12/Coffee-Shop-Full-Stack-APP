import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
#MENTHOR SUGGESTION  
CORS(app)
#Security issues can arise from enabling CORS so this has to be done carefully..Please refer the below guide for best practices while implementing CORS.
#https://www.pivotpointsecurity.com/blog/cross-origin-resource-sharing-security/


@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type,Authorization,true')
    response.headers.add(
        'Access-Control-Allow-Methods',
        'GET,PATCH,POST,DELETE,OPTIONS')
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200


'''
@TODO implement endpoint
    POST /drinks
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    body = request.get_json()
    format_recipe = body['recipe']
    newtitle = body['title']

    try:
        if isinstance(format_recipe, dict):
            format_recipe = [format_recipe]
        newrecipe = json.dumps(format_recipe)
        new_drink = Drink(title=newtitle, recipe=newrecipe)
        new_drink.insert()
        return jsonify({'success': True, 'drinks': [new_drink.long()]})

    except BaseException:
        #MENTHOR SUGGESTION
        abort(422)
        #For better debugging purposes I would suggest use logging or sys.exc_info[].


'''
@TODO implement endpoint
    PATCH /drinks/<id>
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drinks(payload, drink_id):
    body = request.get_json()
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        if 'title' in body:
            drink.title = body.get('title')
        if 'recipe' in body:
            drink.recipe = json.dumps(body.get('recipe'))

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except BaseException:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200

    except BaseException:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
#MENTHOR SUGGESTION 
# You can also try to implement error handler500 - Internal Server Errorwhich also one of the most potential error.
# I'm attaching the link below to give you more context on error handling.
# https://flask.palletsprojects.com/en/1.1.x/reqcontext/#teardown-callbacks
