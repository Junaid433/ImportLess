from typing import Set, List

def generate_requirements(packages: Set[str]) -> List[str]:
    """
    Given a set of package names, generate a sorted list suitable
    for writing to requirements.txt.
    """
    return sorted(packages)


def diff_requirements(old_reqs: Set[str], new_reqs: Set[str]) -> dict:
    """
    Compare old and new requirements sets, return dict with:
    - added: packages in new_reqs but not in old_reqs
    - removed: packages in old_reqs but not in new_reqs
    """
    added = new_reqs - old_reqs
    removed = old_reqs - new_reqs
    return {
        "added": sorted(added),
        "removed": sorted(removed),
    }
