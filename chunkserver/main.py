from flask import Flask
#from flask import request
#from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route("/")
def example():
	return "Chunkserver Flask API!"

@app.route("/create")
def create():
	abort(501)
	return ""

@app.route("/lease")
def lease():
	abort(501)
	return ""

@app.route("/collect-garbage/", methods=['GET','POST'])
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
