from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from analysis import main

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@cross_origin()
@app.route("/")
def hello_world():
    return

@app.route("/api/post-movies", methods=["POST"])
def post_movies():
    data = request.json
    return jsonify(data)

@app.route("/api/analyze-movies", methods=["GET", "POST"])
def start_analysis():
    data = request.json
    results = main(data[0], data[1])
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)