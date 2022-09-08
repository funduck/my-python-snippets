import asyncio
import aiohttp
from health_checking.health_checking import HealthChecking
from health_checking.http_server import start_server

class TestHttpServer:
    def test_should_start_server_with_health_checker(self):
        oks = 0
        errs = 0
        last_descr = ""

        timeouts = {
            "checks_init": 0.1,
            "checks": 0.05,
            "sets": 0.07
        }

        async def test_healthchecks():
            nonlocal oks, errs, last_descr
            await asyncio.sleep(timeouts["checks_init"])
            async with aiohttp.ClientSession('http://localhost:8888') as session:
                while True:
                    await asyncio.sleep(timeouts["checks"])
                    async with session.get("/") as response:
                        if response.status == 200:
                            oks += 1
                        else:
                            errs += 1
                        last_descr = await response.text()

        async def set_healthchecks():
            await asyncio.sleep(timeouts["checks_init"])
            for _ in range(3):
                await asyncio.sleep(timeouts["sets"])
                HealthChecking.getChecker("server").set_healthy("main")
            for _ in range(3):
                await asyncio.sleep(timeouts["sets"])
                HealthChecking.getChecker("server").set_not_healthy("main", "is feeling bad")

        async def runner():
            """
            This is a good example of "start_server" coroutine with HealthChecking
            """
            tasks = list(map(asyncio.create_task, [
                start_server(host="localhost", port=8888, checker=HealthChecking.getChecker("server")),
                test_healthchecks(),
                set_healthchecks()
            ]))
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in tasks:
                task.cancel()

        asyncio.run(runner())

        assert oks > 0
        assert errs > 0
        assert '"main": "is feeling bad"' in last_descr
