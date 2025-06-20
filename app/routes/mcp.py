from deputydev_core.services.mcp.dataclass.main import ToolInvokeRequest
from sanic import Blueprint, HTTPResponse, Request
from sanic.exceptions import SanicException
from sanic.response import json

from app.services.mcp_service import McpService

mcp = Blueprint("mcp", url_prefix="mcp")


@mcp.route("/servers/sync", methods=["POST"])
async def server_sync(_request: Request):
    config_path = _request.json["config_path"]
    if not config_path:
        raise SanicException("config_path is not present", status_code=400)
    response = await McpService.sync_mcp_servers(config_path)
    return json(response.model_dump())


@mcp.route("/servers", methods=["GET"])
async def servers(_request: Request):
    response = await McpService.get_servers()
    return json(response.model_dump())


@mcp.route("/servers/<server_name>/enable", methods=["PATCH"])
async def enable_server(request: Request, server_name: str) -> HTTPResponse:
    response = await McpService.enable_server(server_name=server_name)
    return json(response.model_dump())


@mcp.route("/servers/<server_name>/disable", methods=["PATCH"])
async def disable_server(request: Request, server_name: str) -> HTTPResponse:
    response = await McpService.disable_server(server_name=server_name)
    return json(response.model_dump())


@mcp.route("/servers/<server_name>/restart", methods=["PATCH"])
async def restart_server(request: Request, server_name: str) -> HTTPResponse:
    response = await McpService.restart_server(server_name=server_name)
    return json(response.model_dump())


@mcp.route("/servers/tool/invoke", methods=["POST"])
async def invoke_tool(_request: Request):
    json_body = _request.json
    server_name = json_body["server_name"]
    tool_name = json_body["tool_name"]
    tool_arguments = json_body["tool_arguments"]
    request = ToolInvokeRequest(server_name=server_name, tool_name=tool_name, tool_arguments=tool_arguments)
    response = await McpService.invoke_tool(request)
    return json(response.model_dump())


@mcp.route("/servers/tool/approve", methods=["POST"])
async def approve_tool(_request: Request):
    json_body = _request.json
    server_name = json_body["server_name"]
    tool_name = json_body["tool_name"]
    response = await McpService.approve_tool(server_name, tool_name)
    return json(response.model_dump())


@mcp.route("/servers/tools", methods=["GET"])
async def get_tools(_request: Request):
    response = await McpService.get_eligible_tools()
    return json(response.model_dump())
