class ExecutorAgent:
    def execute_plan(self, plan, knowledge):
        # Implement the logic to execute the plan based on the knowledge
        result = {
            "status": "success",
            "message": f"Plan for {plan['task']} executed by Executor Agent using knowledge: {knowledge['info']}"
        }
        return result
