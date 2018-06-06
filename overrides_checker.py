#!/usr/bin/env python3

"""
The goal of this file is to check all the overrides for direct type
consistency.  This module relies on the scraping provided by other modules.
"""

import sys
from scrapers import AnnotationKind
from rules import direct_type
from violation import OverrideViolation

def check_overrides( overrides, fun_types ):
    """
    Check all the overrides for direct type consistency
    """
    for overridden_method in overrides.keys():
        overridden_direct_type = direct_type(
                fun_types.get( overridden_method, set() ) )

        for overrider_method in overrides[ overridden_method ]:
            overrider_direct_type = direct_type(
                    fun_types.get( overrider_method, set() ) )

            if overridden_direct_type != overrider_direct_type:
                yield OverrideViolation( overridden_method,
                                         overrider_method )
