from clang.cindex import CursorKind
from collections import defaultdict

class CallTree():
    """
    Represents the call tree for a program.  Each function maps to a set
    of the functions that it calls.  The call tree is a directed graph which
    may contain cycles.
    """
    def __init__( self ):
        self.tree = defaultdict( lambda: set() )

    def add( self, caller, callee ):
        self.tree[ caller ].add( callee )

    def addAll( self, caller, callees ):
        self.tree[ caller ] |= callees

    def functions( self ):
        return self.tree.keys()

    def calls( self, caller ):
        return self.tree[ caller ]

def merge_call_trees( subtrees ):
    """
    Union two call trees into a single merged call tree
    """
    result = CallTree()

    for tree in subtrees:
        for caller in tree.functions():
            result.addAll( caller, tree.calls( caller ) )

    return result

def build_call_tree( translation_unit ):
    """
    Build a call tree for the given translation unit.  This is a wrapper
    function around _rec_build_call_tree which mutates the in-parameter
    in place.
    """
    result = CallTree()

    _rec_build_call_tree(
        translation_unit.cursor,
        translation_unit,
        result,
    )

    return result

def _rec_build_call_tree( node, caller, call_tree ):
    """
    Build a call tree by recursively visiting all the nodes in a given
    context.  This function mutates |call_tree| in place.
    """
    if ( node.kind == CursorKind.FUNCTION_DECL or
         node.kind == CursorKind.CXX_METHOD ):
        caller = node
    elif ( node.kind == CursorKind.CALL_EXPR ):
        if node.referenced:
            func = node.referenced

            call_tree.add( caller.get_usr(), func.get_usr() )

    for c in node.get_children():
        _rec_build_call_tree( c, caller, call_tree )
