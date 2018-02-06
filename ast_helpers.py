import clang.cindex
from clang.cindex import CursorKind
from collections import defaultdict 

def dump_ast( node, depth=0 ):
    """
    dump the ast for easy human consumption
    """
    indent = " " * depth
    print( "%s%s: %s" % ( indent, str( node.kind ), str( node.displayname ) ) )

    if depth == 8 and node.kind == CursorKind.COMPOUND_STMT:
        pass

    for child in node.get_children():
        dump_ast( child, depth + 2 )

def get_human_name( node ):
    """
    Given a declaration, find its fully qualified name (with class and
    namespaces and compilation unit) and make it human readable
    """
    res = str(node.displayname)
    node = node.semantic_parent
    while node:
        res = str(node.displayname) + "::" + res
        node = node.semantic_parent
    return res

def get_qualifiers( node ):
    """
    Given a declaration, return all its qualifiers
    """
    res = set()
    for child in node.get_children():
        if child.kind == CursorKind.ANNOTATE_ATTR:
            if child.displayname.startswith("funqual::"):
                res.add(child.displayname[9:])
    return res

