# Copyright 2013-2014 Matthias Wilhelm

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

import matplotlib as mpl
import matplotlib.pyplot as plt

class Style(object):
	def __init__(self):
		pass

class Style1col(Style):

	def apply(self, mode, content, wide):
		mpl.rc_file('../rc/1fig-contour-rc.txt')


	def annotate(self, mode, content, wide):
		if wide:
			self._annotate_wide()
		else:
			self._annotate()


	def _annotate(self):
		plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 1), xytext=(-1.25, 3), color='w', fontsize=8,
				arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='w'))

	def _annotate_wide(self):
		plt.annotate(r'$\delta_\mathrm{SIR}$', xy=(-0.25, 1), xytext=(-2.75, 1.35), color='w', fontsize=8,
				arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color='w'))

