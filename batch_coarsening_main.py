#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

from loader.iohandler import IOHandler
from similarity.similarity import Similarity
from coarsening.matching import Matching
from coarsening.coarser import Coarser
from linkprediction.link_predictor import LinkPredictor
from linkprediction.ml_link_predictor import MultilevelLinkPredictor
from linkprediction.metric_calculator import MetricCalculator
from linkprediction.sampler import Sampler
from loader.graph_loader import GraphLoader
import random
import os

import time

def print_graph(graph):
    print "Vertices:", range(graph.vcount())
    print "Edges:", graph.get_edgelist()

def print_predicted(predicted_edges):
    for predicted_edge in predicted_edges:
        print predicted_edge,":",predicted_edges[predicted_edge]

def print_graph_status(graph):
    print "Vertices:", graph.vcount(), "Edges:", graph.ecount()

# Parse options command line
parser = argparse.ArgumentParser(description="Multilevel link prediction")
# Define the arguments that the user will pass to the software.
parser.add_argument('-f', '--filename', action='store', dest='filename', help='A file name that contains a .ncol network.', type = str)
parser.add_argument('-k', '--k', action='store', dest='k', help='Number of folds to cross validation.', type = int, default = 10)
parser.add_argument('-l', '--levels', action='store', dest='levels', help='Number of levels the networks will be coarsed.', type = int, default = 0)
parser.add_argument('-m', '--matching', action='store', dest='matching_method', help='Matching method that will be used for coarsening. [0 - RM, 1 - MSE, 2 - LSE].', type = int, default = 0)
parser.add_argument('-s', '--similarity', action='store', dest='similarity_method', help='Similarity measure used for link prediction. [0 - CN, 1 - JAC, 2 - SAL, 3 - AA, 4 - PA, 5 - KATZ].', type = int, default = 0)
parser.add_argument('-lp', '--mlinkpredictor', action='store', dest='multilevellp_method', help='Method that will be used for multilevel link prediction. [0 - ER, 1 - ERF, 2 - WER, 3 - WERF].', type = int, default = 0)

# Parses the arguments.
args = parser.parse_args()

if args.filename is None:
	parser.error("required -f [filename] arg.")

graph_loader = GraphLoader()
if("ncol" in args.filename):
    graph = graph_loader.load_unipartite_undirected_ncol(args.filename)
elif("gml" in args.filename):
    graph = graph_loader.load_unipartite_undirected_gml(args.filename)

coarser = Coarser()
matching = Matching()
link_predictor = LinkPredictor()
similarity = Similarity()
ml_link_predictor = MultilevelLinkPredictor()
metric_calculator = MetricCalculator()
sampler = Sampler()

# Number of folds of the set.
k = args.k
# Number of levels that will be coarsened of the graph.
l = args.levels
# Matching method.
m = args.matching_method
# Similarity method.
s = args.similarity_method
# Similarity method.
lp = args.multilevellp_method
# Solves the dataset name.
dataset_name = (args.filename.split("/")[len(args.filename.split("/")) - 1]).split(".")[0]
print "Executing for dataset =",dataset_name,"k =",k,"l =",l,"m =",m,"s =",s,"lp =",lp

# Gets the edgelist and shuffles this list.
edgelist = random.sample(graph.get_edgelist(), graph.ecount())
auc_io_handlers = [None] * (l + 1)
pr_io_handlers = [None] * (l + 1)
time_io_handlers = [None] * (l + 1)
# ranking_io_handlers = [None] * (l + 1)

# Size of Ls that will be analised.
ls = [100, 200, 500, 1000, 2500, 5000, 10000]

for i in range(l+1):
    # Creating io_handlers for writing outputs in the files.
    auc_io_handlers[i] = IOHandler()
    pr_io_handlers[i] = IOHandler()
    time_io_handlers[i] = IOHandler()
    # ranking_io_handlers[i] = IOHandler()
    dir = "output/" + dataset_name + "/" + ml_link_predictor.predictors_array[lp].__name__ + "/" + matching.matchings_array[m].__name__ + "/" + similarity.similarities_array[s].__name__ + "/level" + str(i) + "/"
    if(not os.path.exists(dir)):
        os.makedirs(dir)
    # Loading output files.
    auc_io_handlers[i].load_output_file(dir + "auc.csv")
    pr_io_handlers[i].load_output_file(dir + "pr.csv")
    time_io_handlers[i].load_output_file(dir + "time.csv")
    # Writes the reader in each file.
    auc_io_handlers[i].write_results(",".join(map(str, ls)))
    pr_io_handlers[i].write_results(",".join(map(str, ls)))

predicted_edges_handler = IOHandler()
predicted_edges_path= "output/" + dataset_name + "/" + ml_link_predictor.predictors_array[lp].__name__ + "/" + matching.matchings_array[
    m].__name__ + "/" + similarity.similarities_array[s].__name__ + "/"

for i in range(k):
    print "Calculating for (",(i+1),"/",k,") folds..."
    # Creates the probe edges by k-fold.
    # probe_edges = sampler.create_k_edges_probe_list(graph, edgelist, i, k)

    # Creates the random probe edges.
    probe_edges = sampler.create_random_edges_probe_list(graph, 0.20)
    # Delete the edges from the graph.
    sampler.delete_edges(graph, probe_edges)

    # Calculating for level l.
    coarsed_graph = graph
    for level in range(l+1):
        start_time = time.time()
        similarity = Similarity()
        # Open the predicted edges file to write them.
        predicted_edges_handler.load_output_file(predicted_edges_path + "ranking.txt")

        if(level != 0):
            # Calculates the matching for coarsening.
            matching_array = matching.matchings_array[m](coarsed_graph, similarity = similarity.common_neighbors)
            coarsed_graph = coarser.coarserning(coarsed_graph, matching_array)
            # Predict the coarsed edges.
            coarsed_predicted = link_predictor.link_prediction_by_similarity(coarsed_graph, similarity.similarities_array[s])

            # Extracting real predicted edges.
            predicted_edges = ml_link_predictor.predictors_array[lp](graph, coarsed_graph, coarsed_predicted, predicted_edges_handler)
        else:
            # Predict the coarsed edges.
            predicted_edges = link_predictor.link_prediction_by_similarity_to_file(graph, similarity.similarities_array[s], predicted_edges_handler)

        # Finishes the time counter.
        elapsed_time = (time.time() - start_time)
        predicted_edges_handler.close_files()

        # Open the predicted edges file to write them.
        predicted_edges_handler.load_input_file(predicted_edges_path + "ranking.txt")

        aucs = [None] * len(ls)
        prs = [None] * len(ls)

        # Sorts the edges file for Precision calculation.
        predicted_edges_handler.batch_sort()
        for j in range(len(ls)):
            # Calculates precision.
            prs[j] = metric_calculator.calculate_precision_from_file(probe_edges, predicted_edges_handler, ls[j])

        # Shuffles the edges file for AUC calculation.
        predicted_edges_handler.batch_shuffle()
        for j in range(len(ls)):
            # Calculates auc.
            aucs[j] = metric_calculator.calculate_auc_from_file(probe_edges, predicted_edges_handler, ls[j])

        # Closes the predicted edges input file.
        predicted_edges_handler.close_files()
        # Delete the predicted edges file.
        predicted_edges_handler.remove_input_file()

        # Writes the auc results.
        auc_io_handlers[level].write_results(",".join(map(str, aucs)))
        # Writes the precision results.
        pr_io_handlers[level].write_results(",".join(map(str, prs)))
        # Writes the time results.
        time_io_handlers[level].write_results(str(elapsed_time))


    # Re-adds the edges in the network.
    sampler.readd_edges(graph, probe_edges)

for i in range(l+1):
    auc_io_handlers[i].close_files()
    pr_io_handlers[i].close_files()
    time_io_handlers[i].close_files()