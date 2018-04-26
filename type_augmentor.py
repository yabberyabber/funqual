#!/usr/bin/env python3

"""
The goal of this module is to take the explicit qualified type information of
a set of functions as well as a call tree and to expand the type information
to include implicit type information.  The following rules apply:
 - A function with direct type X also has indirect type X
 - A function that calls a function with indirect type X also has indirect type X
"""

import sys
from scrapers import AnnotationKind


def determine_indirect_type( function, call_tree,
                             funptr_types, function_types ):
    """
    For the given function, determine its indirect type by recursively
    walking the call tree and colleting function types that are indirectly
    called by this function
    """
    visited = set( [ function ] )
    qualifiers = set()

    for child in call_tree.calls( function ):
        qualifiers |= _rec_determine_indirect_type(
                child, call_tree, funptr_types, function_types, visited )

    return qualifiers


def _rec_determine_indirect_type( function, call_tree, funptr_types,
                                  function_types, visited ):
    """
    Recurse the call tree starting at |function| and collecting the types
    of everything visited.  Do not recurse on |visited|.  
    """
    types = []
    types += funptr_types.get( function, [] )
    types += function_types.get( function, [] )

    for child in call_tree.calls( function ):
        if child not in visited:
            visited.add( child )
            types += _rec_determine_indirect_type(
                    child, call_tree, funptr_types, function_types,
                    visited )

    return set( [ ( AnnotationKind.INDIRECT, qual ) for ( _, qual ) in types ] )


def augment_types( call_tree, funptr_types, function_types ):
    """
    Given a call tree, the types of all function pointers, and the types of all
    functions (augmented with overrides), determine the indirect types of
    all functions and return a mapping of function to its complete type
    """
    types = {}

    for function in function_types.keys():
        indirect_types = determine_indirect_type(
                function, call_tree, funptr_types, function_types )
        direct_types = function_types[ function ]
        types[ function ] = indirect_types | direct_types

    return types


if __name__ == '__main__':
    from pprint import pprint
    import scrapers
    import call_tree
    from ast_helpers import get_translation_unit

    target = get_translation_unit( sys.argv[ 1 ] )

    call_tree = call_tree.build_call_tree( target )
    overrides = scrapers.Overrides.scrape( target )
    func_types = scrapers.FunctionQualifiers.scrape( target )
    funcptr_types = scrapers.FunctionPointers.scrape( target )

    call_tree.augment_with_overrides( overrides )

    pprint( augment_types( call_tree, funcptr_types, func_types ) )
