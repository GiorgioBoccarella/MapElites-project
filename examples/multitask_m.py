#! /usr/bin/env python
#| This file is a part of the pymap_elites framework.
#| Copyright 2019, INRIA
#| Main contributor(s):
#| Jean-Baptiste Mouret, jean-baptiste.mouret@inria.fr
#| Eloise Dalin , eloise.dalin@inria.fr
#| Pierre Desreumaux , pierre.desreumaux@inria.fr
#|
#|
#| **Main paper**: Mouret JB, Clune J. Illuminating search spaces by
#| mapping elites. arXiv preprint arXiv:1504.04909. 2015 Apr 20.
#|
#| This software is governed by the CeCILL license under French law
#| and abiding by the rules of distribution of free software.  You
#| can use, modify and/ or redistribute the software under the terms
#| of the CeCILL license as circulated by CEA, CNRS and INRIA at the
#| following URL "http://www.cecill.info".
#|
#| As a counterpart to the access to the source code and rights to
#| copy, modify and redistribute granted by the license, users are
#| provided only with a limited warranty and the software's author,
#| the holder of the economic rights, and the successive licensors
#| have only limited liability.
#|
#| In this respect, the user's attention is drawn to the risks
#| associated with loading, using, modifying and/or developing or
#| reproducing the software by the user in light of its specific
#| status of free software, that may mean that it is complicated to
#| manipulate, and that also therefore means that it is reserved for
#| developers and experienced professionals having in-depth computer
#| knowledge. Users are therefore encouraged to load and test the
#| software's suitability as regards their requirements in conditions
#| enabling the security of their systems and/or data to be ensured
#| and, more generally, to use and operate it in the same conditions
#| as regards security.
#|
#| The fact that you are presently reading this means that you have
#| had knowledge of the CeCILL license and that you accept its terms.
#

import kinematic_arm
import math
import numpy as np
import sys

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import map_elites.multitask_mod as mt_map_elites
import map_elites.common as cm_map_elites


def fitness(ind, env):
    #np.linalg.norm(ind - env) is the mismatch
    # The 10 is arbitrary, worst fitness possible is 6.83772..
    f = 10 - np.linalg.norm(ind - env)
    return f

if len(sys.argv) == 1 or ('help' in sys.argv):
    print("Usage: \"python3 ./examples/multitask_arm.py 10 [no_distance]\"")
    exit(0)


dim_x = int(sys.argv[1])

# dim_map, dim_x, function
px = cm_map_elites.default_params.copy()
px["dump_period"] = 2000
px["parallel"] = False


#Generate environements
# 10 bits = 1024 env
n = 10
env_list = [bin(x)[2:].rjust(n, "0") for x in range(2**n)]

#From string to binary
for i in range(len(env_list)):
    env_list[i] = [int(numeric_string) for numeric_string in env_list[i]]
#Every environment sum is == 5
env_list = [i for i in env_list if sum(i) == 5]



archive = mt_map_elites.compute(dim_x = dim_x, f=fitness, tasks=env_list, max_evals=1e6, params=px, log_file=open('mt_no_dist.dat', 'w'))
