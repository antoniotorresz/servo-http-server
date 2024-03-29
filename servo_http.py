from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import event
import servo_hardware

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

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
        servo_hardware.move_servo()
    else:
        servo_hardware.stop_servo()

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

@app.route('/')
def home():
    """
    Returns the home page with information about the actions in the database.

    Returns:
        dict: A dictionary containing the total number of actions, details of the last action, details of all actions,
              and the current server time.
    """
    return {
        "total_actions": Action.query.count(),
        "last_action": Action.query.order_by(Action.id.desc()).first().to_dict(),
        "actions": [action.to_dict() for action in Action.query.all()],
        "server_time": f"{datetime.now()}"
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    if not Action.query.first():
        init_action_database()