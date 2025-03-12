from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query_knowledge():
    data = request.json
    # Implement the logic to query knowledge
    response = {
        "status": "success",
        "message": "Knowledge queried by Knowledge Agent"
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5002)
