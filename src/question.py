from flask import Blueprint, jsonify
from datetime import datetime
import config


qs = Blueprint('question', __name__)

prefix = config.host_prefix + '/question'

@qs.route(prefix+'/create')
def create():
    ret = {
        'Object':'question',
        'Action':'create',
        'Server_time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Payload':[]
    }
    return jsonify(ret)