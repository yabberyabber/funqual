#!/usr/bin/env python3

import sys
import logging
import pdb
import time
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
from overrides_checker import check_overrides
from rule_checker import check_rules

logging.basicConfig( filename="dbg_output", filemode="w", level=logging.DEBUG )

def scrape_all_files( files, ext_types, options ):
    call_subtrees = []
    override_subtrees = []
    cursor_subsets = []
    func_type_subsets = []
    funcptr_type_subsets = []
    assignment_subsets = []

    tu_time = 0.0
    start_time = time.time()

    for fname in files:
        overrideScraper = scrapers.Overrides()
        cursorScraper = scrapers.FunctionCursors()
        funcTypeScraper = scrapers.FunctionQualifiers()
        funPtrTypeScraper = scrapers.FunctionPointers()
        assScraper = scrapers.FunPtrAssignments()

        pre_tu_time = time.time()
        target = ast_helpers.get_translation_unit( fname, options )

        logging.info( "Translation unit: " + str( target.spelling ) )
        #ast_helpers.dump_ast( target.cursor, lambda x: logging.debug(x) )

        tu_time += time.time() - pre_tu_time

        scrapers.run_scrapers( target.cursor, 
                [ overrideScraper, cursorScraper,
                  funcTypeScraper, funPtrTypeScraper,
                  assScraper ] )

        call_subtrees.append(
                build_call_tree( target ) )
        override_subtrees.append(
                overrideScraper.get() )
        cursor_subsets.append(
                cursorScraper.get() )
        func_type_subsets.append(
                funcTypeScraper.get() )
        funcptr_type_subsets.append(
                funPtrTypeScraper.get() )
        assignment_subsets.append(
                assScraper.get() )

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

    pre_augment_time = time.time()
    aug_func_types = augment_types( call_tree, funcptr_types, func_types )
    post_augment_time = time.time()

    standard_funcs = set( [ key for key in func_types.keys() ] )

    all_func_types = scrapers.merge_disjoint_dicts( 
            [ aug_func_types, funcptr_types ] )

    end_time = time.time()

    if options.show_time:
        print( "time to parse: {:0.5f} seconds".format( tu_time ) )
        print( "time to scrape stuff: {:0.5f} seconds".format( 
               end_time - start_time - tu_time ) )
        print( "time to infer indirect type: {:0.5f} seconds".format(
               post_augment_time - pre_augment_time ) )

    return ( call_tree, all_func_types, cursors, assignments, standard_funcs,
             overrides )

def get_violations( files, tagsfile, options ):

    ext_types, type_rules = rules.parse_rules_file( tagsfile )

    pre_file_parse = time.time()
    ( call_tree,
      all_func_types,
      cursors,
      assignments,
      standard_funcs,
      overrides ) = scrape_all_files( files, ext_types, options )
    post_file_parse = time.time()

    rule_violations = check_rules(
            call_tree, all_func_types, type_rules, standard_funcs )
    post_rule_checking = time.time()

    assignment_violations = check_assignments(
            assignments, all_func_types )
    post_assignment_checking = time.time()

    override_violations = check_overrides(
            overrides, all_func_types )
    post_overrides_checking = time.time()

    if options.show_time:
        print( "Time to parse files: {:0.3f} Seconds".format(
            post_file_parse - pre_file_parse ) )
        print( "Time to check graph rules: {:0.5f} Seconds".format(
            post_rule_checking - post_file_parse ) )
        print( "Time to check assignments: {:0.5f} Seconds".format(
            post_assignment_checking - post_rule_checking ) )
        print( "Time to check overrides: {:0.5f} Seconds".format(
            post_overrides_checking - post_assignment_checking ) )
        print( "Functions examined (includes libraries and ptrs): {}".format(
            len( all_func_types ) ) )
        print( "Calls examined: {}".format( call_tree.size() ) )

    return ( cursors, all_func_types,
             chain( assignment_violations,
                    rule_violations,
                    override_violations ) )

def parse_args():
    parser = OptionParser()

    parser.add_option( "-t", "--tags-file", dest="tags_file",
                       help="Name of file containing extra function qualifiers",
                       metavar="FILE", default=None )

    parser.add_option( "-x", "--language", dest="language",
                       help=( "Treat input files as having this language.  "
                              + "Equivalent to clang's -x.  Try c++ or c" ),
                       metavar="LANGUAGE", default="c++" )

    parser.add_option( "-s", "--std", dest="standard",
                       help=( "Specity the language standard to compile for.  "
                              + "Equivalent to clan's -std=.  "
                              + "Try c++17 or c89" ),
                       metavar="LANGUAGE", default="c++17" )

    parser.add_option( "-I", "--include", dest="include_path",
                       help=( "Directory to be added to include search path.  "
                              + "For multiple directories, comma separate." ),
                       metavar="FILE", default=None )

    parser.add_option( "-f", dest="clang_flags",
                       help=( "any flags to be passed directly to clang "
                              + "(for multiple flags, enclose in quotes)"),
                       metavar="FLAGS", default=None )

    parser.add_option( "-v", action="store_true", dest="verbose",
                       help="Verbose mode makes more dbg output",
                       default=False )

    parser.add_option( "--time", action="store_true", dest="show_time",
                       help="Output execution time for different phases of prgm",
                       default=False )

    ( options, files ) = parser.parse_args()

    if len( sys.argv ) == 1:
        parser.print_help( sys.stderr )
        sys.exit( 0 )

    return ( options, files )

def main():
    options, files = parse_args()

    cursors, types, violations = get_violations(
            files, options.tags_file, options )

    for violation in violations:
        print(
                violation.render_string(
                    cursors, types ) )
        print()

if __name__ == '__main__':
    main()
