import clang.cindex
import unittest
import parse
from pprint import pprint
import ast_helpers

from call_tree import build_call_tree

class TestCallGraph( unittest.TestCase ):
    def get_calltree( self, sourcefile ):
        index = clang.cindex.Index.create()
        tu = index.parse( sourcefile )
        call_tree = build_call_tree( tu )
        return call_tree

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

        pprint( dict( call_tree.tree ) )

        expected_call_tree = {
            'c:@F@save_the_pandas#': set( [
                'c:@F@increase_environment#',
                'c:@F@stop_deforestation#',
                'c:@F@stop_hunting#I#',
            ] ),
            'c:@F@stop_deforestation#': set(),
            'c:@F@increase_environment#': set(),
            'c:@F@stop_hunting#I#': set( [
                'malloc',
                'c:@F@printf',
            ] ),
        }

        for key in expected_call_tree.keys():
            self.assertEqual(
                call_tree.calls( key ),
                expected_call_tree[ key ],
            )

if __name__ == '__main__':
    unittest.main()
