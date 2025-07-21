class ImportLessError(Exception):
    """Base exception class for ImportLess errors."""
    pass

class FileParseError(ImportLessError):
    """Raised when a Python file cannot be parsed."""

    def __init__(self, filepath: str, message: str = "Failed to parse Python file"):
        self.filepath = filepath
        self.message = message
        super().__init__(f"{message}: {filepath}")

class InvalidImportError(ImportLessError):
    """Raised when an invalid or malformed import statement is encountered."""

class DependencyGraphError(ImportLessError):
    """Raised when there is an issue building or processing the dependency graph."""

class DependencyAnalysisError(ImportLessError):
    """Raised when dependency analysis fails."""

    def __init__(self, message: str = "Dependency analysis error"):
        self.message = message
        super().__init__(message)

class RequirementGenerationError(ImportLessError):
    """Raised when generating requirements fails."""
