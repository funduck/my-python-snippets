"""
Http health checking server.
"""


import asyncio
from typing import Callable
from health_checking.health_checking import Checker


async def start_server(
    host: str = "0.0.0.0",
    port: int = 8888,
    checker: Checker = None,
    check_cb: Callable = None
):
    """
    A coroutine that runs TCP server, responding to healthcheck requests GET HOST:PORT.
    200 - ok, healthy.
    503 - not healthy.
    Response may contain optional description of health status.
    Can be used with health_checking.Checker
    or health_check_cb a callback that will return tuple[boolean, string]
    """
    if checker:
        check_health = lambda : checker.get_status()
    elif check_cb:
        check_health = check_cb
    else:
        raise RuntimeError("Should provide 'checker' or 'check_cb', both are None")

    async def handler(_: asyncio.StreamReader, writer: asyncio.StreamWriter):
        healthy, descr = check_health()
        http_response = "200 OK" if healthy else "503 SERVICE UNAVAILABLE"

        writer.write(f'HTTP/1.1 {http_response}\r\n\r\n{descr}'.encode('utf8'))
        await writer.drain()
        if writer.can_write_eof():
            writer.write_eof()
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(handler, host, port)

    try:
        async with server:
            await server.serve_forever()
    except asyncio.CancelledError:
        server.close()
        await server.wait_closed()
