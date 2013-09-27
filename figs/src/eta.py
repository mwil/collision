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

from __future__ import print_function

import numpy as np
import sys
import threading
import time
import datetime as dt

class ETA(object):
    def __init__(self, steps=1):
        self.times = np.array([])
        self.steps_left = steps
        self.total_steps = steps
        self.curr_len = 0
        
        self.running = False
        self.correction = 0
        
    def __del__(self):
        self.running = False
        print('\nDone.')
        
    def start_timer(self):
        self.start_time = time.time()
    
    def stop_timer(self):
        self.steps_left -= 1
        self.correction = 0
        self.times = np.append(self.times, time.time() - self.start_time)
        
        if not self.running:
            self.running = True
            self.print_eta()
            
        if not self.steps_left:
            self.running = False
    
    def print_above(self, str):
        dlen =  self.curr_len - len(str) 
        print('\b'*self.curr_len + str +' '*dlen, end='\n')
    
    def print_eta(self):
        progress = 100.0 - ((100.0 * self.steps_left) / self.total_steps)
        eta = dt.timedelta(seconds=int(self.steps_left*np.mean(self.times))-self.correction)
        
        self.curr_len = len('Progress: %5.2f%%, time remaining: %s' % (progress, eta))
        
        print('\rProgress: %5.2f%%, time remaining: %s' % (progress, eta), end='')
        sys.stdout.flush()
        
        if self.running:
            self.correction += 1
            threading.Timer(1, self.print_eta).start()
    
if __name__ == '__main__':
    eta = ETA(steps=20)
    
    for i in xrange(20):
        eta.start_timer()
        time.sleep(5)
        eta.print_above('Blub above.')
        eta.stop_timer()
