"""
Pydantic models for the ``ovos-PHAL-plugin-tools`` bus surface.

The ``ovos-PHAL-plugin-tools`` PHAL plugin exposes installed OPM ToolBox
plugins over the messagebus, allowing skills, agents, and external clients to:

- **list** all available tools (``ovos.tools.list``);
- **get** the full JSON Schema of a single tool (``ovos.tools.get``);
- **invoke** a tool by name with keyword arguments (``ovos.tools.invoke``);
- **reload** the toolbox registry at runtime (``ovos.tools.reload``).

Source: ``OpenVoiceOS/ovos-PHAL-plugin-tools`` (``ovos_phal_plugin_tools/__init__.py``).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage


# ---------------------------------------------------------------------------
# Shared schema types
# ---------------------------------------------------------------------------

class ToolEntry(BaseModel):
    """Description of a single tool exposed by a ToolBox plugin."""

    name: str = Field(..., description="Unique tool name across all loaded toolboxes.")
    description: str = Field(..., description="Human-readable description of what the tool does.")
    argument_schema: Dict[str, Any] = Field(
        ...,
        description="JSON Schema object describing the accepted keyword arguments.",
    )
    output_schema: Dict[str, Any] = Field(
        ...,
        description="JSON Schema object describing the return value structure.",
    )
    toolbox_id: str = Field(
        ...,
        description="Entry-point name of the ToolBox plugin that registered this tool.",
    )
    model_config = ConfigDict(extra="allow")


# ---------------------------------------------------------------------------
# ovos.tools.list / ovos.tools.list.response
# ---------------------------------------------------------------------------

class OvosToolsListMessage(OpenVoiceOSMessage):
    """Request the full list of tools registered across all loaded ToolBox plugins.

    The plugin responds with ``ovos.tools.list.response`` carrying a list of
    :class:`ToolEntry` objects.

    Source: ``ovos-PHAL-plugin-tools`` ``handle_tools_list``.

    Example::

        OvosToolsListMessage()
    """

    message_type: str = "ovos.tools.list"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosToolsListResponseData(BaseModel):
    """Response payload for ``ovos.tools.list``."""

    tools: List[ToolEntry] = Field(
        ...,
        description="All tools across all loaded ToolBox plugins.",
    )


class OvosToolsListResponseMessage(OpenVoiceOSMessage):
    """Return the list of all available tools.

    Emitted by ``ovos-PHAL-plugin-tools`` in response to ``ovos.tools.list``.

    Example::

        OvosToolsListResponseMessage(
            data=OvosToolsListResponseData(tools=[
                ToolEntry(
                    name="add",
                    description="Add two integers.",
                    argument_schema={"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}},
                    output_schema={"type": "object", "properties": {"result": {"type": "integer"}}},
                    toolbox_id="math_tools",
                )
            ])
        )
    """

    message_type: str = "ovos.tools.list.response"
    data: OvosToolsListResponseData


# ---------------------------------------------------------------------------
# ovos.tools.get / ovos.tools.get.response
# ---------------------------------------------------------------------------

class OvosToolsGetData(BaseModel):
    """Request payload for retrieving a single tool's schema."""

    name: str = Field(..., description="Name of the tool to retrieve.")


class OvosToolsGetMessage(OpenVoiceOSMessage):
    """Request the full schema of a named tool.

    The plugin responds with ``ovos.tools.get.response`` carrying either a
    :class:`ToolEntry` or an error string.

    Source: ``ovos-PHAL-plugin-tools`` ``handle_tools_get``.

    Example::

        OvosToolsGetMessage(data=OvosToolsGetData(name="add"))
    """

    message_type: str = "ovos.tools.get"
    data: OvosToolsGetData


class OvosToolsGetResponseData(BaseModel):
    """Response payload for ``ovos.tools.get``.

    On success: all :class:`ToolEntry` fields are populated and ``error`` is
    absent.  On error: ``error`` is set and the tool fields may be absent.
    """

    name: Optional[str] = Field(None, description="Tool name (populated on success).")
    description: Optional[str] = Field(None, description="Tool description (populated on success).")
    argument_schema: Optional[Dict[str, Any]] = Field(
        None, description="Argument JSON Schema (populated on success)."
    )
    output_schema: Optional[Dict[str, Any]] = Field(
        None, description="Output JSON Schema (populated on success)."
    )
    toolbox_id: Optional[str] = Field(
        None, description="ToolBox plugin id (populated on success)."
    )
    error: Optional[str] = Field(None, description="Error message when the tool was not found.")
    model_config = ConfigDict(extra="allow")


class OvosToolsGetResponseMessage(OpenVoiceOSMessage):
    """Return a single tool's schema, or an error if the tool was not found.

    Emitted by ``ovos-PHAL-plugin-tools`` in response to ``ovos.tools.get``.
    """

    message_type: str = "ovos.tools.get.response"
    data: OvosToolsGetResponseData


# ---------------------------------------------------------------------------
# ovos.tools.invoke / ovos.tools.invoke.response
# ---------------------------------------------------------------------------

class OvosToolsInvokeData(BaseModel):
    """Request payload for invoking a tool."""

    name: str = Field(..., description="Name of the tool to invoke.")
    args: Dict[str, Any] = Field(
        default_factory=dict,
        description="Keyword arguments to pass to the tool, validated against its argument_schema.",
    )


class OvosToolsInvokeMessage(OpenVoiceOSMessage):
    """Invoke a named tool with the given keyword arguments.

    The plugin calls the tool synchronously and responds with
    ``ovos.tools.invoke.response`` carrying either a ``result`` or an ``error``.

    Source: ``ovos-PHAL-plugin-tools`` ``handle_tools_invoke``.

    Example::

        OvosToolsInvokeMessage(
            data=OvosToolsInvokeData(name="add", args={"a": 10, "b": 32})
        )
    """

    message_type: str = "ovos.tools.invoke"
    data: OvosToolsInvokeData


class OvosToolsInvokeResponseData(BaseModel):
    """Response payload for ``ovos.tools.invoke``.

    On success: ``result`` is populated.
    On error: ``error`` is set (``result`` may be absent or ``None``).
    """

    name: str = Field(..., description="Name of the invoked tool.")
    result: Optional[Dict[str, Any]] = Field(
        None,
        description="Return value of the tool call, structured per the tool's output_schema.",
    )
    error: Optional[str] = Field(
        None,
        description="Error string (e.g. 'ValueError: ...') when the invocation raised.",
    )
    model_config = ConfigDict(extra="allow")


class OvosToolsInvokeResponseMessage(OpenVoiceOSMessage):
    """Return the result (or error) from a tool invocation.

    Emitted by ``ovos-PHAL-plugin-tools`` in response to ``ovos.tools.invoke``.
    """

    message_type: str = "ovos.tools.invoke.response"
    data: OvosToolsInvokeResponseData


# ---------------------------------------------------------------------------
# ovos.tools.reload / ovos.tools.reload.response
# ---------------------------------------------------------------------------

class OvosToolsReloadMessage(OpenVoiceOSMessage):
    """Reload the toolbox registry by re-discovering all installed ToolBox plugins.

    Useful when new toolbox plugins have been installed while OVOS is running
    (e.g. via ``pip install`` followed by ``ovos.pip.install.complete``).
    The plugin clears the existing registry, re-runs discovery, and responds
    with ``ovos.tools.reload.response``.

    Source: ``ovos-PHAL-plugin-tools`` ``handle_tools_reload``.
    """

    message_type: str = "ovos.tools.reload"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosToolsReloadResponseData(BaseModel):
    """Response payload for ``ovos.tools.reload``."""

    loaded: List[str] = Field(
        ...,
        description="List of toolbox_id strings for all successfully loaded toolboxes after reload.",
    )
    total_tools: int = Field(
        ...,
        description="Total number of tools registered across all reloaded toolboxes.",
    )


class OvosToolsReloadResponseMessage(OpenVoiceOSMessage):
    """Confirm that the toolbox registry was reloaded.

    Emitted by ``ovos-PHAL-plugin-tools`` in response to ``ovos.tools.reload``.
    """

    message_type: str = "ovos.tools.reload.response"
    data: OvosToolsReloadResponseData
