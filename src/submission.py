from flask import Blueprint, jsonify
import config


sub = Blueprint('submission', __name__)

prefix = config.host_prefix + '/submission'

@sub.route('/api/submission/create')
def create():
	return 'this is submission create'