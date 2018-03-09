from clang.cindex import CursorKind
from collections import defaultdict

def merge( override_maps ):
    result = defaultdict( lambda: set() )

    for override_map in override_maps:
        for key, val in override_map.items():
            result[ key ] |= val

    return result

def get_overrides( tu ):
    overrides = defaultdict( lambda: set() )

    for trav in tu.cursor.walk_preorder():
        if trav.kind == CursorKind.CXX_METHOD:
            for overridden in trav.get_overridden_cursors():
                overrides[ overridden.get_usr() ].add( trav.get_usr() )

    return overrides
