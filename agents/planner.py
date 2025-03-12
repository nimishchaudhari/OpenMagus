class PlannerAgent:
    def create_plan(self, request):
        # Implement the logic to create a plan based on the request
        plan = {
            "task": request.get("task", "example_task"),
            "steps": request.get("steps", ["step1", "step2", "step3"])
        }
        return plan
