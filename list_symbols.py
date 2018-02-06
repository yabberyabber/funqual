import sys
import clang.cindex
from clang.cindex import CursorKind
import pdb
import pprint
from collections import defaultdict
from optparse import OptionParser

def main( options, args ):
    index = clang.cindex.Index.create()
    tu = index.parse( args[0] )
    dump_func( tu.cursor, args[0], options )

def dump_func( node, filename, options ):
    """
    Dump all the unified symbol resolution strings for the functions
    in the given ast
    """

    if node.kind == CursorKind.TRANSLATION_UNIT:
        for child in node.get_children():
            dump_func( child, filename, options )
        return

    if ( options.no_decl == False and
         not ( options.no_includes and node.location.file.name != filename ) ):
        if ( node.kind == CursorKind.FUNCTION_DECL or
             node.kind == CursorKind.CXX_METHOD ):
            print( "Found function declaration %s on line %d.  USR: %s" %
                   ( node.spelling, node.location.line, node.get_usr() ) )

    if options.no_call == False:
        if ( node.kind == CursorKind.CALL_EXPR ):
            print( "Found function use %s on line %d.  USR: %s" %
                   ( node.spelling, int( node.location.line ), node.referenced.get_usr() ) )

    for child in node.get_children():
        dump_func( child, filename, options )

if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option( "", "--no-includes", dest="no_includes",
                       help="Skip definitions in included files",
                       action="store_true", default=False )

    parser.add_option( "", "--no-decl", dest="no_decl",
                       help="Don't report USR for function declarations",
                       action="store_true", default=False )

    parser.add_option( "", "--no-call", dest="no_call",
                       help="Don't report USR for function calls",
                       action="store_true", default=False )

    ( options, args ) = parser.parse_args()

    main( options, args )

