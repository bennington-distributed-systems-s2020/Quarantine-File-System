from flask import Flask, request, Response, json, abort
#from werkzeug.utils import secure_filename

import logging
logging.basicConfig(level=logging.DEBUG)

import base64

import master_interact, append_funcs

with open("config.json") as config_json:
    config = json.load(config_json)

app = Flask(__name__)

@app.route("/")
def example():
    return "Chunkserver Flask API!"

@app.route("/create/", strict_slashes=False, methods=['GET', 'POST'])
def create():
    request_json = request.get_json()
    try:
        chunk_handle = request_json['chunk_handle']
            #chunk_file = {}
            #chunk_file["chunk"] = []
            #chunk_file["chunk"].append({
            #        "name" : chunk_handle,
            #        "mutable": 0,
            #	"lease": 0,
            #	"ISO_lease_time": 00000000,
            #	"lease_time":00000000
            #})
        with open(config["CHUNK_PATH"] + chunk_handle + '.chunk', 'wb') as chunk:
            chunk.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        return app.response_class(json.dumps(True), content_type='application/json')
    except (KeyError, IOError, OSError) as e:
        app.logger.warning("File {0} not found.".format(request_json['chunk_handle']), exc_info = True)
        abort(400)
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

#lease: check whether a chunk has a lease or not
@app.route("/lease", strict_slashes=False, methods=['GET', 'POST'])
def lease():
    request_json = request.get_json()
    try:
        #returning a value with json
        #https://stackoverflow.com/questions/35133318/return-bool-as-post-response-using-flask
        return app.response_class(json.dumps(master_interact.lease(request_json['chunk_handle'])),
                                  content_type='application/json')
    except (KeyError, IOError, OSError) as e:
        #information on logging found here
        #https://www.scalyr.com/blog/getting-started-quickly-with-flask-logging/
        app.logger.warning("File {0} not found.".format(request_json['chunk_handle']), exc_info = True)
        abort(400)
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

#chunk-inventory: returns information for a random subset of chunk
@app.route("/chunk-inventory/", strict_slashes=False, methods=['GET', 'POST'])
def chunk_inventory():
    try:
        return app.response_class(json.dumps(master_interact.chunk_inventory()),
                                  content_type='application/json')
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

#collect-garbage: delete the chunks listed
@app.route("/collect-garbage/", strict_slashes=False, methods=['GET', 'POST'])
def collect_garbage():
    request_json = request.get_json()
    try:
        return app.response_class(json.dumps(master_interact.collect_garbage(request_json['deleted_chunks'])),
                                 content_type='application/json')
    except (KeyError, IOError, OSError) as e:
        abort(400)
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

#lease_grant: grants a lease to a chunk
#for now I will just update the chunk_handle and timestamp information.
#Replicas are important for appends, so how that is stored is dependent on how
#append is implemented as well
@app.route("/lease-grant/", strict_slashes=False, methods=['GET', 'POST'])
def lease_grant():
    request_json = request.get_json()
    try:
        return app.response_class(json.dumps(master_interact.lease_grant(request_json['chunk_handle'],
                                                                     request_json['timestamp'],
                                                                     request_json['replica'])),
                                  content_type='application/json')
    except (KeyError, IOError, OSError) as e:
        app.logger.warning("File {0} not found.".format(request_json['chunk_handle']), exc_info = True)
        abort(400)
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

@app.route("/read/", strict_slashes=False, methods=['GET', 'POST'])
def read():
    request_json = request.get_json()
    try:
        chunk_handle = request_json['chunk_handle']
        start_byte = request_json['start_byte']
        byte_range = request_json['byte_range']
        b64_encoded_return_bytes = ""

        with open(config["CHUNK_PATH"] + chunk_handle + '.chunk') as c_file:
            c_file.seek(start_byte + 9) #9 first information bytes
            return_bytes = c_file.read(byte_range)
            b64_encoded_return_bytes = base64.b64encode(return_bytes).decode()
            #json_data = json.load(chunk_data)
            #return_list = []
            #for x in range(0, byte_range):
            #        python_data = json_data.readline()
            #        return_list.append(python_data)

        return app.response_class(json.dumps(b64_encoded_return_bytes))
    except (KeyError, IOError, OSError) as e:
        app.logger.warning("File {0} not found.".format(request_json['chunk_handle']), exc_info = True)
        abort(400)
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

@app.route("/append", strict_slashes=False, methods=['GET', 'POST'])
def append():
    # save the chunk_handle and bytes from the POST request's JSON
    request_json = request.get_json()
    try:
        #Q: wrapped the class in another file to make it look cleaner
        #Q: also renamed the 2nd parameter to "data" because bytes was a built-in type
        return app.response_class(json.dumps(append_funcs.append(request_json['chunk_handle'], request_json['data'])),
                                 content_type='application/json')
    except (KeyError, IOError, OSError) as e:
        app.logger.warning("File {0} not found.".format(request_json['chunk_handle']), exc_info = True)
        abort(400)
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

@app.route("/append-request", strict_slashes=False, methods=['GET', 'POST'])
def append_request():
    # use the chunk_handle to write the buffer to the File
    # send append_request to Replicas
    # return int
    request_json = request.get_json()
    try:
        return app.response_class(json.dumps(append_funcs.append_request(request_json['chunk_handle'])),
                                 content_type='application/json')
    except (KeyError, IOError, OSError) as e:
        app.logger.warning("File {0} not found.".format(request_json['chunk_handle']), exc_info = True)
        abort(400)
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)
