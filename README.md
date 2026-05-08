<div align="center">

# Fishkeeper Ai MCP

**FishKeeper.AI MCP Server - Aquarium Management AI**

[![PyPI](https://img.shields.io/pypi/v/meok-fishkeeper-ai-mcp)](https://pypi.org/project/meok-fishkeeper-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

FishKeeper.AI MCP Server - Aquarium Management AI
Built by MEOK AI Labs | https://fishkeeper.ai

Water analysis, species identification, compatibility checking,
disease diagnosis, stocking calculations, and feeding schedules.

## Tools

| Tool | Description |
|------|-------------|
| `analyze_water_params` | Analyze aquarium water parameters and return health assessment. |
| `identify_fish` | Identify fish species and return detailed care requirements. |
| `check_compatibility` | Check if multiple fish species are compatible in the same tank. |
| `diagnose_disease` | Diagnose fish disease from symptoms and suggest treatments. |
| `calculate_stocking` | Calculate maximum fish stocking for a tank. |
| `get_feeding_schedule` | Generate a feeding schedule based on species mix. |

## Installation

```bash
pip install meok-fishkeeper-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "fishkeeper-ai": {
      "command": "python",
      "args": ["-m", "meok_fishkeeper_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 6 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
