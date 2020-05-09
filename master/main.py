from flask import Flask

main = Flask(__name__)

@app.route("/")
def example():
    pass

if __name__ == "__main__":
    main.run(host='0.0.0.0')
