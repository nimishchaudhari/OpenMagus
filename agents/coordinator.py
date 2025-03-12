from flask import Flask, request, jsonify
from agents.planner_agent import PlannerAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.executor import ExecutorAgent
from agents.security import has_capability
from agents.network_security import allow_access, get_client_ip

from agents.sanitizer import sanitize_input
app = Flask(__name__)

class CoordinatorAgent:
    def __init__(self):
        self.planner = PlannerAgent()
        self.knowledge = KnowledgeAgent()
        self.executor = ExecutorAgent()

    async def handle_request(self, request_data):
        plan = self.planner.create_plan(sanitized_data)
sanitized_data = sanitize_input(request_data)
        knowledge = self.knowledge.retrieve_knowledge(plan)
        await self.executor.add_task(plan, knowledge)
        result = await self.executor.execute_plan(plan, knowledge)
        return result

coordinator = CoordinatorAgent()

@app.route('/request', methods=['POST'])
@has_capability('execute')
async def handle_request():
client_ip = get_client_ip(request)
    if not allow_access(client_ip):
        return jsonify({'message': 'Access denied'}), 403
    data = request.json
    response = await coordinator.handle_request(data)
    return jsonify(response)

async def start(num_workers):
    await coordinator.start(num_workers)

async def close():
    await coordinator.close()

if __name__ == '__main__':
    import asyncio
    num_workers = 5  # Set the number of worker threads
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(num_workers))
    app.run(port=5000)
    loop.run_until_complete(close())
