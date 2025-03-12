from flask import Flask, request, jsonify
from agents.planner_agent import PlannerAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.executor_agent import ExecutorAgent

app = Flask(__name__)

class CoordinatorAgent:
    def __init__(self):
        self.planner = PlannerAgent()
        self.knowledge = KnowledgeAgent()
        self.executor = ExecutorAgent()

    def handle_request(self, request_data):
        plan = self.planner.create_plan(request_data)
        knowledge = self.knowledge.retrieve_knowledge(plan)
        result = self.executor.execute_plan(plan, knowledge)
        return result

coordinator = CoordinatorAgent()

@app.route('/request', methods=['POST'])
def handle_request():
    data = request.json
    response = coordinator.handle_request(data)
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000)
