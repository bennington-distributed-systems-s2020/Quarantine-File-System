from flask import Flask, request, Response, json, abort
#from werkzeug.utils import secure_filename
import logging
logging.basicConfig(level=logging.DEBUG)

import master_interact

app = Flask(__name__)

@app.route("/")
def example():
    return "Chunkserver Flask API!"

@app.route("/create/<chunk_handle>/<mutation>/<data>")
def create(chunk_handle, mutation, data):
    lease = lease(chunk_handle)
    chunk_file = {}
    chunk_file["chunk"] = []
    chunk_file["chunk"].append({
            "name" : chunk_handle,
            "mutable" : mutation,
            "lease" : lease,
            "ISO date_time" : lease_time.isoformat(),
            "data" : data
    })
    with open(chunk_handle + '.txt', 'w') as chunk_file:
        json.dump(chunk, chunk_file)
        if json.load(chunk_file):
                success = 1
        else:
                success = 0
    return success

#lease: check whether a chunk has a lease or not
@app.route("/lease", strict_slashes=False, methods=['GET', 'POST'])
def lease():
    request_json = request.get_json()
    try:
        return json.dumps(master_interact.lease(request_json['chunk_handle']))
    except (KeyError, IOError, OSError) as e:
        #information on logging found here
        #https://www.scalyr.com/blog/getting-started-quickly-with-flask-logging/
        app.logger.warning("File {0} not found.".format(request_json['chunk_handle']))
        abort(400)
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

#chunk-inventory: returns information for a random subset of chunk
@app.route("/chunk-inventory/", strict_slashes=False, methods=['GET', 'POST'])
def chunk_inventory():
    try:
        return json.dumps(master_interact.chunk_inventory())
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

#collect-garbage: delete the chunks listed
@app.route("/collect-garbage/", strict_slashes=False, methods=['GET', 'POST'])
def collect_garbage():
    request_json = request.get_json()
    try:
        return json.dumps(master_interact.collect_garbage(request_json['deleted_chunks']))
    except (KeyError, IOError, OSError) as e:
        abort(400)
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

@app.route("/lease-request/", strict_slashes=False, methods=['GET', 'POST'])
def lease_request():
    abort(501)
    return""

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
