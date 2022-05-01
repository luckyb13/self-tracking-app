

from flask import Flask, render_template,request,redirect,url_for
import os
import requests
import matplotlib.pyplot as plt
from matplotlib import use
use('Agg')
from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with, marshal
from flask_sqlalchemy import SQLAlchemy

import datetime
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class User(db.Model):
    __tablename__ = 'user'
    user_id=db.Column(db.Integer,primary_key=True, autoincrement=True)
    user_name=db.Column(db.String(20),nullable=False)
    first_name=db.Column(db.String(20), nullable=False)
    last_name=db.Column(db.String(20))
    password=db.Column(db.String(20),nullable=False)
    def __repr__(self):
        return "<User %r>" %self.user_id

class Tracker(db.Model):
    __tablename__ = 'tracker'
    tracker_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_type=db.Column(db.String(100), nullable=False)
    tracker_name=db.Column(db.String(100),nullable=False)
    description=db.Column(db.String(100),nullable=False)
    settings= db.Column(db.String(100))
    user_id=db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def __repr__(self):
        return "<Tracker %r" %self.tracker_id

class Tracker_Numerical(db.Model):
    tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False)
    log_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow())
    tracker_value=db.Column(db.Float,nullable=False)
    tracker_note=db.Column(db.String(100))



class Tracker_boolean(db.Model):
    log_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False)
    tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow())
    tracker_value=db.Column(db.Boolean,nullable=False)
    tracker_note=db.Column(db.String(100))

'''class Tracker_time_duration(db.Model):
    tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False, primary_key=True)
    #user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
    tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow(), primary_key=True)
    tracker_value=db.Column(db.Integer,nullable=False)
    tracker_note=db.Column(db.String(100))
'''
#db.create_all()


class Tracker_multi_choice(db.Model):
    log_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False)
    #user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
    tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow())
    tracker_value=db.Column(db.String(50),nullable=False)
    tracker_note=db.Column(db.String(100))

#TRACKERS: CREATE: ARGS
trackers_post_args = reqparse.RequestParser()
trackers_post_args.add_argument("tracker_name", type=str, help="Name of the tracker is required", required=True)
trackers_post_args.add_argument("tracker_type", type=str, help="type  of the tracker is required", required=True)
trackers_post_args.add_argument("description", type=str, help="description of the tracker is required", required=True)
trackers_post_args.add_argument("settings", type=str)

#TRACKERS: UPDATE: ARGS
trackers_update_args = reqparse.RequestParser()
trackers_update_args.add_argument("tracker_name", type=str, help="Name of the tracker is required", required=True)
trackers_update_args.add_argument("description", type=str, help="description of the tracker is required", required=True)
trackers_update_args.add_argument("settings", type=str)

#LOGS, BOOLEAN: POST, PUT: ARGS
bool_args = reqparse.RequestParser()
#logs_post_args.add_argument("tracker_timestamp")
bool_args.add_argument("tracker_value", type=bool,  help="value of the tracker log is required", required=True)
bool_args.add_argument("tracker_note", type=str, help="note for the tracker log is required", required=True)

#LOGS, NUMERICAL: POST, PUT: ARGS
numerical_args = reqparse.RequestParser()
#logs_post_args.add_argument("tracker_timestamp")
numerical_args.add_argument("tracker_value", type=int,  help="value of the tracker log is required", required=True)
numerical_args.add_argument("tracker_note", type=str, help="note for the tracker log is required", required=True)

#LOGS, MULTICHOICE: POST, PUT: ARGS
multi_args = reqparse.RequestParser()
#logs_post_args.add_argument("tracker_timestamp")
multi_args.add_argument("tracker_value", type=str,  help="value of the tracker log is required", required=True)
multi_args.add_argument("tracker_note", type=str, help="note for the tracker log is required", required=True)

#TRACKER: GET: JSON
tracker_json = {
    'tracker_id': fields.Integer,
    'tracker_type': fields.String,
    'tracker_name': fields.String,
    'description': fields.String,
    'settings': fields.String,
    'user_id': fields.Integer
}

tracker_boolean_json= {
    'log_id': fields.Integer,
    'tracker_id': fields.Integer,
    'tracker_timestamp': fields.String,
    'tracker_value': fields.Boolean,
    'tracker_note': fields.String,
}
tracker_numerical_json= {
    'log_id': fields.Integer,
    'tracker_id': fields.Integer,
    'tracker_timestamp': fields.String,
    'tracker_value': fields.Integer,
    'tracker_note': fields.String,
}

tracker_multichoice_json= {
    'log_id': fields.Integer,
    'tracker_id': fields.Integer,
    'tracker_timestamp': fields.String,
    'tracker_value': fields.String,
    'tracker_note': fields.String,
}

BASE = "http://127.0.0.1:5000/"

#API: TRACKERS: CRUD

class Trackers(Resource):
#API: TRACKER: READ
    @marshal_with(tracker_json)
    def get(self, user_id ):
        allT= Tracker.query.filter_by(user_id=user_id).all()
        return allT
#API: TRACKER: CREATE
    #@marshal_with(resource_fields)
    def post(self, user_id):
        args = trackers_post_args.parse_args()
        newT = Tracker(user_id= user_id, tracker_name=args['tracker_name'], tracker_type=args['tracker_type'], description=args['description'])
        db.session.add(newT)
        db.session.commit()
        return {0:'good'}

api.add_resource(Trackers, "/<int:user_id>/trackers")

#API: TRACKER: UPDATE
class Tracker_manipulate(Resource):
    def put(self, user_id, tracker_id ):
        args = trackers_update_args.parse_args()
        trackerUpdate= Tracker.query.filter_by(tracker_id= tracker_id).update(dict(tracker_name= args['tracker_name'], description= args['description']))
        db.session.commit()
        return 'succesfully updated'

#API: TRACKER: DELETE
    #@marshal_with(resource_fields)
    def delete(self, user_id, tracker_id):
        Tracker.query.filter_by(tracker_id= tracker_id).delete()
        db.session.commit()
        return 'sucessfully deleted'
api.add_resource(Tracker_manipulate, "/<int:user_id>/tracker/<int:tracker_id>")

type_dict= {'numerical': Tracker_Numerical, 'multiple_choice': Tracker_multi_choice, 'boolean': Tracker_boolean, 'time_duration':Tracker_Numerical }
logs_json_dict= {'numerical': tracker_numerical_json, 'multiple_choice': tracker_multichoice_json, 'boolean': tracker_boolean_json, 'time_duration':tracker_numerical_json }

logType= {Tracker_Numerical: numerical_args, Tracker_multi_choice: multi_args, Tracker_boolean: bool_args}

#API: LOGS: CRUD
#API: LOG: READ, CREATE
class Tracker_logs(Resource):
    def get(self, user_id, tracker_id):
        tType= Tracker.query.filter_by(tracker_id=tracker_id).first().tracker_type
        logClass=type_dict[tType]
        tLogs=logClass.query.filter_by(tracker_id=tracker_id).all()
        return  marshal(tLogs, logs_json_dict[tType])

    def post(self, user_id, tracker_id):
        tType= Tracker.query.filter_by(tracker_id=tracker_id).first().tracker_type
        logClass=type_dict[tType]
        args = logType[logClass].parse_args()
        newLog = logClass(tracker_id=tracker_id, tracker_value=args['tracker_value'], tracker_note=args['tracker_note'])
        db.session.add(newLog)
        db.session.commit()
        return 'new log added '
api.add_resource(Tracker_logs, "/<int:user_id>/<int:tracker_id>/tracker_logs")

#API: LOGS: UPDATE
class log_manipulate(Resource):

    #@marshal_with(logs_json_dict[tType])
    def put(self, user_id, tracker_id, log_id):
        tType= Tracker.query.filter_by(tracker_id=tracker_id).first().tracker_type
        logClass=type_dict[tType]
        args = logType[logClass].parse_args()
        logUpdate=logClass.query.filter_by(tracker_id=tracker_id, log_id=log_id).update(dict(tracker_value=args['tracker_value'], tracker_note=args['tracker_note']))
        db.session.commit()

        return 'tracker_log updated'

#API: LOGS: DELETE
#@marshal_with(resource_fields)
    def delete(self, user_id, tracker_id, log_id):
        tType= Tracker.query.filter_by(tracker_id=tracker_id).first().tracker_type
        logClass=type_dict[tType]
        logClass.query.filter_by(log_id=log_id).delete()
        db.session.commit()
        return 'tracker_log deleted'

api.add_resource(log_manipulate, "/<int:user_id>/<int:tracker_id>/tracker_log/<int:log_id>")

#route landing page
@app.route('/')
def land():
    return render_template('landing.html')
#ROUTE: LOGIN
@app.route('/login', methods= ["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('login1.html')
    if request.method == "POST":
        un, pw= request.form['u_name'], request.form['pswd']
        userInfo= User.query.filter_by(user_name= un, password= pw).first()
        uid= userInfo.user_id
        #return 'logPost'
        #return str(uid)
        return redirect(f'/{uid}/{un}/dashboard')
#@app.route('/login', methods= ["GET", "POST"])

#ROUTE: REGISTER
@app.route('/register', methods= ["GET", "POST"] )
def register():
    if request.method == "POST":
        un, fn= request.form['u_name'], request.form['f_name']
        ln, pw= request.form['l_name'], request.form['pswd']
        addUser= User(user_name=un, first_name=fn, last_name=ln, password=pw)
        db.session.add(addUser)
        db.session.commit()
        return redirect('/login')
        #return render_template('dashboard.html')
    if request.method == "GET":
       return render_template('register1.html')

#ROUTES: TRACKER CRUD
#ROUTE: TRACKER READ
@app.route('/<int:user_id>/<user_name>/dashboard')
def dash(user_id, user_name):
    tList = requests.get(BASE + str(user_id)+ "/trackers", {'tracker_type': 'Boolean', 'tracker_name': 'helping', 'description': 'counting days of helping '})
    tDict= tList.json()
    l= []
    for r in tDict:
        tid= r['tracker_id']
        tid=str(tid)

        tlog= requests.get(f"{BASE}{user_id}/{tid}/tracker_logs")
        tlogDict= tlog.json()
        if(len(tlogDict)>0):
            for i in tlogDict:
                l.append(i['tracker_timestamp'])
    j=0
    for i in tDict:
        if(len(l)>j):
            s=l[j].split(' ')
            i['logs']= s[0]
            j+=1
        else:
            i['logs']= 'No logs found'
    # print(tDict)
    #return str(len(tDict))
    return render_template('dashboard.html', tDict=tDict, user_name=user_name, user_id= user_id)

#ROUTE: TRACKER CREATE
@app.route('/<int:user_id>/<user_name>/add_tracker', methods= ["GET","POST"])
def addT(user_id, user_name):
    if request.method == 'POST':
        tn, td= request.form['tName'], request.form['tDesc']
        tt= request.form['ttypes']
        requests.post(BASE + str(user_id)+ "/trackers", {'tracker_type': tt, 'tracker_name': tn, 'description': td})

        return redirect(f'/{user_id}/{user_name}/dashboard')
    elif request.method == 'GET':
        return render_template('add-tracker.html', user_name=user_name, user_id= user_id)

#ROUTE: TRACKER UPDATE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/update_tracker' , methods= ["GET","POST"])
def upT(user_id, user_name, tracker_id):
    #return render_template('update1.html' , user_name=user_name, user_id= user_id, tracker_id= tracker_id)
    if request.method == 'POST':
       tn, td= request.form['tName'], request.form['tDesc']
       requests.put(BASE + str(user_id)+ "/tracker/" +str(tracker_id), {'tracker_name': tn, 'description': td })
       return redirect(f'/{user_id}/{user_name}/dashboard')
    elif request.method == 'GET':
        t=Tracker.query.filter_by(tracker_id=tracker_id).first()
        tn= t.tracker_name
        td= t.description
        t= t.tracker_type
        return render_template('update-tracker.html' , user_name=user_name, user_id= user_id, tracker_id= tracker_id, tn= tn, td= td, t= t)

#ROUTE: TRACKER DELETE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/delete_tracker')
def delT(user_id, user_name, tracker_id):
    requests.delete(BASE + str(user_id) +"/tracker/"+ str(tracker_id))
    return redirect(f'/{user_id}/{user_name}/dashboard')


#TRACKER LOGS: CRUD,  ROUTES
#READ LOGS, ROUTES
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/tracker_logs', methods= ["GET","POST"])
def viewT(user_id, user_name, tracker_id, tracker_name):
    logL= requests.get(BASE + str(user_id)+"/" + str(tracker_id)+ "/tracker_logs")
    logListJson= logL.json()
    response = requests.get(f"{BASE}{str(user_id)}/trackers")
    td= response.json()
    s=""
    for r in td:
        if r['tracker_id']== tracker_id:
            tt= r['tracker_type']
            s=tt
    tracker_values=[]
    # print(s)
    tracker_logss=[]
    for i in logListJson:
        ts= i['tracker_timestamp']
        tk= ts.split(' ')
        # print(tk[0])
        tracker_logss.append(tk[0])
        tracker_values.append(i['tracker_value'])
    # print(tracker_log)
    plt.clf()
    plt.scatter(tracker_logss, tracker_values)
    plt.savefig('./static/hist1.png')

    return render_template('view-tracker.html', user_id= user_id, user_name=user_name, tracker_id= tracker_id, tracker_name=tracker_name, logListJson= logListJson,tracker_type= s)

#ADD A LOG, ROUTE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/add_log', methods= ["GET","POST"])
def addLog(user_id, user_name, tracker_id, tracker_name):
    #response = requests.post(BASE + user_id+"/" +tracker_id +"/tracker_logs", {'tracker_value':True, 'tracker_note':'new log'})
    if request.method == 'POST':
       val, nts= request.form['value'], request.form['notes']
       requests.post(BASE + str(user_id) +"/" +str(tracker_id)+ "/tracker_logs", {'tracker_value':val, 'tracker_note':nts})
       return redirect(f'/{user_id}/{user_name}/{tracker_id}/{tracker_name}/tracker_logs')
    elif request.method == 'GET':
       return render_template('add-logs.html', user_id= user_id, user_name=user_name, tracker_id= tracker_id, tracker_name=tracker_name)

#UPDATE A LOG, ROUTE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/<int:log_id>/update_log' , methods= ["GET","POST"])
def updateLog(user_id, user_name, tracker_id, log_id, tracker_name):
    #return 'hi'
    if request.method == 'POST':
       val, nts= request.form['value'], request.form['notes']
       requests.put(f'{BASE}{user_id}/{tracker_id}/tracker_log/{log_id}', {'tracker_value':val, 'tracker_note':nts})
       return redirect(f'/{user_id}/{user_name}/{tracker_id}/{tracker_name}/tracker_logs')
    elif request.method == 'GET':
        response = requests.get(f"{BASE}{user_id}/{tracker_id}/tracker_logs")
        tlogs=response.json()
        for r in tlogs:
            if r['log_id']== log_id:
               lv= r['tracker_value']
               ln= r['tracker_note']
               ltime= r['tracker_timestamp']
        return render_template('update-log.html', user_id= user_id, user_name=user_name, tracker_id= tracker_id, tracker_name=tracker_name, log_id=log_id, lv=lv, ln=ln, ltime=ltime)

#DELETE A LOG, ROUTE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/<int:log_id>/delete_log', methods= ["GET","POST"])
def deleteLog(user_id, user_name, tracker_id, log_id, tracker_name ):
    requests.delete(BASE + str(user_id)+"/" + str(tracker_id)+ "/tracker_log/"+ str(log_id))
    return redirect(f'/{user_id}/{user_name}/{tracker_id}/{tracker_name}/tracker_logs')



if __name__ == '__main__':
    app.run( debug=True)

