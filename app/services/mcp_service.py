from typing import List, Optional

from deputydev_core.services.mcp.client import MCPClient
from deputydev_core.services.mcp.dataclass.main import (
    ServersDetails,
    ConnectionStatus,
    Tools,
    ToolInvokeRequest,
    McpDefaultSettings,
)
import mcp

from app.utils.request_handlers import handle_mcp_exceptions
from deputydev_core.utils.config_manager import ConfigManager


class McpService:
    mcp_client: Optional[MCPClient] = None

    @classmethod
    def get_default_settings(cls) -> McpDefaultSettings:
        settings = McpDefaultSettings(
            **{
                "max_tools": ConfigManager.configs["MCP"]["MAX_TOOLS"],
                "read_timeout": ConfigManager.configs["MCP"]["SERVER_CONNECTION_TIMEOUT"],
                "tool_response_timeout": ConfigManager.configs["MCP"]["TOOL_RESPONSE_TIMEOUT"],
                "buffer_size": ConfigManager.configs["MCP"]["BUFFER_SIZE"],
            }
        )
        # WARN: Do not delete this, this is useful for local debugging
        # settings = McpDefaultSettings(**{
        #     "max_tools": 200,
        #     "read_timeout": 100,
        #     "tool_response_timeout": 100,
        #     "buffer_size": 20000
        # })
        return settings

    @classmethod
    async def init(cls, mcp_config_path: str):
        if not cls.mcp_client:
            settings = cls.get_default_settings()
            cls.mcp_client = await MCPClient.get_instance(default_settings=settings, mcp_config_path=mcp_config_path)

    @classmethod
    @handle_mcp_exceptions
    async def sync_mcp_servers(cls, config_path: str):
        await cls.init(config_path)
        await cls.mcp_client.sync_mcp_servers()
        # TODO handle pagination
        return await cls.create_server_list(limit=-1, offset=0)

    @classmethod
    @handle_mcp_exceptions
    async def list_tools(cls, server_name):
        return await cls.mcp_client.fetch_tools_list(server_name)

    @classmethod
    async def invoke_tool(cls, tool_invoke_request: ToolInvokeRequest) -> mcp.types.CallToolResult:
        try:
            return await cls.mcp_client.call_tool(
                server_name=tool_invoke_request.server_name,
                tool_name=tool_invoke_request.tool_name,
                tool_arguments=tool_invoke_request.tool_arguments,
            )
        except Exception as ex:
            return mcp.types.CallToolResult(
                isError=True,
                content=[mcp.types.TextContent(type="text", text=f"Error: {str(ex)}")],
            )

    @classmethod
    async def create_server_list(cls, limit: int, offset: int) -> List[ServersDetails]:
        servers: List[ServersDetails] = []
        if offset > len(cls.mcp_client.connections):
            return []
        if limit == -1:
            limit = len(cls.mcp_client.connections)

        eligible_servers = cls.mcp_client.get_servers(connection_statuses=list(ConnectionStatus))[
            offset : offset + limit
        ]

        for server in eligible_servers:
            servers.append(
                ServersDetails(
                    name=server.name,
                    status=server.status.value,
                    tool_count=len(server.tools) if server.tools else 0,
                    tools=server.tools if server.tools else [],
                    error=server.error,
                    disabled=server.disabled,
                )
            )
        return servers

    @classmethod
    @handle_mcp_exceptions
    async def get_servers(cls, limit: int = -1, offset: int = 0) -> List[ServersDetails]:
        if not cls.mcp_client:
            return []
        return await cls.create_server_list(limit, offset)

    @classmethod
    @handle_mcp_exceptions
    async def get_eligible_tools(cls) -> List[Tools]:
        return await cls.mcp_client.get_tools()

    @classmethod
    @handle_mcp_exceptions
    async def restart_server(cls, server_name: str):
        return await cls.mcp_client.restart_server(server_name)

    @classmethod
    @handle_mcp_exceptions
    async def disable_server(cls, server_name: str):
        return await cls.mcp_client.change_status(server_name, disable=True)

    @classmethod
    @handle_mcp_exceptions
    async def enable_server(cls, server_name: str):
        return await cls.mcp_client.change_status(server_name, disable=False)

    @classmethod
    @handle_mcp_exceptions
    async def approve_tool(cls, server_name: str, tool_name: str):
        return await cls.mcp_client.approve_tool(server_name, tool_name)
