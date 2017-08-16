from flask import Blueprint
from flask import jsonify
from flask import request
from flask import g
from datetime import datetime
import MySQLdb
import requests
import config
import db_pw


prefix = config.host_prefix + '/user'

user_key = ['uid', 'name', 'squad', 'email', 'password', 'last_login', 'auth']

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


def db_query(sql, args=()):
    g.cursor.execute(sql, args)
    g.conn.commit()
    data_rows = g.cursor.fetchall()
    rv = [dict((g.cursor.description[index][0], value)
          for index, value in enumerate(row))
          for row in data_rows]
    return rv if rv else None


@user.route(prefix + 'login', methods=['POST'])
def login():
    ret = {
        'object': 'user',
        'action': 'login',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }
    data = request.get_json()
    print(data)
    if data is None:
        return jsonify(ret), 400
    try:
        email = data['email']
        passwd = data['password']
    except KeyError as err:
        print(err)
        return jsonify(ret), 400

    # login eeccamp
    send_data = {"token": db_pw.token, "email": email, "id": passwd}
    try:
        r = requests.get(config.ee_url + '/api/auth.php', send_data)
    except requests.exceptions.RequestException as err:
        print(err)
        return jsonify(ret), 500

    user = {"email": email, "password": passwd}
    try:
        user['auth'] = r.text['auth']
        if user['auth'] is 10:
            user['uid'] = r.text['rid']
            user['name'] = r.text['name_chn']
            user['squad'] = r.text['squad']
        else:
            user['uid'] = r.text['uid'] + '0000'
            user['name'] = r.text['name']
            user['squad'] = r.text['squad']
    except KeyError as err:
        print(err)
        return jsonify(ret), 500

    # insert db
    value = []
    for i in range(len(user_key)):
        try:
            value.append(user[user_key[i]])
        except KeyError as err:
            value.append(None)

    sql = 'INSERT INTO user (' + ', '.join(user_key) + ')'
    sql += 'VALUES (' + ', '.join(['%s'] * len(user_key)) + ')'

    try:
        user['token'] = r.text['token']
    except KeyError as err:
        print(err)
        return jsonify(ret), 500

    try:
        db_query(sql, tuple(value))
        ret['payload'] = [user]
        return jsonify(ret), 201
    except MySQLdb.Error as err:
        print(err)
        return jsonify(ret), 500


@user.route(prefix + 'read', methods=['GET'])
def read():
    ret = {
        'object': 'user',
        'action': 'read',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }
    data = request.get_json()
    print(data)
    if data is None:
        try:
            sql = 'SELECT * FROM question'
            payload = db_query(sql)
            ret['payload'] = payload
            return jsonify(ret), 200
        except MySQLdb.Error as err:
            print(err)
            return jsonify(ret), 500

    try:
        sql = 'SELECT * FROM question WHERE uid = ' + str(data['uid'])
        payload = db_query(sql)
        ret['payload'] = payload
        return jsonify(ret), 200
    except KeyError:
        return jsonify(ret), 400
    except MySQLdb.Error as err:
        print(err)
        return jsonify(ret), 500


@user.route(prefix + 'update', methods=['PUT'])
def update():
    ret = {
        'object': 'user',
        'action': 'update',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }
    data = requests.get_json()
    if data is None:
        return jsonify(ret), 400
    try:
        uid = data['uid']
    except KeyError as err:
        print(err)
        return jsonify(ret), 400

    key = []
    value = []
    for i in range(len(user_key)):
        try:
            value.append(data[user_key[i]])
            key.append(user_key[i])
        except KeyError as err:
            pass

    sql = 'UPDATE user SET '
    sql += '=%s, '.join(key) + '=%s '
    sql += 'WHERE uid = ' + uid

    try:
        db_query(sql, tuple(value))
        return jsonify(ret), 200
    except MySQLdb.Error as err:
        print(err)
        return jsonify(ret), 500


@user.route(prefix + 'create', methods=['POST'])
def create():
    pass
