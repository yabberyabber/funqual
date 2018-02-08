from collections import defaultdict 
from ast_helpers import get_human_name

class Rule( object ):
    def check( self, call_tree, func_tags, func_cursors ):
        raise NotImplementedError( "Child class should override this" )

class RuleRestrictIndirectCall( Rule ):
    def __init__( self, caller_tag, callee_tag, message="" ):
        self.caller_tag = caller_tag
        self.callee_tag = callee_tag
        self.message = message

    def __str__( self ):
        return "restruct_indirect_call({0}, {1})".format( self.caller_tag,
                                                          self.callee_tag )

    def error_string( self ):
        return "`{0}` function indirectly called from `{1}` context".format(
                    self.callee_tag,
                    self.caller_tag )

    def check( self, call_tree, func_tags, func_cursors ):
        caller_funcs = set()
        for caller_func, caller_tags in func_tags.items():
            if self.caller_tag in caller_tags:
                caller_funcs.add( caller_func )

        for caller_func in caller_funcs:
            for callee_func in call_tree[ caller_func ]:
                yield from self._check_func( callee_func, call_tree,
                                             func_tags, func_cursors,
                                             [ caller_func ] )

    def _check_func( self, curr, call_tree, func_tags,
                     func_cursors, path ):
        if self.callee_tag in func_tags[ curr ]:
            yield Violation( self,
                             path + [ curr ] )

        for callee_func in call_tree[ curr ]:
            if callee_func not in path:
                yield from self._check_func( callee_func, call_tree,
                                             func_tags, func_cursors,
                                             path + [ curr ] )


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

    def check( self, call_tree, func_tags, func_cursors ):
        to_check = []
        for func, tags in func_tags.items():
            if self.caller_tag in tags:
                to_check.append( func )

        for caller_func in to_check:
            for callee_func in call_tree[ caller_func ]:
                if self.callee_tag not in func_tags[ callee_func ]:
                    yield Violation( self,
                                     [ caller_func, callee_func ] )

class Violation( object ):
    def __init__( self, rule, call_path ):
        self.rule = rule
        self.call_path = call_path

    def render_string( self, func_cursors ):
        ret = "Rule violation: {0}\n".format( str( self.rule.error_string() ) )

        pretty_path = [ get_human_name( func_cursors[ func_usr ] )
                        for func_usr
                        in self.call_path ]

        pretty_path = "\n\t-calls: ".join( pretty_path )
        ret += "\tPath:   " + pretty_path

        if self.rule.message:
            ret += "\tRule-specific message: {0}\n".format( self.rule.message )
        return ret


def idx_or_default( arr, idx, default ):
    try:
        return arr[idx]
    except IndexError:
        return default

def parse_rules_file( filename ):
    tags = defaultdict(lambda: set())
    rules = []

    with open( filename, "r" ) as tagsFile:
        for line in tagsFile:
            line = line.split( " " )
            if line[ 0 ] == "tag":
                tags[ line[ 1 ] ].add( line[ 2 ].strip() )
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
