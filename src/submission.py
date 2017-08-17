from flask import jsonify
from flask import Blueprint
from flask import g
from flask import request
from datetime import datetime
import MySQLdb
import config
import db_pw


sub = Blueprint('submission', __name__)

prefix = config.host_prefix + '/submission'


sub_required = ['uid', 'qid', 'code']
sub_optional = ['judge_status', 'judge_exetime', 'judge_exemem']

sub_keys = sub_required + sub_optional


@sub.before_request
def db_connect():
    g.conn = MySQLdb.connect(host=config.DB['host'],
                             user=config.DB['user'],
                             passwd=db_pw.DB_PW,
                             db=config.DB['db'])
    g.cursor = g.conn.cursor()


@sub.after_request
def db_disconnect(response):
    g.cursor.close()
    g.conn.close()
    return response


def db_query(query, args=(), one=False):
    g.cursor.execute(query, args)
    g.conn.commit()
    data_rows = g.cursor.fetchall()
    rv = [dict((g.cursor.description[index][0], value)
          for index, value in enumerate(row))
          for row in data_rows]
    return (rv[0] if rv else None) if one else rv


@sub.route(prefix + '/create', methods=['POST'])
def create():
    ret = {
        'object': 'submission',
        'action': 'create',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }

    data = request.get_json(force=False)

    if data is None:
        return jsonify(ret), 400

    value = []

    for i in range(len(sub_required)):
        try:
            value.append(data[sub_required[i]])
        except KeyError as err:
            print(err)
            return jsonify(ret), 400

    for i in range(len(sub_optional)):
        try:
            value.append(data[sub_optional[i]])
        except KeyError as err:
            print(err)
            value.append(None)

    query = "INSERT INTO `submission` (" + ','.join(sub_keys) + ")" + \
            "VALUES (" + ','.join(['%s'] * len(sub_keys)) + ')'

    try:
        db_ret = db_query(query, tuple(value), one=True)
        print(db_ret)
        return jsonify(ret), 201
    except MySQLdb.Error as err:
        print("MySQLdb Error:")
        print(err)
        return jsonify(ret), 500


@sub.route(prefix + '/read/uncompiled', methods=['GET'])
def readUncompiled():
    ret = {
        'object': 'submission',
        'action': 'readUncompiled',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }

    query_sel = 'SELECT * FROM `submission` WHERE `judge_status` = "CP"'
    query_udt = 'UPDATE `submission` ' + \
                "SET `judge_status`='CI' " + \
                'WHERE `submission`.`sid`='

    try:
        db_ret = db_query(query_sel, one=True)
        print("DataBase SELECT return :")
        print(db_ret)
        if db_ret is not None:
            ret['payload'] = [db_ret]
            query_udt += str(db_ret['sid'])
            db_ret = db_query(query_udt)
            print(db_ret)
        return jsonify(ret), 200
    except MySQLdb.Error as err:
        print("MySQLdb Error:")
        print(err)
        return jsonify(ret), 500


@sub.route(prefix + '/read/unjudged', methods=['GET'])
def readUnjudge():
    ret = {
        'object': 'submission',
        'action': 'readUnjudged',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }

    query_sel = 'SELECT * FROM `submission` WHERE `judge_status` = "JP"'
    query_udt = 'UPDATE `submission` ' + \
                "SET `judge_status`='JI' " + \
                'WHERE `submission`.`sid`='

    try:
        db_ret = db_query(query_sel, one=True)
        print("DataBase SELECT return :")
        print(db_ret)
        if db_ret is not None:
            ret['payload'] = [db_ret]
            query_udt += str(db_ret['sid'])
            db_ret = db_query(query_udt)
            print(db_ret)
        return jsonify(ret), 200
    except MySQLdb.Error as err:
        print("MySQLdb Error:")
        print(err)
        return jsonify(ret), 500


@sub.route(prefix + '/read', methods=['GET'])
def read():
    ret = {
        'object': 'submission',
        'action': 'read',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }

    data = request.get_json()
    print(data)
    if data is None:
        ''' read with no parameter, return ALL '''
        query = 'SELECT * FROM `submission` WHERE 1'
        db_ret = db_query(query)
        ret['payload'] = db_ret
        return jsonify(ret), 200
    if len(data) is not 1:
        ''' Mutiple parameters is not allowed '''
        return jsonify(ret), 400

    try:
        value = data['sid']
        query = 'SELECT * FROM `submission` WHERE `sid` = ' + str(value)
        try:
            db_ret = db_query(query)
            ret['payload'] = db_ret
            return jsonify(ret), 200
        except MySQLdb.Error as err:
            print(err)
            return jsonify(ret), 500

    except KeyError:
        pass

    try:
        value = data['uid']
        query = 'SELECT * FROM `submission` WHERE `uid` = ' + str(value)
        try:
            db_ret = db_query(query)
            ret['payload'] = db_ret
            return jsonify(ret), 200
        except MySQLdb.Error as err:
            print(err)
            return jsonify(ret), 500
    except KeyError:
        pass

    try:
        value = data['qid']
        query = 'SELECT * FROM `submission` WHERE `qid` = ' + str(value)
        try:
            db_ret = db_query(query)
            ret['payload'] = db_ret
            return jsonify(ret), 200
        except MySQLdb.Error as err:
            print(err)
            return jsonify(ret), 500
    except KeyError:
        pass

    return jsonify(ret), 400


@sub.route(prefix + '/update', methods=['PUT'])
def update():
    ret = {
        'object': 'submission',
        'action': 'update',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }

    data = request.get_json(force=False)
    print("Received data:")
    print(data)
    if data is None:
        return jsonify(ret), 400

    try:
        sid = data['sid']
    except KeyError as err:
        print(err)
        return jsonify(ret), 400

    keys = []
    values = []
    for i in range(len(sub_keys)):
        try:
            values.append(data[sub_keys[i]])
            keys.append(sub_keys[i])
        except KeyError as err:
            pass

    query = 'UPDATE `submission` SET '
    query += '=%s, '.join(keys) + '=%s '
    query += 'WHERE `submission`.`sid`=' + str(sid)
    print(query)
    try:
        db_ret = db_query(query, tuple(values))
        print(db_ret)
        return jsonify(ret), 200
    except MySQLdb.Error as err:
        print('MySQLdb error:')
        print(err)
        return jsonify(ret), 500
