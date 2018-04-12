#!/usr/bin/env python
# -*- coding: utf-8 -*-
from igraph import *

class Coarser():

    def __init__(self):
        pass

    # Method that receives an original graph and a matching array and creates a coarsed graph. Complexity = O(V + E)
    def coarserning(self, graph, matching):
        # Creates a new coarsed graph.
        coarsed_graph = Graph()
        # Calculates the number of vertices of the coarsed graph.
        n_vertices = 0
        # An array of the successors of all vertices in the new coarsed graph.
        successors = range(graph.vcount())
        successor = 0
        for i in range(len(matching)):
            if(i <= matching[i]):
                n_vertices += 1
                successors[i] = successor
                successor += 1
            else:
                successors[i] = successors[matching[i]]
        # Add the vertices in the coarsed graph.
        coarsed_graph.add_vertices(n_vertices)
        # Calculates the new edges for the coarsed graph.
        weights = {}
        for edge in graph.get_edgelist():
            # Recovers the vertices new ids in the coarsed network.
            new_source = successors[edge[0]]
            new_target = successors[edge[1]]
            if(new_source != new_target):
                # Tests if the edge was already defined for the coarsed graph.
                if((new_source, new_target) in weights):
                    weights[(new_source, new_target)] += graph[edge[0], edge[1]]
                elif((new_target, new_source) in weights):
                    weights[(new_target, new_source)] += graph[edge[0], edge[1]]
                else:
                    weights[(new_source, new_target)] = graph[edge[0], edge[1]]

        # Add the edges in the graph.
        coarsed_graph.add_edges(weights.keys())
        # Add the edges weights in the graph.
        coarsed_graph.es['weight'] = weights.values()
        # Updates the coarse level of the graph.
        coarsed_graph['level'] = graph['level'] + 1
        # Updates the succesors of the graph according to the original graph.
        coarsed_graph['successors'] = [0] * len(graph['successors'])
        for i in range(len(graph['successors'])):
            coarsed_graph['successors'][i] = successors[graph['successors'][i]]

        return coarsed_graph

    # Method that receives the coarsed graph and extracts subgraphs of the vertices inside the supervertices.
    # Each supervertice generates a subgraph.
    def create_subgraphs(self, original_graph, coarsed_graph):
        supervertices = {}
        # Gets the supervertices from the successors.
        for i in range(len(coarsed_graph['successors'])):
            successor = coarsed_graph['successors'][i]
            if(successor in supervertices):
                supervertices[successor].append(i)
            else:
                supervertices[successor] = [i]
        # Creates the subgraphs for each supervertex.
        subgraphs = [None] * len(supervertices)
        index = 0
        for supervertex in supervertices:
            subgraphs[index] = original_graph.subgraph(supervertices[supervertex])
            index += 1
        return subgraphs