import os
import sys

def get_params(input_params):
    params = []

    for var, choices, prompt in input_params:
        resp = None
        while resp not in choices:
            resp = raw_input(prompt+' '+repr(choices) +'? ').lower()
        params.append(resp)

    return params

def overwrite_ok(filepath):
    # Since the computations are quite long, make sure that existing results should really be deleted!
    if os.path.exists(filepath):
        print("The file already exists!")
        resp = None
            
        while resp not in ('yes', 'no', 'y', 'n'):
            resp = raw_input('Do you want to continue (y/n)? ').lower()
                        
        if resp not in ('yes', 'y'):
            return False

    return True

def osx_notify():
    try:
        from osax import OSAX
    except:
        print 'appscript not installed ...' 

    sa = OSAX()
    sa.activate()
    sa.display_dialog('%s: computations are finished!' % (sys.argv[0]))