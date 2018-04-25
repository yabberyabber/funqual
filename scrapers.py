#!/usr/bin/env python3

import sys
from clang.cindex import CursorKind
from ast_helpers import get_translation_unit
from collections import defaultdict

class AnnotationKind:
    DIRECT = 1
    INDIRECT = 2

def parse_annotation( annotation ):
    """
    Parse an annotation.  If it starts with a known prefix, return
    a tuple of (type, annotation).  Otherwise, return None
    """
    annotation = annotation.split( "::" )
    if len( annotation ) != 2:
        return None
    if annotation[ 0 ] == 'funqual':
        return ( AnnotationKind.DIRECT, annotation[ 1 ] )
    if annotation[ 0 ] == 'funqual_indirect':
        return ( AnnotationKind.INDIRECT, annotation[ 1 ] )
    return None


def get_qualifiers( node ):
    """
    Given a node, return the set of all its explicit qualifiers
    """
    qualifiers = set()

    for child in node.get_children():
        if child.kind == CursorKind.ANNOTATE_ATTR:
            if parse_annotation( child.displayname ):
                qualifiers.add( parse_annotation( child.displayname ) )

    return qualifiers


def merge_disjoint_dicts( dicts ):
    """
    Merge a list of dictionaries where none of them share any keys
    """
    result = {}

    for mapping in dicts:
        for key, value in mapping.items():
            if key in result:
                raise Exception(
                        "key `{}` defined in two dictionaries".format(
                            key ) )
            results[ key ] = value

    return result


class FunctionPointers:
    @staticmethod
    def scrape( tu ):
        """
        Given a translation unit, scrape a mapping of function pointers to their
        qualified types
        """
        funptrs = {}

        for trav in tu.cursor.walk_preorder():
            if trav.kind == CursorKind.VAR_DECL:
                funptrs[ trav.get_usr() ] = get_qualifiers( trav )

        return funptrs

    merge = merge_disjoint_dicts


class FunctionQualifiers():
    """
    Contains helper methods for scraping the function qualifiers out of
    a set of translation units
    """
    @staticmethod
    def scrape( tu ):
        """
        Given a translation unit, scrape a mapping of function/methods to their
        qualified types (direct type only)
        """
        func_tags = defaultdict( lambda: set() )

        for trav in tu.cursor.walk_preorder():
            if trav.kind in [ CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD ]:
                full_name = trav.get_usr()
                qualifiers = get_qualifiers( trav )

                func_tags[ full_name ] |= qualifiers

        return dict( func_tags ) 

    @staticmethod
    def merge( mappings ):
        func_tags = defaultdict( lambda: set() )

        for mapping in mappings:
            for symbol, qualifiers in mapping:
                func_tags[ symbol ] |= qualifiers

        return dict( func_tags )


class FunctionCursors:
    """
    Contains helper methods for scraping the function cursors out of a
    set of translation units
    """

    @staticmethod
    def scrape( tu ):
        """
        Given a translation unit, scrape a mapping of function usr to the 
        cannonical cursor (we need to be able to retrieve the cursor later
        for error reporting)
        """
        func_cursors = {}

        for trav in tu.cursor.walk_preorder():
            if trav.kind in [ CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD ]:
                full_name = trav.get_usr()
                cursor = trav.canonical

                func_cursors[ full_name ] = cursor

        return func_cursors

    merge = merge_disjoint_dicts


class Overrides:
    """
    Contains helper methods for scrapping function overrides out of a
    translation unit and merging together override mappings from
    multiple translation units.
    """
    @staticmethod
    def scrape( tu ):
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

    @staticmethod
    def merge( override_maps ):
        """
        Merge two override maps
        """
        result = defaultdict( lambda: set() )

        for override_map in override_maps:
            for key, val in override_map.items():
                result[ key ] |= val

        return result


class FunPtrAssignments:
    """
    Scrapes the assignments of function pointers
    """
    @classmethod
    def get_operator( cls, binop_node ):
        """
        Cheap hack to get the binary operator out of a clang expression
        because clang doesn't expose the binop interface to the python
        api
        """
        return [ x.spelling for x in binop_node.get_tokens() ][1]


    @classmethod
    def get_lvalue( cls, binop_node ):
        "Cheap hack to get lvalue from binop expression"
        return [ x for x in binop_node.get_children() ][ 0 ].referenced


    @classmethod
    def get_rvalue( cls, binop_node ):
        "Cheap hack to get rvalue from binop expression"
        return [ x for x in binop_node.get_children() ][ 1 ].referenced


    @classmethod
    def is_lvalue_funptr( cls, binop_node ):
        "Check whether the lvalue of this operation is a function pointer"

        if '(*)' in cls.get_lvalue( binop_node ).type.spelling:
            return True
        else:
            return False


    @classmethod
    def scrape( cls, tu ):
        """
        Scrape a single translation unit for all assignments into function
        pointers.  Grab usr so they can be typechecked.
        Return list of tuples in the following format:
          ( lvalue usr, rvalue usr, cursor of assignment for error reporting )
        """
        results = []

        for trav in tu.cursor.walk_preorder():
            if ( trav.kind == CursorKind.BINARY_OPERATOR and
                 len( list( trav.get_children() ) ) == 2 ):
                try:
                    if ( cls.get_operator( trav ) == '=' and
                         cls.is_lvalue_funptr( trav ) ):
                        results.append(
                                ( cls.get_lvalue( trav ).get_usr(),
                                  cls.get_rvalue( trav ).get_usr(),
                                  trav.canonical ) )
                except:
                    pass

        return results

    @classmethod
    def merge( cls, lists_of_assignments ):
        """
        Takes the result of scraping several translation units
        and merges the results into one list
        """

        results = []

        for list_of_assignments in lists_of_assignments:
            for assignment in list_of_assignments:
                results.append( assignment )

        return results


if __name__ == '__main__':
    from pprint import pprint

    target = get_translation_unit( sys.argv[ 2 ] )

    if sys.argv[ 1 ] == 'ptr':
        pprint( FunctionPointers.scrape( target ) )
    elif sys.argv[ 1 ] == 'qual':
        pprint( FunctionQualifiers.scrape( target ) )
    elif sys.argv[ 1 ] == 'override':
        pprint( Overrides.scrape( target ) )
    elif sys.argv[ 1 ] == 'assignment':
        pprint( FunPtrAssignments.scrape( target ) )