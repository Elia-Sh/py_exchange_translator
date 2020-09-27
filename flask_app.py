from flask import Flask, request, jsonify

from py_exchange_translator import main as translator

app = Flask(__name__)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def root_route():
    result = None
    try:
        amount = request.args.get('amount', 0)
        currency = request.args.get('currency', None)
        result = translator(amount, currency)
    except Exception: 
        raise InvalidUsage('Unexpected Error; Syntax: [amount=<>, currency=<>]', status_code=410)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run()
