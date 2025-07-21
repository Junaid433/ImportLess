from typing import Dict, Set, List
from importless.models.import_node import ImportNode

class DependencyGraph:
    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}

    def add_imports(self, file_module: str, imports: List[ImportNode]):
        """
        Add import dependencies for a file/module.
        """
        if file_module not in self.graph:
            self.graph[file_module] = set()

        for imp in imports:
            if imp.module:
                self.graph[file_module].add(imp.module)

    def get_dependencies(self, module: str) -> Set[str]:
        return self.graph.get(module, set())

    def all_modules(self) -> List[str]:
        return list(self.graph.keys())
