# Copyright 2013 Matthias Wilhelm

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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