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

# settings for the data generation of the contour plot

import numpy as np

T = 1.
As = 1.0
#Au = 100.0
Au = 2.0

dx = 1./250
nbits = 3000

tau_range = np.arange(-1.5*T, 1.5*T, 3*T*dx)
phi_range = np.arange(-np.pi, np.pi, 2*np.pi*dx)
