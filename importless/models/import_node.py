from dataclasses import dataclass
from typing import Optional

@dataclass
class ImportNode:
    """
    Represents a single import statement or node.
    """
    module: Optional[str]    
    name: Optional[str]      
    alias: Optional[str]    
    lineno: int         

    def __str__(self):
        parts = []
        if self.module:
            parts.append(f"module='{self.module}'")
        if self.name:
            parts.append(f"name='{self.name}'")
        if self.alias:
            parts.append(f"alias='{self.alias}'")
        parts.append(f"lineno={self.lineno}")
        return f"ImportNode({', '.join(parts)})"
