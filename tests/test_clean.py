import textwrap
from importless.cli.commands.clean import find_unused_imports, remove_unused_imports_from_source

def test_find_unused_imports_basic():
    source = textwrap.dedent("""
        import os
        import sys
        import json
        print(os.name)
    """)
    unused = find_unused_imports(source)
    unused_modules = [imp[2] for imp in unused if imp[1] == "import"]
    assert "sys" in unused_modules
    assert "json" in unused_modules
    assert "os" not in unused_modules

def test_remove_unused_imports_basic():
    source = textwrap.dedent("""
        import os
        import sys
        import json
        print(os.name)
    """)
    unused = find_unused_imports(source)
    cleaned = remove_unused_imports_from_source(source, unused)
    assert "import sys" not in cleaned
    assert "import json" not in cleaned
    assert "import os" in cleaned

def test_find_unused_imports_alias():
    source = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        print(np.array([1,2,3]))
    """)
    unused = find_unused_imports(source)
    unused_modules = [imp[2] for imp in unused if imp[1] == "import"]
    assert "pandas" in unused_modules
    assert "numpy" not in unused_modules

def test_remove_unused_imports_alias():
    source = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        print(np.array([1,2,3]))
    """)
    unused = find_unused_imports(source)
    cleaned = remove_unused_imports_from_source(source, unused)
    assert "import pandas" not in cleaned
    assert "import numpy" in cleaned

def test_find_unused_imports_from_import():
    source = textwrap.dedent("""
        from math import sqrt, pi
        from collections import defaultdict
        print(sqrt(9))
    """)
    unused = find_unused_imports(source)
    unused_from = [(imp[3], imp[4]) for imp in unused if imp[1] == "from"]
    assert ("pi", None) in unused_from
    assert ("sqrt", None) not in unused_from
    assert ("defaultdict", None) in unused_from

def test_remove_unused_imports_from_import():
    source = textwrap.dedent("""
        from math import sqrt, pi
        from collections import defaultdict
        print(sqrt(9))
    """)
    unused = find_unused_imports(source)
    cleaned = remove_unused_imports_from_source(source, unused)
    assert "pi" not in cleaned
    assert "sqrt" in cleaned
    assert "defaultdict" not in cleaned

def test_find_unused_imports_mixed():
    source = textwrap.dedent("""
        import os
        from sys import path as sys_path
        import json
        print(os.name, sys_path)
    """)
    unused = find_unused_imports(source)
    unused_imports = [imp for imp in unused if imp[1] == "import"]
    unused_froms = [imp for imp in unused if imp[1] == "from"]
    unused_names = [imp[2] if imp[1]=="import" else imp[3] for imp in unused]
    assert "json" in unused_names
    assert "os" not in unused_names
    assert "path" not in unused_names  # used as sys_path alias

def test_remove_unused_imports_mixed():
    source = textwrap.dedent("""
        import os
        from sys import path as sys_path
        import json
        print(os.name, sys_path)
    """)
    unused = find_unused_imports(source)
    cleaned = remove_unused_imports_from_source(source, unused)
    assert "import json" not in cleaned
    assert "import os" in cleaned
    assert "from sys import path" in cleaned

def test_find_unused_imports_with_asname():
    source = textwrap.dedent("""
        from collections import defaultdict as dd, namedtuple as nt
        print(dd)
    """)
    unused = find_unused_imports(source)
    unused_froms = [(imp[3], imp[4]) for imp in unused if imp[1] == "from"]
    assert ("namedtuple", "nt") in unused_froms
    assert ("defaultdict", "dd") not in unused_froms

def test_remove_unused_imports_with_asname():
    source = textwrap.dedent("""
        from collections import defaultdict as dd, namedtuple as nt
        print(dd)
    """)
    unused = find_unused_imports(source)
    cleaned = remove_unused_imports_from_source(source, unused)
    assert "namedtuple" not in cleaned
    assert "defaultdict" in cleaned
