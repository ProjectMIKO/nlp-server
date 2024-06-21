from flask import Flask, request
from flask_cors import CORS
from nlp_keyword.controller import keyword
from stt.controller import stt

import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.before_request
def handle_options_request():
    if request.method == 'OPTIONS':
        return '', 200


app.register_blueprint(keyword, url_prefix='/api/keyword')
app.register_blueprint(stt, url_prefix='/api/stt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
