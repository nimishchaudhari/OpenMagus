from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register_tool():
    data = request.json
    # Implement the logic to register a tool
    response = {
        "status": "success",
        "message": "Tool registered"
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5004)
