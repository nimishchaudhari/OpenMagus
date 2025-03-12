class ModelRouter:
    def __init__(self, primary_llm, secondary_llm, task_specific_models):
        self.primary_llm = primary_llm
        self.secondary_llm = secondary_llm
        self.task_specific_models = task_specific_models

    def route_task(self, task):
        # Implement task routing logic here
        if task['type'] == 'planning':
            return self.primary_llm.handle_task(task)
        elif task['type'] == 'domain':
            return self.secondary_llm.handle_task(task)
        else:
            model = self.task_specific_models.get(task['type'])
            if model:
                return model.handle_task(task)
            else:
                raise ValueError(f"No model found for task type: {task['type']}")
