from flask import Blueprint
from flask import jsonify
from flask import request
from flask import g
from datetime import datetime
import MySQLdb
import config
import db_pw


prefix = config.host_prefix + '/question'
qs_required = ['title', 'content', 'content_input', 'content_output',
               'example_output', 'judge_output', 'limit_time',
               'limit_mem']
qs_optional = ['example_input', 'judge_input', 'hint', 'tag', 'source']
qs_key = qs_required + qs_optional

qs = Blueprint('question', __name__)


@qs.before_request
def db_connect():
    g.conn = MySQLdb.connect(host=config.DB['host'],
                             user=config.DB['user'],
                             passwd=db_pw.DB_PW,
                             db=config.DB['db'])
    g.cursor = g.conn.cursor()


@qs.after_request
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


@qs.route(prefix + '/create', methods=['POST'])
def create():
    ret = {
        'object': 'question',
        'action': 'create',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }
    data = request.get_json()
    # check for all
    if data is None:
        return jsonify(ret), 400

    value = []
    for i in range(len(qs_required)):
        try:
            value.append(data[qs_required[i]])
        except KeyError as err:
            print(err)
            return jsonify(ret), 400

    for i in range(len(qs_optional)):
        try:
            value.append(data[qs_optional[i]])
        except KeyError:
            value.append(None)

    query = 'INSERT INTO question (' + ','.join(qs_key) + ')'
    query += 'VALUES (' + ', '.join(['%s'] * len(qs_key)) + ')'

    try:
        db_query(query, tuple(value))
        ret['payload'] = [{'sid': g.cursor.lastrowid}]
        return jsonify(ret), 201
    except MySQLdb.Error as err:
        print('MySQL Error:', err)
        return jsonify(ret), 500


@qs.route(prefix + '/read', methods=['GET'])
def read():
    ret = {
        'object': 'question',
        'action': 'read',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }
    data = request.get_json()
    print(data)
    if data is None:
        try:
            query = 'SELECT * FROM question'
            payload = db_query(query)
            ret['payload'] = payload
            return jsonify(ret), 200
        except MySQLdb.Error as err:
            print('MySQL Error:', err)
            return jsonify(ret), 500

    try:
        query = 'SELECT * FROM question WHERE qid = ' + str(data['qid'])
        payload = db_query(query)
        ret['payload'] = payload
        return jsonify(ret), 200
    except KeyError:
        return jsonify(ret), 400
    except MySQLdb.Error as err:
        print('MySQL Error', err)
        return jsonify(ret), 500


@qs.route(prefix + '/update', methods=['PUT'])
def update():
    ret = {
        'object': 'question',
        'action': 'update',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }
    data = request.get_json()
    if data is None:
        return jsonify(ret), 400

    value = []
    for i in range(len(qs_required)):
        try:
            value.append(data[qs_required[i]])
        except KeyError as err:
            print(err)
            return jsonify(ret), 400

    for i in range(len(qs_optional)):
        try:
            value.append(data[qs_optional[i]])
        except KeyError:
            value.append(None)

    query = 'UPDATE question SET '
    query += '=%s, '.join(qs_key) + '=%s '
    query += 'WHERE qid = ' + str(data['qid'])

    try:
        db_query(query, tuple(value))
        return jsonify(ret), 201
    except MySQLdb.Error as err:
        print('MySQL Error:', err)
        return jsonify(ret), 500


@qs.route(prefix + '/delete', methods=['DELETE'])
def delete():
    ret = {
        'object': 'question',
        'action': 'delete',
        'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'payload': []
    }
    data = request.get_json()
    if data is None:
        return jsonify(ret), 400
    try:
        query = 'DELETE FROM question WHERE qid = ' + str(data['qid'])
        payload = db_query(query)
        sub_query = 'DELETE FROM submission WHERE qid = ' + str(data['qid'])
        payload = db_query(sub_query)
        ret['payload'] = payload
        return jsonify(ret), 200
    except KeyError:
        return jsonify(ret), 400
    except MySQLdb.Error as err:
        print('MySQL Error', err)
        return jsonify(ret), 500
