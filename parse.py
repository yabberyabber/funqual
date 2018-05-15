#!/usr/bin/env python3

import sys
import logging
import pdb
from itertools import chain
from pprint import pprint, pformat
from collections import defaultdict
from optparse import OptionParser
import rules
import scrapers
import ast_helpers
from call_tree import build_call_tree, merge_call_trees
from type_augmentor import augment_types
from assignment_checker import check_assignments
from rule_checker import check_rules

logging.basicConfig( filename="dbg_output", filemode="w", level=logging.DEBUG )

def scrape_all_files( files, ext_types ):
    call_subtrees = []
    override_subtrees = []
    cursor_subsets = []
    func_type_subsets = []
    funcptr_type_subsets = []
    assignment_subsets = []

    for fname in files:
        target = ast_helpers.get_translation_unit( fname )

        logging.info( "Translation unit: " + str( target.spelling ) )
        ast_helpers.dump_ast( target.cursor, lambda x: logging.debug(x) )

        call_subtrees.append(
                build_call_tree( target ) )
        override_subtrees.append(
                scrapers.Overrides.scrape( target ) )
        cursor_subsets.append(
                scrapers.FunctionCursors.scrape( target ) )
        func_type_subsets.append(
                scrapers.FunctionQualifiers.scrape( target ) )
        funcptr_type_subsets.append(
                scrapers.FunctionPointers.scrape( target ) )
        assignment_subsets.append(
                scrapers.FunPtrAssignments.scrape( target ) )

    call_tree = merge_call_trees(
            call_subtrees )
    overrides = scrapers.Overrides.merge(
            override_subtrees )
    cursors = scrapers.FunctionCursors.merge(
            cursor_subsets )
    func_types = scrapers.FunctionQualifiers.merge(
            func_type_subsets + [ ext_types ] )
    funcptr_types = scrapers.FunctionPointers.merge(
            funcptr_type_subsets )
    assignments = scrapers.FunPtrAssignments.merge(
            assignment_subsets )

    call_tree.augment_with_overrides( overrides )

    aug_func_types = augment_types( call_tree, funcptr_types, func_types )
    standard_funcs = set( [ key for key in func_types.keys() ] )

    all_func_types = scrapers.merge_disjoint_dicts( 
            [ aug_func_types, funcptr_types ] )

    return call_tree, all_func_types, cursors, assignments, standard_funcs

def get_violations( files, tagsfile ):

    ext_types, type_rules = rules.parse_rules_file( tagsfile )

    ( call_tree, all_func_types, cursors,
      assignments, standard_funcs ) = scrape_all_files( files, ext_types )

    rule_violations = check_rules(
            call_tree, all_func_types, type_rules, standard_funcs )

    assignment_violations = check_assignments(
            assignments, all_func_types )

    return ( cursors, all_func_types,
             chain( assignment_violations, rule_violations ) )

def main( files, tagsfile ):
    cursors, types, violations = get_violations( files, tagsfile )

    for violation in violations:
        print(
                violation.render_string(
                    cursors, types ) )
        print()

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option( "-t", "--tags-file", dest="tags_file",
                       help="Name of file containing extra function qualifiers",
                       metavar="FILE", default=None )

    ( options, args ) = parser.parse_args()

    main( args, options.tags_file )
