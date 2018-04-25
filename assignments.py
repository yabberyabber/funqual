#!/usr/bin/env python3

import sys
from clang.cindex import CursorKind
from ast_helpers import get_translation_unit
from collections import defaultdict

def get_operator( binop_node ):
    """
    Cheap hack to get the binary operator out of a clang expression
    because clang doesn't expose the binop interface to the python
    api
    """
    return [ x.spelling for x in binop_node.get_tokens() ][1]


def get_lvalue( binop_node ):
    "Cheap hack to get lvalue from binop expression"
    return [ x for x in binop_node.get_children() ][ 0 ].referenced


def get_rvalue( binop_node ):
    "Cheap hack to get rvalue from binop expression"
    return [ x for x in binop_node.get_children() ][ 1 ].referenced


def is_lvalue_funptr( binop_node ):
    "Check whether the lvalue of this operation is a function pointer"

    if '(*)' in get_lvalue( binop_node ).type.spelling:
        return True
    else:
        return False


def check_assignments( tu, callback ):
    for trav in tu.cursor.walk_preorder():
        if ( trav.kind == CursorKind.BINARY_OPERATOR and
             len( list( trav.get_children() ) ) == 2 ):
            try:
                if get_operator( trav ) == '=' and is_lvalue_funptr( trav ):
                    callback(
                            ( get_lvalue( trav ).get_usr(),
                              get_rvalue( trav ).get_usr() ) )
            except:
                pass


if __name__ == '__main__':
    target = get_translation_unit( sys.argv[ 1 ] )

    check_assignments( target, print )
