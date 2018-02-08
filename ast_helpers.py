import clang.cindex
from clang.cindex import CursorKind
from collections import defaultdict 

def dump_ast( node, output_func, depth=0 ):
    """
    dump the ast for easy human consumption
    """
    indent = " " * depth
    output_func( "%s%s: %s" % ( indent, str( node.kind ), str( node.displayname ) ) )

    if depth == 8 and node.kind == CursorKind.COMPOUND_STMT:
        pass

    for child in node.get_children():
        dump_ast( child, output_func, depth + 2 )

def get_human_name( node ):
    """
    Given a declaration, find its fully qualified name (with class and
    namespaces and compilation unit) and make it human readable
    """
    node = node.referenced

    res = "{0} ({1},{2})".format(
            node.displayname,
            node.location.line,
            node.location.column )

    node = node.semantic_parent
    while node:
        if node.kind == CursorKind.UNEXPOSED_DECL:
            res = "(#include)" + "::" + res
        else:
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

