from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from datetime import datetime
from sqlalchemy import event

app = Flask(__name__, template_folder='templates')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

DOCUMENTATION_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Servo HTTP Server</title>
</head>
<body>
    <h1>Servo HTTP Server API Documentation</h1>

    <h2>/ (GET)</h2>
    <p>Returns the home page with information about the actions in the database.</p>
    <p>Returns a dictionary containing the total number of actions, details of the last action, details of all actions, and the current server time.</p>

    <h2>/switch-action (POST)</h2>
    <p>Switches the current action by creating a new Action object with the opposite 'is_activated' value.</p>
    <p>Returns a dictionary containing a message indicating the action switch and the details of the new action.</p>

    <h2>/init (GET)</h2>
    <p>Initializes the action database by creating a new Action object with 'is_activated' set to False.</p>
    <p>Returns a dictionary containing a message indicating the action initialization and the details of the new action.</p>

    <h2>/log (GET)</h2>
    <p>Returns a dictionary containing the total number of actions, details of the last action, details of all actions, and the current server time.</p>
</body>
</html>
"""


class Action(db.Model):
    """
    Represents an action in the database.

    Attributes:
        id (int): The unique identifier of the action.
        start_time (datetime): The start time of the action.
        is_activated (bool): Indicates whether the action is activated or not.
    """

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=True)
    is_activated = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        """
        Converts the Action object to a dictionary.

        Returns:
            dict: The Action object represented as a dictionary.
        """
        return {
            'id': self.id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'is_activated': self.is_activated
        }
    
with app.app_context():
    db.create_all()

@event.listens_for(Action.is_activated, 'set')
def on_is_activated_change(target, value, oldvalue, initiator):
    """
    Event listener for the 'is_activated' attribute of the Action class.

    Args:
        target (Action): The Action object being modified.
        value (bool): The new value of the 'is_activated' attribute.
        oldvalue (bool): The old value of the 'is_activated' attribute.
        initiator: The SQLAlchemy event initiator.

    Notes:
        This event listener is triggered whenever the 'is_activated' attribute of an Action object is modified.
        It prints a message indicating whether the servo is being activated or deactivated.
    """
    if value:
        pass
        #servo_hardware.move_servo()
    else:
        pass
        #servo_hardware.stop_servo()

@cross_origin()
@app.route('/switch-action', methods=['POST'])
def switch_action():
    """
    Switches the current action by creating a new Action object with the opposite 'is_activated' value.

    Returns:
        dict: A dictionary containing a message indicating the action switch and the details of the new action.
    """
    last_row = Action.query.order_by(Action.id.desc()).first()
    new_action = Action(is_activated=not last_row.is_activated, start_time=datetime.now())
    db.session.add(new_action)
    db.session.commit()
    return {
        "message": "Action switched",
        "action": new_action.to_dict()
    }

@cross_origin()
@app.route('/init', methods=['GET'])
def init_action_database():
    """
    Initializes the action database by creating a new Action object with 'is_activated' set to False.

    Returns:
        dict: A dictionary containing a message indicating the action initialization and the details of the new action.
    """
    new_action = Action(is_activated=False, start_time=datetime.now())
    db.session.add(new_action)
    db.session.commit()
    return {
        "message": "Action initialized",
        "action": new_action.to_dict()
    }

@cross_origin()
@app.route('/log')
def log():
    """
    Returns the home page with information about the actions in the database.

    Returns:
        dict: A dictionary containing the total number of actions, details of the last action, details of all actions,
              and the current server time.
    """
    actions = [action.to_dict() for action in Action.query.all()]
    return {
        "total_actions": Action.query.count(),
        "last_action": Action.query.order_by(Action.id.desc()).first().to_dict(),
        "actions": actions[::-1],
        "server_time": f"{datetime.now()}"
    }

@cross_origin()
@app.route('/')
def home():
    """
    Returns the home page with information about the actions in the database.

    Returns:
        dict: A dictionary containing the total number of actions, details of the last action, details of all actions,
              and the current server time.
    """
      # Update the template file name to 'home.html'
    return DOCUMENTATION_HTML

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    if not Action.query.first():
        init_action_database()