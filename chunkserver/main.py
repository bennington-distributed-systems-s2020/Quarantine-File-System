from flask import Flask
from flask import request
from flask import Response
from flask import json
#from werkzeug.utils import secure_filename

import master_interact

app = Flask(__name__)

@app.route("/")
def example():
	return "Chunkserver Flask API!"

@app.route("/create")
def create():
	abort(501)
	return ""

@app.route("/lease", strict_slashes=False, methods=['POST'])
def lease():
    try:
        return json.dumps(master_interact.lease(request.form['chunk_handle']))
    except (KeyError, IOError) as e:
        return Response("400 Bad Request. chunk_handle not found. Exception:\n" + str(e), status=400)
    except Exception as e:
        return Response("Server Error. Exception:\n" + str(e), status=500)

@app.route("/chunk-inventory/", methods=['GET', 'POST'])
def chunk_inventory():
    try:
        return json.dumps(master_interact.chunk_inventory())
    except Exception as e:
        raise(e)
        return Response("Server Error. Exception:\n" + str(e), status=500)

@app.route("/collect-garbage/", methods=['POST'])
def collect_garbage():
	abort(501)
	if request.method == 'POST':
		f = request.files['deleted_chunks']
		f.save('deleted_chunks' + secure_filename(f.filename) + '.json')
	return ""

@app.route("/read") #/<int:chunk_handle>,<int:start_byte>,<int:byte_range>
def read():#chunk_handle, start_byte, byte_range):
	abort(501)
	return ""

@app.route("/append")
def append():
	abort(501)
	return ""

@app.route("/append-request")
def append_request():
	abort(501)
	return ""
