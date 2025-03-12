import asyncio
from aiohttp import ClientSession
import logging

class ExecutorAgent:
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.session = ClientSession()

    async def execute_plan(self, plan, knowledge):
        try:
            # Simulate asynchronous task execution
            await asyncio.sleep(1)
            result = {
                "status": "success",
                "message": f"Plan for {plan['task']} executed by Executor Agent using knowledge: {knowledge['info']}"
            }
            return result
        except Exception as e:
            logging.error(f"Error executing plan: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def worker(self):
        while True:
            plan, knowledge = await self.task_queue.get()
            result = await self.execute_plan(plan, knowledge)
            self.task_queue.task_done()
            print(result)

    async def start_workers(self, num_workers):
        workers = [asyncio.create_task(self.worker()) for _ in range(num_workers)]
        await asyncio.gather(*workers)

    async def add_task(self, plan, knowledge):
        await self.task_queue.put((plan, knowledge))

    async def close(self):
        await self.session.close()
