import json
from sanic import Blueprint, Request, HTTPResponse
from deputydev_core.services.mcp.mcp_service import McpService
from deputydev_core.services.mcp.dataclass.main import ToolInvokeRequest
from sanic.response import json

mcp = Blueprint("mcp", url_prefix="mcp")
mcp_service = McpService()


@mcp.route("/servers/sync", methods=["POST"])
async def server_sync(_request: Request):
    json_body = _request.json
    config_path = json_body["config_path"]
    response = await mcp_service.sync_mcp_servers(config_path)
    return json(response.model_dump())


@mcp.route("/servers", methods=["GET"])
async def servers(_request: Request):
    limit = int(_request.args.get("limit", -1))
    offset = int(_request.args.get("offset", 0))
    response = await mcp_service.get_servers(limit, offset)
    return json(response.model_dump())


@mcp.route("/servers/<server_name>/enable", methods=["PATCH"])
async def enable_server(request: Request, server_name: str) -> HTTPResponse:
    response = await mcp_service.enable_server(server_name=server_name)
    return json(response.model_dump())


@mcp.route("/servers/<server_name>/disable", methods=["PATCH"])
async def disable_server(request: Request, server_name: str) -> HTTPResponse:
    response = await mcp_service.disable_server(server_name=server_name)
    return json(response.model_dump())


@mcp.route("/servers/<server_name>/restart", methods=["PATCH"])
async def restart_server(request: Request, server_name: str) -> HTTPResponse:
    response = await mcp_service.restart_server(server_name=server_name)
    return json(response.model_dump())


@mcp.route("/servers/<server_name>", methods=["PUT"])
async def add_new_server(request: Request, server_name: str) -> HTTPResponse:
    response = await mcp_service.add_new_server(server_name=server_name)
    return json(response.model_dump())


@mcp.route("/servers/<server_name>", methods=["DELETE"])
async def delete_server(request: Request, server_name: str) -> HTTPResponse:
    response = await mcp_service.delete_server(server_name=server_name)
    return json(response.model_dump())


@mcp.route("/servers/tool/invoke", methods=["POST"])
async def invoke_tool(_request: Request):
    json_body = _request.json
    server_name = json_body["server_name"]
    tool_name = json_body["tool_name"]
    tool_arguments = json_body["tool_arguments"]
    request = ToolInvokeRequest(server_name=server_name, tool_name=tool_name, tool_arguments=tool_arguments)
    response = await mcp_service.invoke_tool(request)
    return json(response.model_dump())


@mcp.route("/servers/tools", methods=["GET"])
async def get_tools(_request: Request):
    response = await mcp_service.get_eligible_tools()
    # response = {"tools": [tool.model_dump() for tool in tools]}
    return json(response.model_dump())
