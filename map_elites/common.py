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

import math
import numpy as np
import multiprocessing
from pathlib import Path
import sys
import random
from collections import defaultdict
from sklearn.cluster import KMeans

default_params = \
    {
        # more of this -> higher-quality CVT
        "cvt_samples": 25000,
        # we evaluate in batches to paralleliez
        "batch_size": 100,
        # proportion of niches to be filled before starting
        "random_init": 0.1,
        # batch for random initialization
        "random_init_batch": 100,
        # parameters of the "mutation" operator
        "sigma_iso": 0.01,
        # parameters of the "cross-over" operator
        "sigma_line": 0.2,
        # when to write results (one generation = one batch)
        "dump_period": 10000,
        # do we use several cores?
        "parallel": True,
        # do we cache the result of CVT and reuse?
        "cvt_use_cache": True,
        # min/max of parameters
        "min": [0]*15,
        "max": [1]*15,
        "multi_task": False,
        "multi_mode": 'full'
    }
class Species:
    def __init__(self, x, desc, fitness):
        self.x = x
        self.desc = desc
        self.fitness = fitness
        self.centroid = None
        self.challenges = 0

def scale(x,params):
    x_scaled = []
    for i in range(0,len(x)) :
        x_scaled.append(x[i] * (params["max"][i] - params["min"][i]) + params["min"][i])
    return np.array(x_scaled)


def variation_xy(x, z, params):
    y = x.copy()
    for i in range(0, len(y)):
        # iso mutation
        a = np.random.normal(0, (params["max"][i]-params["min"][i])/300.0, 1)
        y[i] =  y[i] + a
        # line mutation
        b = np.random.normal(0, 20*(params["max"][i]-params["min"][i])/300.0, 1)
        y[i] =  y[i] + b*(x[i] - z[i])
    y_bounded = []
    for i in range(0,len(y)):
        elem_bounded = min(y[i],params["max"][i])
        elem_bounded = max(elem_bounded,params["min"][i])
        y_bounded.append(elem_bounded)
    return np.array(y_bounded)

def variation(x, archive, params):
  keys = list(archive.keys())
  z = archive[keys[np.random.randint(len(keys))]].x
  return variation_xy(x, z, params)

def __centroids_filename(k, dim):
    return 'centroids_' + str(k) + '_' + str(dim) + '.dat'


def __write_centroids(centroids):
    k = centroids.shape[0]
    dim = centroids.shape[1]
    filename = __centroids_filename(k, dim)
    with open(filename, 'w') as f:
        for p in centroids:
            for item in p:
                f.write(str(item) + ' ')
            f.write('\n')


def __cvt(k, dim, samples, cvt_use_cache=True):
    # check if we have cached values
    fname = __centroids_filename(k, dim)
    if cvt_use_cache:
        if Path(fname).is_file():
            print("WARNING: using cached CVT:", fname)
            return np.loadtxt(fname)
    # otherwise, compute cvt
    print("Computing CVT (this can take a while...):", fname)

    x = np.random.rand(samples, dim)
    k_means = KMeans(init='k-means++', n_clusters=k,
                     n_init=1, n_jobs=-1, verbose=1)#,algorithm="full")
    k_means.fit(x)
    return k_means.cluster_centers_


def __make_hashable(array):
    return tuple(map(float, array))


# format: fitness, centroid, desc, genome \n
# fitness, centroid, desc and x are vectors
def __save_archive(archive, gen):
    def write_array(a, f):
        for i in a:
            f.write(str(i) + ' ')
    filename = 'archive_' + str(gen) + '.dat'
    with open(filename, 'w') as f:
        for k in archive.values():
            f.write(str(k.fitness) + ' ')
            write_array(k.centroid, f)
            write_array(k.desc, f)
            write_array(k.x, f)
            f.write("\n")


def __add_to_archive(s, centroid, archive, kdt):
    niche_index = kdt.query([centroid], k=1)[1][0][0]
    niche = kdt.data[niche_index]
    n = __make_hashable(niche)
    s.centroid = n
    if n in archive:
        c = s.challenges + 1
        if s.fitness > archive[n].fitness:
            archive[n] = s
            return 1
        return 0
    else:
        archive[n] = s
        return 1