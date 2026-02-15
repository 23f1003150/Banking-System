from flask import Flask, jsonify
from flask_cors import CORS # cross-origin resource sharing for which frontend use which backend
from flask_security import Security
from flask_restful import Api

from controllers.database import db
from controllers.user_datastore import user_datastore
#from controllers.config import Config

def create_app():
    app = Flask(__name__)
    #CORS(app) Enable CORS for all routes and origins

    app.config.from_object('controllers.config.Config') 
    db.init_app(app) 
    security = Security(app, user_datastore)
    api = Api(app, prefix='/api') # for creating RESTful APIs
    
    with app.app_context():
        db.create_all()
        
        admin_role = user_datastore.find_or_create_role(name="Admin", description="with all permissions")
        staff_role = user_datastore.find_or_create_role(name="Staff", description="with limited permissions")
        user_role = user_datastore.find_or_create_role(name="User", description="User Of Application")
        
        if not user_datastore.find_user(email="admin@bank.com"):
            user_datastore.create_user(name="Adminstration", email="admin@bank.com",
                                       password="admin123", 
                                       roles=[admin_role])
            
        if not  user_datastore.find_user(email="staff@bank.com"):
            user_datastore.create_user(name="Staff", email="staff@bank.com",
                                       password="staff123", 
                                       roles=[staff_role])
            
        if not  user_datastore.find_user(email="user@bank.com"):
            user_datastore.create_user(name="User", email="user@bank.com",
                                       password="user123", 
                                       roles=[user_role])
        db.session.commit()
            
    return app, api

app, api = create_app()

CORS(app, origins=[ #Only my frontend (Vue on port 5173) can access APIs Other websites are blocked
    "http://localhost:5173",
    "http://127.0.0.1:5173"
])



@app.route('/')
def hello():
    data = {
        "message": "Hello,Welcome to Flask API!"
    }
    return jsonify(data), 200

@app.route('/api/welcome', methods=['GET'])
def welcome():
    data ={
        "message": "Welcome to the Bank Of Rishav"
    }
    return jsonify(data), 200

from controllers.authentication import CheckEmailApi, LoginAPI, LogoutAPI, RegisterAPI
api.add_resource(LoginAPI, '/login')
api.add_resource(CheckEmailApi, '/check-email')
api.add_resource(LogoutAPI, '/logout')
api.add_resource(RegisterAPI, '/register')

from controllers.content import AccountCRUD
api.add_resource(AccountCRUD, '/accounts', '/accounts/<int:account_id>')



if __name__ == "__main__":
    app.run(debug=True)