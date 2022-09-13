from flask import Flask, abort, jsonify, request
from flask_restful import (
    Api,
    Resource,
    reqparse,
    inputs,
    marshal_with,
    fields
)
from flask_sqlalchemy import SQLAlchemy
import datetime
import sys

app = Flask(__name__)
db = SQLAlchemy(app)

api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calender.db'

resource_data = {
    'id': fields.Integer,
    'event': fields.String,
    'date': fields.String
}


class Calender(db.Model):
    __tablename__ = 'calender'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()

parser = reqparse.RequestParser()
parser1 = reqparse.RequestParser()

parser.add_argument(
    'event',
    type=str,
    help='The event name is required!',
    required=True
)
parser.add_argument(
    'date',
    type=inputs.date,
    help='The event date with the correct format is required! The correct format is YYYY-MM-DD!',
    required=True
)

parser1.add_argument(
    'start_time',
    type=inputs.date,
)
parser1.add_argument(
    'end_time',
    type=inputs.date,
)


class GetResource(Resource):
    @marshal_with(resource_data)
    def get(self, **kwargs):
        cal = Calender.query.filter(Calender.date == datetime.date.today()).all()
        return cal


class PostResource(Resource):
    @marshal_with(resource_data)
    def get(self, **kwargs):
        try:
            val = request.args.get('start_time') and request.args.get('end_time')
        except:
            val = False
        if val:
            data = parser1.parse_args()
            cal = Calender.query.filter(
                Calender.date.between(data['start_time'], data['end_time'])
            ).all()
        else:
            cal = Calender.query.all()
        return cal

    def post(self):
        data = parser.parse_args()
        cal = Calender(**data)
        db.session.add(cal)
        db.session.commit()
        return {
            'message': 'The event has been added!',
            'event': data['event'],
            'date': str(data['date'].date())
        }


class EventByID(Resource):

    @marshal_with(resource_data)
    def get(self, event_id):
        event = Calender.query.filter(Calender.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event

    def delete(self, event_id):
        event = Calender.query.filter(Calender.id == event_id)
        print(event.first())
        if event.first() is None:
            abort(404, "The event doesn't exist!")
        else:
            event.delete()
            db.session.commit()
            return jsonify(
                {
                    "message": "The event has been deleted!"
                }
            )


api.add_resource(PostResource, '/event')
api.add_resource(GetResource, '/event/today')
api.add_resource(EventByID, '/event/<int:event_id>')


# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
