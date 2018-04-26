#!/usr/bin/env python3

"""
The goal of this file is to check all the assignments given.  This module
relies on the scraping provided by other modules.
"""

import sys
from scrapers import AnnotationKind
from violation import AssignmentViolation

def split_type( usr, funptr_types, augmented_fun_types ):
    """
    Split the type of a function into its direct and indirect constituents
    """

    return (
            set( [ name
                   for ( kind, name )
                   in funptr_types.get( usr, set() ) |
                      augmented_fun_types.get( usr, set() )
                   if kind == AnnotationKind.DIRECT ] ),
            set( [ name 
                   for ( kind, name )
                   in funptr_types.get( usr, set() ) |
                      augmented_fun_types.get( usr, set() )
                   if kind == AnnotationKind.INDIRECT ] ) )


def check_assignments( assignments, funptr_types, augmented_fun_types ):
    """
    Check all the assignments in the given list of assignments.  Takes in
    a list of assignments, a mapping of function pointer usr's to their 
    qualified types, and a list of augmented function types (where indirect
    calls have been added post-scrape).  Reports an error for any
    assignments that do not follow the conventions given.
    """
    for lvalue, rvalue, cursor in assignments:
        lvalue_direct_type, lvalue_indirect_type = split_type(
                lvalue, funptr_types, augmented_fun_types )
        rvalue_direct_type, rvalue_indirect_type = split_type(
                rvalue, funptr_types, augmented_fun_types )

        # direct types must match
        # right indirect type must be subset of left indirect type
        if ( lvalue_direct_type != rvalue_direct_type or
             not rvalue_indirect_type.issubset( lvalue_indirect_type ) ):
            yield AssignmentViolation( lvalue, rvalue, cursor )


if __name__ == '__main__':
    import scrapers
    import call_tree
    from ast_helpers import get_translation_unit
    from type_augmentor import augment_types

    target = get_translation_unit( sys.argv[ 1 ] )

    call_tree = call_tree.build_call_tree( target )
    overrides = scrapers.Overrides.scrape( target )
    func_cursors = scrapers.FunctionCursors.scrape( target )
    func_types = scrapers.FunctionQualifiers.scrape( target )
    funcptr_types = scrapers.FunctionPointers.scrape( target )
    assignments = scrapers.FunPtrAssignments.scrape( target )

    call_tree.augment_with_overrides( overrides )

    func_types = augment_types( call_tree, funcptr_types, func_types )

    assignment_violations = check_assignments(
            assignments, funcptr_types, func_types )

    for violation in assignment_violations:
        print(
                violation.render_string(
                    func_cursors, funcptr_types, func_types ) )
        print()
