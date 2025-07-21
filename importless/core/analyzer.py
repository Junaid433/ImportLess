import ast
from typing import List
from importless.models.import_node import ImportNode

class ImportAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports: List[ImportNode] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(
                ImportNode(
                    module=alias.name,
                    name=None,
                    alias=alias.asname,
                    lineno=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module_name = node.module
        for alias in node.names:
            self.imports.append(
                ImportNode(
                    module=module_name,
                    name=alias.name,
                    alias=alias.asname,
                    lineno=node.lineno,
                )
            )
        self.generic_visit(node)


def analyze_source(source_code: str) -> List[ImportNode]:
    """
    Parse the source code string and return a list of ImportNode representing
    import statements found.
    """
    tree = ast.parse(source_code)
    analyzer = ImportAnalyzer()
    analyzer.visit(tree)
    return analyzer.imports
