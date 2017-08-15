from flask import Blueprint
from flask import jsonify
from flask import request
from flask import g
from datetime import datetime
import MySQLdb
import config
import db_pw


prefix = config.host_prefix + '/user'
user_key = ['name', 'squad', 'auth']

user = Blueprint('user', __name__)


@user.before_request
def db_connect():
    g.conn = MySQLdb.connect(host=config.DB['host'],
                             user=config.DB['user'],
                             passwd=db_pw.DB_PW,
                             db=config.DB['db'])
    g.cursor = g.conn.cursor()


@user.after_request
def db_disconnect(response):
    g.cursor.close()
    g.conn.close()
    return response


def db_query(query, args=()):
    g.cursor.execute(query, args)
    g.conn.commit()
    data_rows = g.cursor.fetchall()
    rv = [dict((g.cursor.description[index][0], value)
          for index, value in enumerate(row))
          for row in data_rows]
    return rv if rv else None


@user.route(prefix + 'login')
def login():
    ret = {
        'object': 'user',
        'action': 'login',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }
    data = request.get_json()
    if data is None:
        return jsonify(ret), 400
    return jsonify(ret)
