from collections import defaultdict 

class Rule( object ):
    def check( self, call_tree, func_tags, func_cursors ):
        raise NotImplementedError( "Child class should override this" )

class RuleRestrictIndirectCall( Rule ):
    def __init__( self, caller_tag, callee_tag, message="" ):
        self.caller_tag = caller_tag
        self.callee_tag = callee_tag
        self.message = message

    def check( self, call_tree, func_tags, func_cursors ):
        pass

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
        return "require_call {0} {1}".format( self.caller_tag,
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
        ret = "Rule violation: {0}\n".format( str( self.rule ) )

        pretty_path = [ "{0} (line {1}, col {2} in {3})".format(
                           func_usr,
                           func_cursors[ func_usr ].location.line,
                           func_cursors[ func_usr ].location.column,
                           func_cursors[ func_usr ].location.file
                        )
                        for func_usr
                        in self.call_path ]

        pretty_path = "\n\t   -> ".join( pretty_path )
        ret += "\tPath: " + pretty_path

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
                if line[ 1 ] == "restrict_indirect":
                    rules.append(
                            RuleRestrictIndirectCall(
                                line[ 2 ].strip(), line[ 3 ].strip(),
                                idx_or_default( line, 4, "" ).strip() ) )
                elif line[ 1 ] == "require_call":
                    rules.append(
                            RuleRequireCall(
                                line[ 2 ].strip(), line[ 3 ].strip(),
                                idx_or_default( line, 4, "" ).strip() ) )

    return dict( tags ), rules
