#!/usr/bin/env python3

# This file contains useful functions for ipython notebooks

from IPython import get_ipython

def in_notebook():
    try:
        ipy_str = str(type(get_ipython()))
        if 'zmqshell' in ipy_str or 'terminal' in ipy_str:
            return True
        else:
            return False
    except:
        return False