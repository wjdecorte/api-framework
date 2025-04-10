import json
import logging
from typing import Any, Callable, Coroutine

from fastapi import Request
from fastapi.routing import APIRoute
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse, Response


async def log_request_info(request: Request, request_body, response: Response):
    ds_logger = logging.getLogger(__name__)
    args = {k: v for k, v in request.items()}

    response_body = None
    if isinstance(response, JSONResponse):
        response_body = json.loads(response.body.decode("utf8"))

    ds_logger.info(
        f"{args.get('method')} {args.get('path')} {args.get('scheme')} {response.status_code}"
        f" Headers={[{k.decode(): v.decode()} for k, v in list(args.get('headers')) if k.startswith(b'x')]}"
        f" Path Params={request.path_params} Query Params={request.query_params if request.query_params else 'None'}"
    )
    if request_body:
        ds_logger.info(f"Request Body={request_body}")
    if response_body:
        ds_logger.info(f"Response Body={response_body}")


class LogRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                request_body = await request.json()
            except json.decoder.JSONDecodeError:
                request_body = await request.body()

            response: Response = await original_route_handler(request)
            background_task: BackgroundTask = BackgroundTask(
                log_request_info, request, request_body, response
            )
            if response.background is None:
                response.background = background_task
            else:
                response.background.add_task(
                    background_task.func, *background_task.args, *background_task.kwargs
                )
            return response

        return custom_route_handler
