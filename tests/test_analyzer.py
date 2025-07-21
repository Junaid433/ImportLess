import textwrap
from importless.core.analyzer import analyze_source

def test_analyze_simple_import():
    source = "import os\nimport sys"
    imports = analyze_source(source)
    modules = {imp.module for imp in imports}
    assert "os" in modules
    assert "sys" in modules

def test_analyze_from_import():
    source = "from collections import defaultdict"
    imports = analyze_source(source)
    modules = {imp.module for imp in imports}
    assert "collections" in modules

def test_analyze_alias_import():
    source = "import numpy as np"
    imports = analyze_source(source)
    imp = next(imp for imp in imports if imp.module == "numpy")
    assert imp.alias == "np"

def test_analyze_multiple_imports():
    source = "import os, sys\nfrom math import sqrt, pi"
    imports = analyze_source(source)
    modules = {imp.module for imp in imports}
    assert "os" in modules
    assert "sys" in modules
    assert "math" in modules
    assert any(imp.name == "sqrt" for imp in imports)
    assert any(imp.name == "pi" for imp in imports)

def test_analyze_no_imports():
    source = "print('Hello, World!')"
    imports = analyze_source(source)
    assert len(imports) == 0

def test_analyze_import_with_comments():
    source = textwrap.dedent("""
        # This is a comment
        import json  # Importing JSON module
        from datetime import datetime  # Importing datetime
    """)
    imports = analyze_source(source)
    modules = {imp.module for imp in imports}
    assert "json" in modules
    assert "datetime" in modules

def test_analyze_import_with_docstring():
    source = textwrap.dedent("""
        \"\"\"This module does something.\"\"\"
        import requests
        from urllib.parse import urlparse
    """)
    imports = analyze_source(source)
    modules = {imp.module for imp in imports}
    assert "requests" in modules
    assert "urllib.parse" in modules

def test_analyze_import_with_multiline():
    source = textwrap.dedent("""
        from collections import (
            defaultdict,
            namedtuple
        )
        import os
        import sys
        import json
    """)
    imports = analyze_source(source)
    modules = {imp.module for imp in imports}
    assert "os" in modules
    assert "sys" in modules
    assert "json" in modules
    assert "collections" in modules
    assert any(imp.name == "defaultdict" for imp in imports)
    assert any(imp.name == "namedtuple" for imp in imports)

def test_analyze_import_with_star():
    source = "from math import *"
    imports = analyze_source(source)
    modules = {imp.module for imp in imports}
    assert "math" in modules
    assert any(imp.name == "*" for imp in imports)  

def test_analyze_import_with_nested():
    source = "from package.module import Class, function"
    imports = analyze_source(source)
    modules = {imp.module for imp in imports}
    assert "package.module" in modules
    assert any(imp.name == "Class" for imp in imports)
    assert any(imp.name == "function" for imp in imports)