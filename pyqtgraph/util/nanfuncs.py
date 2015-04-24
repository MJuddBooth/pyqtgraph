'''
Created on Jan 31, 2015

@author: booth

wrapper around np.nanmin, nanmax and isfinite that support np.datetime64.

'''

import numpy as np

try:
    np.isnan(np.datetime64("2001-01-01"))
    from numpy import nanmin, nanmax, isfinite
except TypeError as e:
    try:
        from pandas.core.nanops import nanmin, nanmax
        from pandas.core.nanops import notnull as isfinite
    except ImportError as ie:
        ie.message += "will have to rewrite np.nanmin"
        raise

    
    

