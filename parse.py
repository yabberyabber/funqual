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

def main( files, tagsfile ):
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


    ext_types, type_rules = rules.parse_rules_file( sys.argv[ 2 ] )

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

    all_func_types = scrapers.merge_disjoint_dicts( 
            [ aug_func_types, funcptr_types ] )

    assignment_violations = check_assignments(
            assignments, funcptr_types, func_types )

    rule_violations = check_rules(
            call_tree, all_func_types, type_rules )

    for violation in chain( assignment_violations, rule_violations ):
        print(
                violation.render_string(
                    cursors, funcptr_types, func_types ) )
        print()

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option( "-t", "--tags-file", dest="tags_file",
                       help="Name of file containing extra function qualifiers",
                       metavar="FILE", default=None )

    ( options, args ) = parser.parse_args()

    main( args, options )
