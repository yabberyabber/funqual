"""
Defines violation types.  A violation is a problem with the program that must
be reported to the user.  Violations should be helpful to the human who has
to read them.
"""

from ast_helpers import get_human_name

class BaseViolation( object ):
    """
    Base type for all violations.  Defines the interface for a violation.
    A violation is a problem with the user's program that must be reported
    to the user.
    """
    def render_string( self, func_cursors, funptr_types,
                       aug_fun_types ):
        """
        Return a human readable string that explains to the user what the
        violation is, means, and where to look.
        """
        raise NotImplementedError( "BaseViolation.render_string" )


class AssignmentViolation( BaseViolation ):
    def __init__( self, lvalue, rvalue, cursor ):
        self.lvalue = lvalue
        self.rvalue = rvalue
        self.cursor = cursor

    def render_string( self, func_cursors, funptr_types,
                       augmented_fun_types ):
        ltype = ( augmented_fun_types.get( self.lvalue, set() ) |
                  funptr_types.get( self.lvalue, set() ) )
        rtype = ( augmented_fun_types.get( self.rvalue, set() ) |
                  funptr_types.get( self.rvalue, set() ) )

        return """Assignment violation:
    {} = {} at ({}, {})
 - lvalue is of type {}
 - rvalue is of type {}
Direct type must match.
Lvalue indirect type must be subset of rvalue indirect type""".format(
            self.lvalue, self.rvalue,
            self.cursor.location.line, self.cursor.location.column,
            str( ltype ), str( rtype ) )


class RuleViolation( BaseViolation ):
    def __init__( self, rule, call_path ):
        self.rule = rule
        self.call_path = call_path

    def render_string( self, func_cursors, funcptr_types, aug_func_types ):
        ret = "Rule violation: {0}\n".format( str( self.rule.error_string() ) )

        pretty_path = [ get_human_name( func_cursors[ func_usr ] )
                        for func_usr
                        in self.call_path ]

        pretty_path = "\n\t-calls: ".join( pretty_path )
        ret += "\tPath:   " + pretty_path

        if self.rule.message:
            ret += "\tRule-specific message: {0}\n".format( self.rule.message )
        return ret
