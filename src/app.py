from flask import Flask
from submission import sub
from question import qs
from user import user
import config


app = Flask(__name__)
app.register_blueprint(sub)
app.register_blueprint(qs)
app.register_blueprint(user)


@app.route('/')
def index():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(host=config.host, port=config.port, debug=True)
