import clang.cindex
from clang.cindex import CursorKind, TranslationUnit
from collections import defaultdict 
import pdb

def get_translation_unit( fname ):
    index = clang.cindex.Index.create()
    options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
    tu = index.parse( fname, options=options, args=[ '-x',  'c++', '-std=c++17', ] )

    for diag in tu.diagnostics:
        print( diag )

    return tu


def dump_ast( node, output_func, depth=0 ):
    """
    dump the ast for easy human consumption
    """
    indent = " " * depth
    output_func( "%s%s: %s" % ( indent, str( node.kind ), str( node.displayname ) ) )

    if node.displayname == 'stop_hunting(int)':
        #pdb.set_trace()
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
    This includes quaifiers on overridden cursors.
    """
    res = set()
    for child in node.get_children():
        if child.kind == CursorKind.ANNOTATE_ATTR:
            if child.displayname.startswith("funqual::"):
                res.add(child.displayname[9:])

    for overridden_cursor in node.get_overridden_cursors():
        res |= get_qualifiers( overridden_cursor )

    return res
