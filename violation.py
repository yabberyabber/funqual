"""
Defines violation types.  A violation is a problem with the program that must
be reported to the user.  Violations should be helpful to the human who has
to read them.
"""

from ast_helpers import get_human_name
from scrapers import AnnotationKind

class BaseViolation( object ):
    """
    Base type for all violations.  Defines the interface for a violation.
    A violation is a problem with the user's program that must be reported
    to the user.
    """
    def render_string( self, func_cursors, fun_types ):
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

    def render_string( self, func_cursors, fun_types ):
        ltype = fun_types.get( self.lvalue, set() )
        rtype = fun_types.get( self.rvalue, set() )

        return """Assignment violation:
    {} = {} at ({}, {})
 - lvalue has type
    - Direct: {}
    - Indirect: {}
 - rvalue has type
    - Direct: {}
    - Indirect: {}
Direct type must match.
Lvalue indirect type must be subset of rvalue indirect type""".format(
            self.lvalue, self.rvalue,
            self.cursor.location.line, self.cursor.location.column,
            set( [ x[1] for x in ltype if x[0] == AnnotationKind.DIRECT ] ),
            set( [ x[1] for x in ltype if x[0] == AnnotationKind.INDIRECT ] ),
            set( [ x[1] for x in rtype if x[0] == AnnotationKind.DIRECT ] ),
            set( [ x[1] for x in rtype if x[0] == AnnotationKind.INDIRECT ] ) )


class RuleViolation( BaseViolation ):
    def __init__( self, rule, call_path ):
        self.rule = rule
        self.call_path = call_path

    def render_string( self, func_cursors, fun_types ):
        ret = "Rule violation: {0}\n".format( str( self.rule.error_string() ) )

        pretty_path = [ get_human_name( func_cursors[ func_usr ] )
                        for func_usr
                        in self.call_path ]

        pretty_path = "\n\t-calls: ".join( pretty_path )
        ret += "\tPath:   " + pretty_path

        if self.rule.message:
            ret += "\tRule-specific message: {0}\n".format( self.rule.message )
        return ret


class OverrideViolation( BaseViolation ):
    def __init__( self, overridden_method, overrider_method ):
        self.overridden_method = overridden_method
        self.overrider_method = overrider_method

    def render_string( self, func_cursors, fun_types ):
        overridden_name = get_human_name( func_cursors[ self.overridden_method ] )
        overrider_name = get_human_name( func_cursors[ self.overrider_method ] )

        overridden_type = fun_types.get( self.overridden_method, set() )
        overrider_type = fun_types.get( self.overrider_method, set() )

        return """Override Violation:
\t{} overrides {} but their direct types don't match.
\t - {} has type {}
\t - {} has type {}
""".format( overrider_name, overridden_name,
            overrider_name, 
            set( [ x[1] for x in overrider_type if x[0] == AnnotationKind.DIRECT ] ),
            overridden_name,
            set( [ x[1] for x in overridden_type if x[0] == AnnotationKind.DIRECT ] ) )
