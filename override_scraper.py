from clang.cindex import CursorKind
from collections import defaultdict

def merge( override_maps ):
    """
    Merge two override maps
    """
    result = defaultdict( lambda: set() )

    for override_map in override_maps:
        for key, val in override_map.items():
            result[ key ] |= val

    return result

def get_overrides( tu ):
    """
    Scrape a translation unit and generate a mapping of methods to the 
    methods that override them
    """
    overrides = defaultdict( lambda: set() )

    for trav in tu.cursor.walk_preorder():
        if trav.kind == CursorKind.CXX_METHOD:
            to_visit = list( trav.get_overridden_cursors() )
            while to_visit:
                overridden = to_visit.pop()
                overrides[ overridden.get_usr() ].add( trav.get_usr() )
                to_visit += list( overridden.get_overridden_cursors() )

    return overrides
