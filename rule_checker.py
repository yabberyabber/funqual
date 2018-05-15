#!/usr/bin/env python3

import sys
from violation import RuleViolation


def check_rules( call_tree, func_types, rules, standard_funcs ):
    """
    Given a program call tree, a mapping from function to its type, and
    a set of rules, apply each rule and return all the rule violations
    """
    for rule in rules:
        yield from rule.check( call_tree, func_types, standard_funcs )


if __name__ == '__main__':
    import scrapers
    import call_tree
    from ast_helpers import get_translation_unit
    from type_augmentor import augment_types
    from rules import parse_rules_file
    from pprint import pprint

    ext_types, rules = parse_rules_file( sys.argv[ 2 ] )
    target = get_translation_unit( sys.argv[ 1 ] )

    call_tree = call_tree.build_call_tree( target )
    overrides = scrapers.Overrides.scrape( target )
    func_cursors = scrapers.FunctionCursors.scrape( target )
    func_types = scrapers.merge_disjoint_dicts( [
            scrapers.FunctionQualifiers.scrape( target ),
            ext_types ] )
    standard_funcs = set( func_types.keys() )
    funcptr_types = scrapers.FunctionPointers.scrape( target )
    assignments = scrapers.FunPtrAssignments.scrape( target )

    call_tree.augment_with_overrides( overrides )

    aug_func_types = augment_types( call_tree, funcptr_types, func_types )

    all_func_types = scrapers.merge_disjoint_dicts(
            [ aug_func_types, funcptr_types ] )

    rule_violations = check_rules(
            call_tree, all_func_types, rules, standard_funcs )

    for violation in rule_violations:
        print(
                violation.render_string(
                    func_cursors, funcptr_types, aug_func_types ) )
        print()
