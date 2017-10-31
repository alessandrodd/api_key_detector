import itertools
import logging
import math
import os
from collections import OrderedDict

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from sklearn.neural_network import MLPClassifier

"""
Comparison between different Neural Network classifiers
Inspired by http://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html
"""

logging.basicConfig(level=logging.DEBUG)

PARAMETER_LABELS = ["Entropy", "Sequentiality", "Gibberish", "Charset Length"]
N_DIMS = len(PARAMETER_LABELS)

h = 0.3  # step size in the mesh, smaller => higher resolution, higher computing time and memory usage
classifiers = OrderedDict(
    [
        ("100,100,100 10000iter", MLPClassifier(hidden_layer_sizes=(100, 100, 100), solver='adam', max_iter=10000)),
        ("100,100,100 5000iter", MLPClassifier(hidden_layer_sizes=(100, 100, 100), solver='adam', max_iter=5000)),
        ("100,100,100 1000iter", MLPClassifier(hidden_layer_sizes=(100, 100, 100), solver='adam', max_iter=1000)),
        ("100,100,100 100iter", MLPClassifier(hidden_layer_sizes=(100, 100, 100), solver='adam', max_iter=100)),
        ("100,100, 10000iter", MLPClassifier(hidden_layer_sizes=(100, 100), solver='adam', max_iter=10000)),
        ("100,100, 5000iter", MLPClassifier(hidden_layer_sizes=(100, 100), solver='adam', max_iter=5000)),
        ("100,100, 1000iter", MLPClassifier(hidden_layer_sizes=(100, 100), solver='adam', max_iter=1000)),
        ("100,100, 100iter", MLPClassifier(hidden_layer_sizes=(100, 100), solver='adam', max_iter=100)),
        ("100, 5000iter", MLPClassifier(hidden_layer_sizes=(100,), solver='adam', max_iter=5000)),
        ("100, 1000iter", MLPClassifier(hidden_layer_sizes=(100,), solver='adam', max_iter=1000)),
        ("100, 100iter", MLPClassifier(hidden_layer_sizes=(100,), solver='adam', max_iter=100))
    ])

# load classifier dataset, i.e. a n*4 matrix where n is the number of samples,
# while 4 columns are for tridimensional inputs + expected output/class
# e.g.  [[0.1, 0.2, 0.3, 1.0],
#        [0.6, 0.7, 0.8, 0.0]]
matrix = np.load(os.path.join("datasets", "classifier_learnset.npy"))
np.random.shuffle(matrix)
# separate expected outputs and inputs features
train_outputs = np.array([matrix[:, -1]]).T
train_outputs = train_outputs.astype(int)
train_inputs = matrix[:, 0:-1]
# load test set
matrix = np.load(os.path.join("datasets", "classifier_testset_extended.npy"))
test_outputs = np.array([matrix[:, -1]]).T
test_outputs = test_outputs.astype(int)
test_inputs = matrix[:, 0:-1]

# standardize the input
input_mean = train_inputs.mean(axis=0)
input_stdev = train_inputs.std(axis=0)
train_inputs -= input_mean
train_inputs /= input_stdev
test_inputs -= input_mean
test_inputs /= input_stdev

# we have multidimensional input and we want to print the 2d projections,
# so let's get the min of max of each dimension
dim_min = np.array(train_inputs.min(axis=0))
dim_max = np.array(train_inputs.max(axis=0))
# add some margin
dim_min = dim_min - (dim_max - dim_min) / 20
dim_max = dim_max + (dim_max - dim_min) / 20

# first create a multidimensional meshgrid to calculate the values for
# a set of all possible combinations of x,y,z...
ranges = tuple([np.arange(mn, mx, h) for mn, mx in zip(dim_min, dim_max)])

# create a meshgrid
meshgrid = np.meshgrid(*ranges)

# then, for each projection (pair of dimensions) we should create another meshgrid, 2d this time
# the next variable should contain a list of 2d mesh, it's quite complex to imagine it
meshes2d = []
pairs = list(itertools.combinations(range(N_DIMS), 2))
for pair in pairs:
    mesh2d = np.meshgrid(np.arange(dim_min[pair[0]], dim_max[pair[0]], h),
                         np.arange(dim_min[pair[1]], dim_max[pair[1]], h))
    meshes2d.append(mesh2d)

# let's choose a colormap. Red-Blue seems nice for binary classification
cm = 'RdBu'
cm_bright = ListedColormap(['#FF0000', '#0000FF'])

# Set figure width and height
fig_size = plt.rcParams["figure.figsize"]
fig_size[0] = len(classifiers) * 4
fig_size[1] = len(pairs) * 3
plt.rcParams["figure.figsize"] = fig_size

# initialize the axes with labels
# and, for each projection, plot the training points
f, axarr = plt.subplots(len(pairs), len(classifiers) + 1)
for i in range(len(pairs)):
    for j in range(len(classifiers) + 1):
        # labels
        if i == 0:
            axarr[i, j].set_title("Input data")
        axarr[i, j].set_xlabel(PARAMETER_LABELS[pairs[i][0]])
        axarr[i, j].set_ylabel(PARAMETER_LABELS[pairs[i][1]])
        # training points and testing points
        if j == 0:
            axarr[i, j].scatter(train_inputs[:, pairs[i][0]], train_inputs[:, pairs[i][1]],
                                c=train_outputs[:, 0],
                                cmap=cm_bright, s=1)
            axarr[i, j].scatter(test_inputs[:, pairs[i][0]], test_inputs[:, pairs[i][1]], c=test_outputs[:, 0],
                                cmap=cm_bright, s=1)

# iterate over classifiers
for index, name in enumerate(classifiers.keys()):
    clf = classifiers.get(name)
    print("Computing {0} ...".format(name))

    # train the classifier, then test it
    clf.fit(train_inputs, train_outputs[:, 0])
    score = clf.score(test_inputs, test_outputs[:, 0])

    print("Score: {0} ({1} wrong)".format(score, round((1 - score) * (test_inputs.shape[0]))))

    # calculate the decision boundary
    raveled_meshgrid = []
    for m in meshgrid:
        # noinspection PyUnresolvedReferences
        raveled_meshgrid.append(m.ravel())
    raveled_meshgrid = np.array(raveled_meshgrid)
    arguments = raveled_meshgrid.T
    arguments_splitted = np.array_split(arguments, math.ceil(len(arguments) / 100))
    Z = None
    for argument in arguments_splitted:
        if hasattr(clf, "decision_function"):
            results = clf.decision_function(argument)
        else:
            results = clf.predict_proba(argument)[:, 1]
        if Z is None:
            Z = results
        else:
            Z = np.concatenate((Z, results))

    # reduce the dimensionality and plot the colored area for each projection
    for index2, (pair, mesh2d) in enumerate(zip(pairs, meshes2d)):
        dims = []
        for i in range(N_DIMS):
            if i not in pair:
                dims.append(i)
        reshaped = Z.reshape(meshgrid[0].shape)
        # TODO: GENERALIZE THIS!!!!!
        if index2 == 0:
            zprojection = reshaped.mean(axis=(2, 3))
        elif index2 == 1:
            zprojection = reshaped.mean(axis=(0, 3)).T
        elif index2 == 2:
            zprojection = reshaped.mean(axis=(0, 2)).T
        elif index2 == 3:
            zprojection = reshaped.mean(axis=(1, 3)).T
        elif index2 == 4:
            zprojection = reshaped.mean(axis=(1, 2)).T
        else:
            zprojection = reshaped.mean(axis=(0, 1)).T
        axarr[pairs.index(pair), index + 1].set_title("{0}\n{1:.5f}".format(name, score))
        axarr[pairs.index(pair), index + 1].contourf(mesh2d[0], mesh2d[1], zprojection, cmap=cm, alpha=.8)
        axarr[pairs.index(pair), index + 1].scatter(train_inputs[:, pair[0]], train_inputs[:, pair[1]],
                                                    c=train_outputs[:, 0],
                                                    cmap=cm_bright, s=1)
        axarr[pairs.index(pair), index + 1].scatter(test_inputs[:, pair[0]], test_inputs[:, pair[1]],
                                                    c=test_outputs[:, 0],
                                                    cmap=cm_bright, s=1)

plt.tight_layout()
plt.savefig(os.path.join("test_results", "neuralnets_configurations_adam.png"))
plt.show()
