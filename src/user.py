from flask import Blueprint, jsonify
import config


user = Blueprint('user', __name__)

prefix = config.host_prefix + '/user'


@user.route('/api/user/create')
def create():
    return 'this is user create'
