from typing import Any
from strands.types.tools import ToolUse, ToolResult

TOOL_SPEC = {
    "name": "character_counter",
    "description": "Counts the total number of characters in the provided text",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to count characters in"
                }
            },
            "required": ["text"]
        }
    }
}

def character_counter(tool_use: ToolUse, **kwargs: Any) -> ToolResult:
    """
    Counts the total number of characters in the provided text.
    
    Args:
        tool_use: The tool use object containing input parameters
        
    Returns:
        ToolResult: Dictionary containing the character count result
    """
    tool_use_id = tool_use["toolUseId"]
    text = tool_use["input"]["text"]
    
    # Count characters in the text
    character_count = len(text)
    
    return {
        "toolUseId": tool_use_id,
        "status": "success",
        "content": [{"text": f"Character count: {character_count} characters in the provided text"}]
    }