from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/plan', methods=['POST'])
def plan_task():
    data = request.json
    # Implement the logic to plan the task
    response = {
        "status": "success",
        "message": "Task planned by Planner Agent"
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5001)
