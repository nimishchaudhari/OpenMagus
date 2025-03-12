class ProceduralMemory:
    def __init__(self):
        self.plans = {}

    def store_plan(self, session_id, plan):
        self.plans[session_id] = plan

    def retrieve_plan(self, session_id):
        return self.plans.get(session_id)

    def record_result(self, session_id, step, result):
        if session_id in self.plans:
            self.plans[session_id]['results'].append({'step': step, 'result': result})
