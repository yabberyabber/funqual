import sys
import clang.cindex
from clang.cindex import CursorKind
import pdb
import pprint
from collections import defaultdict
from optparse import OptionParser
from rules import RuleRestrictIndirectCall, RuleRequireCall, parse_rules_file
from ast_helpers import dump_ast, get_qualifiers

pp = pprint.PrettyPrinter()

"A mapping of function-name to its qualifiers"
func_tags = defaultdict(lambda: set())
"A mapping of function-name to the canonical cursor"
func_cursors = {}
"A mapping of function-name to the functions it calls"
call_tree = defaultdict(lambda: set())

rules = []

def main( filename, tagsfile ):
    index = clang.cindex.Index.create()
    tu = index.parse( filename )
    print( "Translation unit: ", tu.spelling )
    dump_ast( tu.cursor)
    print()
    grab_funcs( tu.cursor )
    print()
    build_call_tree( tu.cursor, tu )
    print()

    rules = []
    if tagsfile.tags_file:
        external_tags, rules = parse_rules_file( tagsfile.tags_file )

        for func, tagset in external_tags.items():
            func_tags[ func ].update( tagset )

    pp.pprint( func_tags )
    pp.pprint( call_tree )

    for rule in rules:
        for violation in rule.check( call_tree, func_tags, func_cursors ):
            print()
            print( violation.render_string( func_cursors ) )

def grab_funcs( node ):
    """
    Populate the funcs data structure
    """
    if ( node.kind == CursorKind.FUNCTION_DECL or
         node.kind == CursorKind.CXX_METHOD ):
        full_name = node.get_usr()
        qualifiers = get_qualifiers( node )

        print( "Found %s [line=%s, col=%s of %s] -> %s" %
               ( node.get_usr(), node.location.line,
                 node.location.column, node.location.file,
                 str( get_qualifiers( node ) ) ) )

        if full_name not in func_tags:
            func_tags[ full_name ] = qualifiers

        if func_tags[ full_name ] != qualifiers:
            print( "ERROR: MULTIPLE CONFLICTING DEFINITIONS OF %s" %
                   ( full_name ) )

        func_cursors[ full_name ] = node.canonical

    for c in node.get_children():
        grab_funcs( c )

def build_call_tree( node, caller ):
    if ( node.kind == CursorKind.FUNCTION_DECL or
         node.kind == CursorKind.CXX_METHOD ):
        caller = node

    if ( node.kind == CursorKind.CALL_EXPR ):
        print( "Function %s called from %s" %
               ( node.referenced.get_usr(),
                 caller.get_usr() ) )
        call_tree[ caller.get_usr() ].add( node.referenced.get_usr() )

    for c in node.get_children():
        build_call_tree( c, caller )

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option( "-t", "--tags-file", dest="tags_file",
                       help="Name of file containing extra function qualifiers",
                       metavar="FILE", default=None )

    ( options, args ) = parser.parse_args()

    main( args[0], options )
