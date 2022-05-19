"""
This file is part of dreamTeam.

dreamTeam is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
"""
import trivial
import tf
import ktf
import rtf
import ptf
import dptf


def makeSolver(method):
    """
    Make a solver regarding the given option.
    """
    print("c [FACTORY] Method: ", method)
    if method == "trivial":
        return trivial.Trivial()
    if method == "tf":
        return tf.Tf()
    if method == "ktf":
        return ktf.KTf()
    if method == "rtf":
        return rtf.RTf()
    if method == "ptf":
        return ptf.PTf()
    if method == "dptf":
        return dptf.DPTf()

    return None
