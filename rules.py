from collections import defaultdict 
from ast_helpers import get_human_name
from violation import RuleViolation
from scrapers import AnnotationKind


class Rule( object ):
    def check( self, call_tree, func_tags, standard_funcs ):
        raise NotImplementedError( "Child class should override this" )


class RuleRestrictIndirectCall( Rule ):
    def __init__( self, caller_tag, callee_tag, message="" ):
        self.caller_tag = caller_tag
        self.callee_tag = callee_tag
        self.message = message

    def __str__( self ):
        return "restrict_indirect_call({0}, {1})".format( self.caller_tag,
                                                          self.callee_tag )

    def error_string( self ):
        return "`{0}` function indirectly called from `{1}` context".format(
                    self.callee_tag,
                    self.caller_tag )

    def check( self, call_tree, func_tags, standard_funcs ):
        caller_funcs = set()
        for caller_func, caller_tags in func_tags.items():
            if self.caller_tag in direct_type( caller_tags ):
                caller_funcs.add( caller_func )

        for caller_func in caller_funcs:
            for callee_func in call_tree.calls( caller_func ):
                yield from self._check_func( callee_func, call_tree,
                                             func_tags,
                                             [ caller_func ],
                                             standard_funcs )

    def _check_func( self, curr, call_tree, func_tags,
                     path, standard_funcs ):
        if curr in standard_funcs:
            # curr is a standard func and not a funcptr
            # then we ignore indirect type
            if self.callee_tag in direct_type( func_tags.get( curr, set() ) ):
                yield RuleViolation( self,
                                     path + [ curr ] )
        else:
            # curr is a funptr so we do look at indirect type
            if ( self.callee_tag in direct_type( func_tags.get( curr, set() ) )
                 or
                 self.callee_tag in indirect_type(
                     func_tags.get( curr, set() ) ) ):
                yield RuleViolation( self,
                                     path + [ curr ] )


        for callee_func in call_tree.calls( curr ):
            if callee_func not in path:
                yield from self._check_func( callee_func, call_tree,
                                             func_tags,
                                             path + [ curr ],
                                             standard_funcs )


class RuleRequireCall( Rule ):
    """
    With this rule type, functions with the tag |caller_tag| may *only*
    call functions with |callee_tag|.  
    """
    def __init__( self, caller_tag, callee_tag, message="" ):
        self.caller_tag = caller_tag
        self.callee_tag = callee_tag
        self.message = message

    def __str__( self ):
        return "require_call({0}, {1})".format( self.caller_tag,
                                                self.callee_tag )

    def error_string( self ):
        return "`{1}` function calls a function that is not `{1}`".format(
                    self.caller_tag,
                    self.callee_tag )

    def check( self, call_tree, func_tags, standard_funcs ):
        to_check = []
        for func, tags in func_tags.items():
            if self.caller_tag in direct_type( tags ):
                to_check.append( func )

        for caller_func in to_check:
            for callee_func in call_tree.calls( caller_func ):
                if ( self.callee_tag not in
                     direct_type( func_tags[ callee_func ] ) ):
                    yield RuleViolation( self,
                                         [ caller_func, callee_func ] )


def idx_or_default( arr, idx, default ):
    """
    Like arr.get( idx, default ) except that arr is a list and lists
    don't have a get attribute
    """
    try:
        return arr[idx]
    except IndexError:
        return default


def parse_rules_file( filename ):
    """
    Given a rules file, parse out all the rule definitions and external
    function taggings
    """
    tags = defaultdict(lambda: set())
    rules = []

    with open( filename, "r" ) as tagsFile:
        for line in tagsFile:
            line = line.split( " " )
            if line[ 0 ] == "tag":
                tags[ line[ 1 ] ].add(
                        (AnnotationKind.DIRECT, line[ 2 ].strip() ) )
            elif line[ 0 ] == "rule":
                if line[ 1 ] == "restrict_indirect_call":
                    rules.append(
                            RuleRestrictIndirectCall(
                                line[ 2 ].strip(), line[ 3 ].strip(),
                                idx_or_default( line, 4, "" ).strip() ) )
                elif line[ 1 ] == "require_call":
                    rules.append(
                            RuleRequireCall(
                                line[ 2 ].strip(), line[ 3 ].strip(),
                                idx_or_default( line, 4, "" ).strip() ) )
                else:
                    print( "Could not interpret line: {0}".format( line ) )

    return dict( tags ), rules


def direct_type( types ):
    return set( [
        name
        for ( kind, name )
        in types
        if kind == AnnotationKind.DIRECT ] )


def indirect_type( types ):
    return set( [
        name
        for ( kind, name )
        in types
        if kind == AnnotationKind.INDIRECT ] )
