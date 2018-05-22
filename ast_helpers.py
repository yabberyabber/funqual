#!/usr/bin/env python3

import clang.cindex
from clang.cindex import CursorKind, TranslationUnit
from collections import defaultdict 
import pdb
import sys

def get_translation_unit( fname, cmd_args ):
    index = clang.cindex.Index.create()
    options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD

    args = [
            '-x', cmd_args.language,
            '-std=' + cmd_args.standard,
    ]

    if cmd_args.include_path:
        for path in cmd_args.include_path.split( ',' ):
            args.append( '-I' )
            args.append( path )

    tu = index.parse( fname, options=options, args=args )

    if tu.diagnostics:
        print( "\nParsing errors for {}".format( fname ) )
        for diag in tu.diagnostics:
            print( "\t{}".format( str( diag ) ) )
        if cmd_args.verbose:
            print( "Clang arguments: {}".format( ' '.join( args ) ) )

    return tu


def dump_ast( node, output_func, depth=0 ):
    """
    dump the ast for easy human consumption
    """
    indent = " " * depth
    output_func( "%s%s: %s" % ( indent, str( node.kind ), str( node.displayname ) ) )

    if node.kind in [CursorKind.DECL_REF_EXPR, CursorKind.VAR_DECL]:
        #pdb.set_trace()
        pass

    if node.kind == CursorKind.BINARY_OPERATOR:
        #pdb.set_trace()
        pass

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

def is_function_pointer( cursor ):
    return '(*)' in cursor.type.spelling

if __name__ == '__main__':
    dump_ast(get_translation_unit(sys.argv[1]).cursor, print)
