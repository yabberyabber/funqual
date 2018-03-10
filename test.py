import clang.cindex
from clang.cindex import CursorKind, TranslationUnit
import unittest
import parse
from pprint import pprint
import ast_helpers
import override_scraper
from call_tree import build_call_tree

class TestCallGraph( unittest.TestCase ):
    def test_callgraph_simple( self ):
        call_tree = self.get_calltree( 'test_cases/1/main.cpp' )

        self.assertEqual(
            dict( call_tree.tree ),
            {
                'c:@F@main#': set( [ 'c:@F@do_stuff#' ] ),
                'c:@F@do_stuff#': set( [ 'c:@F@save_the_pandas#' ] ),
            },
        )

    def test_callgraph_complex( self ):
        call_tree = self.get_calltree( 'test_cases/1/alt.cpp' )

        expected_call_tree = {
            'c:@F@save_the_pandas#': set( [
                'c:@F@increase_environment#',
                'c:@F@stop_deforestation#',
                'c:@F@stop_hunting#I#',
            ] ),
            'c:@F@stop_deforestation#': set(),
            'c:@F@increase_environment#': set(),
            'c:@F@stop_hunting#I#': set( [
                'c:@F@malloc',
                'c:@F@printf',
            ] ),
        }

        self.assertCallTreeMatch( call_tree, expected_call_tree )

    def test_methods_inherited( self ):
        """
        We should be able to detect calling of constructors and
        using object methods
        """
        call_tree = self.get_calltree( 'test_cases/2/main.cpp' )
        call_tree.augment_with_overrides( get_overrides( 'test_cases/2/main.cpp' ) )

        expected_call_tree = {
            'c:@F@main#': set( [
                'c:@S@Panda@F@Feed#I#',
                'c:@S@RedPanda@F@Feed#I#',
                'c:@S@RedPanda@F@RedPanda#',
            ] ),
            'c:@S@Panda@F@Feed#I#': set( [
                'c:@F@printf',
            ] ),
            'c:@S@RedPanda@F@Feed#I#': set( [
                'c:@F@malloc',
                'c:@F@printf',
            ] ),
        }

        self.assertCallTreeMatch( call_tree, expected_call_tree )

    def get_calltree( self, sourcefile ):
        """
        Open the given source file, parse it, and determine the call tree
        """
        index = clang.cindex.Index.create()
        tu = index.parse( sourcefile )
        call_tree = build_call_tree( tu )
        return call_tree

    def assertCallTreeMatch( self, call_tree, expectation ):
        """
        Assert that for the functions defined in |expectation|, the
        correspondings functions are populated similarly in |call_tree|
        """
        for key in expectation.keys():
            self.assertEqual(
                call_tree.calls( key ),
                expectation[ key ],
            )

class TestOverrides( unittest.TestCase ):
    def test_basic_inheritance_override( self ):
        overrides = get_overrides( 'test_cases/2/main.cpp' )

        self.assertEqual( dict( overrides ), {
            'c:@S@Panda@F@Feed#I#': set( [ 'c:@S@RedPanda@F@Feed#I#' ] ),
        } )

    def test_multilevel_inheritance_override( self ):
        overrides = get_overrides(
                'test_cases/3/main.cpp', 'test_cases/3/Panda.cpp',
                'test_cases/3/DomesticRedPanda.cpp',
                'test_cases/3/RedPanda.cpp',
                'test_cases/3/TrashPanda.cpp', )

        self.assertEqual( overrides[ 'c:@S@Panda@F@Feed#I#' ],
                          set( [
                              'c:@S@DomesticRedPanda@F@Feed#I#',
                              'c:@S@RedPanda@F@Feed#I#',
                              'c:@S@TrashPanda@F@Feed#I#',
                          ] ) )
        
def get_overrides( *sourcefiles ):
    """
    Open the given source file, parse it and determine the overrides map
    """
    overrides = [
        override_scraper.get_overrides(
            ast_helpers.get_translation_unit(
                sourcefile ) )
        for sourcefile
        in sourcefiles
    ]

    return override_scraper.merge( overrides )


if __name__ == '__main__':
    unittest.main()
