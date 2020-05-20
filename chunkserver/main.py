from flask import Flask, request, Response, json, abort
#from werkzeug.utils import secure_filename
import logging
logging.basicConfig(level=logging.DEBUG)

import master_interact, lease_grant
MAX_APPEND_LIMIT = 16
CHUNK_SIZE = 64

app = Flask(__name__)

@app.route("/")
def example():
    return "Chunkserver Flask API!"

@app.route("/create/<chunk_handle>")
def create(chunk_handle):
	chunk_file = {}
	chunk_file["chunk"] = []
	chunk_file["chunk"].append({
                "name" : chunk_handle,
                "mutable": 0,
		"lease": 0,
		"ISO_lease_time": 00000000,
		"lease_time":00000000
        })
	with open(chunk_handle + '.chunk', 'w') as chunk:
		json.dump(chunk_file, chunk)
		if json.load(chunk):
			success = 1
		else:
			success = 0
		return success

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
        app.logger.warning("File {0} not found.".format(request_json['chunk_handle']))
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
        return app.response_class(json.dumps(lease_grant.lease_grant(request_json['chunk_handle'],
                                                                     request_json['timestamp'],
                                                                     request_json['replica'])),
                                  content_type='application/json')
    except (KeyError, IOError, OSError) as e:
        abort(400)
    except Exception as e:
        app.logger.error("Exception.", exc_info = True)
        abort(500)

@app.route("/read/<int:chunk_handle>,<int:start_byte>,<int:byte_range>")
def read(chunk_handle, start_byte, byte_range):
	with open(chunk_handle + '.chunk') as c_file:
		chunk_data = c_file.seek(start_byte + 16) #16 first information bytes
		json_data = json.load(chunk_data)
		return_list = []
		for x in range(0, byte_range):
			python_data = json_data.readline()
			return_list.append(python_data)

	return return_list

@app.route("/append", strict_slashes=False, methods=['GET', 'POST'])
def append():
	"""
	The Append function which takes data from the Client

	It expects JSON input from an HTTP POST request in the form: {
		'chunk_handle': <hex>,
		'bytes': <binary_data>
	}
	It implements a skeleton LRU (Least Recently Used) Cache but currently cached bytes have no expiration (FIXME). Bytes are stored in a <chunk_handle>.chunk.<timestamp>.cache file

	It returns:
		- 0: Success: It worked
		- 1: Failure: Too many Bytes
		- 2: Failure: Chunk too full
		- 3: Failure: Yo idk
	"""
	# save the chunk_handle and bytes from the POST request's JSON
	request_json = request.get_json()
	chunk_handle = request_json['chunk_handle']
	bytes = request_json['bytes'] # FIXME should typecast as bytes
	if len(bytes) > MAX_APPEND_LIMIT:
		return 1 # The operation failed because bytes > MAX_APPEND_LIMIT
	else if len(bytes) > CHUNK_SIZE - len(os.path.getsize(chunk_handle + ".chunk")):
		# FIXME: this logic should be moved to append_request see Nuclino API for more information
		return 2 # The operation failed because bytes > The amount of space left on the chunk
	else:
		# use the chunk_handle to create the cache file
		with open(chunk_handle + '.chunk.' + datetime.datetime.now() + 'cache', 'x') as cache: # using x 'create only' mode so writing will fail if cache file already exists FIXME
			# dump the recieved bytes into the cache file
			json.dump(bytes, cache)
			return 0
	return 3 # ya--- idk

@app.route("/append-request")
def append_request():
	# use the chunk_handle to write the buffer to the File
	# send append_request to Replicas
	# return int
    abort(501)
    return ""
