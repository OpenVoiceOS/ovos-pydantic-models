# PHAL Tools Bus Messages

Messages emitted and consumed by
[`ovos-PHAL-plugin-tools`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-tools).

The plugin exposes installed OPM **ToolBox** plugins over the messagebus, allowing skills,
agents, and external clients to list, inspect, invoke, and reload tools at runtime — no
direct Python imports required.

---

## Coverage table

| Message type | Class | Direction | Description |
|---|---|---|---|
| `ovos.tools.list` | `OvosToolsListMessage` | client → plugin | List all tools across all loaded toolboxes |
| `ovos.tools.list.response` | `OvosToolsListResponseMessage` | plugin → client | Returns `tools: List[ToolEntry]` |
| `ovos.tools.get` | `OvosToolsGetMessage` | client → plugin | Get schema of a single named tool |
| `ovos.tools.get.response` | `OvosToolsGetResponseMessage` | plugin → client | Returns tool schema or `error` |
| `ovos.tools.invoke` | `OvosToolsInvokeMessage` | client → plugin | Invoke a tool with `name` + `args` |
| `ovos.tools.invoke.response` | `OvosToolsInvokeResponseMessage` | plugin → client | Returns `result` or `error` |
| `ovos.tools.reload` | `OvosToolsReloadMessage` | client → plugin | Reload the toolbox registry |
| `ovos.tools.reload.response` | `OvosToolsReloadResponseMessage` | plugin → client | Returns `loaded` toolbox list + `total_tools` |

---

## Usage

```python
from ovos_pydantic_models.phal.tools import (
    OvosToolsListMessage, OvosToolsListResponseData, OvosToolsListResponseMessage,
    OvosToolsGetData, OvosToolsGetMessage,
    OvosToolsGetResponseData, OvosToolsGetResponseMessage,
    OvosToolsInvokeData, OvosToolsInvokeMessage,
    OvosToolsInvokeResponseData, OvosToolsInvokeResponseMessage,
    OvosToolsReloadMessage, OvosToolsReloadResponseData, OvosToolsReloadResponseMessage,
    ToolEntry,
)
```

### List all tools

```python
# Request
req = OvosToolsListMessage()

# Response (received from bus)
resp = OvosToolsListResponseMessage(
    data=OvosToolsListResponseData(
        tools=[
            ToolEntry(
                name="add",
                description="Add two integers.",
                argument_schema={
                    "type": "object",
                    "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                },
                output_schema={
                    "type": "object",
                    "properties": {"result": {"type": "integer"}},
                },
                toolbox_id="math_tools",
            )
        ]
    )
)
for tool in resp.data.tools:
    print(tool.name, "-", tool.description)
```

### Get a single tool's schema

```python
req = OvosToolsGetMessage(data=OvosToolsGetData(name="add"))

# Success response
ok = OvosToolsGetResponseMessage(
    data=OvosToolsGetResponseData(
        name="add", description="Add two integers.",
        argument_schema={"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}},
        output_schema={"type": "object", "properties": {"result": {"type": "integer"}}},
        toolbox_id="math_tools",
    )
)

# Error response
err = OvosToolsGetResponseMessage(
    data=OvosToolsGetResponseData(error="Unknown tool: 'nonexistent'")
)
```

### Invoke a tool

```python
req = OvosToolsInvokeMessage(
    data=OvosToolsInvokeData(name="add", args={"a": 10, "b": 32})
)

# Success
ok = OvosToolsInvokeResponseMessage(
    data=OvosToolsInvokeResponseData(name="add", result={"result": 42})
)

# Error
err = OvosToolsInvokeResponseMessage(
    data=OvosToolsInvokeResponseData(name="add", error="ValueError: b must be positive")
)
```

### Reload the registry

```python
req = OvosToolsReloadMessage()

resp = OvosToolsReloadResponseMessage(
    data=OvosToolsReloadResponseData(loaded=["math_tools", "weather_tools"], total_tools=5)
)
print(f"Loaded {resp.data.total_tools} tools from {resp.data.loaded}")
```
