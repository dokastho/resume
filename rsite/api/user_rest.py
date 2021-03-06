"""
Site user rest api.

URLs include:
/api/v1/user/
"""

import flask
import rsite
from rsite.model import rest_api_auth_user, get_db

@rsite.app.route("/api/v1/user/", methods=['GET'])
def current_user():
    """Return the logname of the current user."""

    logname, database = rest_api_auth_user()
    
    cur = database.execute(
        "SELECT * "
        "FROM users "
        'WHERE username == ?',
        (logname, )
    )
    
    data = cur.fetchone()

    if data is None:
        flask.abort(500)
    
    return flask.jsonify(data), 201


@rsite.app.route("/api/v1/user/taken/", methods=['GET'])
def username_taken():
    """Return true if user exists."""
    
    username = flask.request.args.get("username", type=str, default='')
    
    database = get_db()
    
    cur = database.execute(
        "SELECT * "
        "FROM users "
        'WHERE username == ?',
        (username, )
    )
    
    user = cur.fetchall()

    data = {
        "valid": len(user) == 0,
    }
    return flask.jsonify(data), 201