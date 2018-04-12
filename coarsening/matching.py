#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

class Matching():

    def __init__(self):
        # Array that contains all the available matching methods implemented in this class.
        self.matchings_array = [self.random_matching, self.most_similar_edge_matching, self.least_similar_edge_matching,
                                self.heavy_edge_matching, self.light_edge_matching]



    # Implementation of the Random matching (RM). Time complexity is O(|E|).
    def random_matching(self, graph, similarity):
        # Creates an array that represents the matching array.
        matching = range(graph.vcount())
        # Gets the edgelist.
        edgelist = graph.get_edgelist()
        for edge in random.sample(edgelist, len(edgelist)):
            from_vertex = edge[0]
            to_vertex = edge[1]
            # If this condition is satisfied, a matching occurs.
            if(matching[from_vertex] == from_vertex and matching[to_vertex] == to_vertex):
                matching[from_vertex] = to_vertex
                matching[to_vertex] = from_vertex

        return matching


    # Implementation of the Most Similar Edge Matching (MSEM). For each vertex that was not matched yet,
    # The most similar (according to a similarity measure) neighbor is selected for matching. MSE - Most Similar Edge.
    def most_similar_edge_matching(self, graph, similarity):
        adjlist = map(set, graph.get_adjlist())
        # Creates an array that represents the matching array.
        matching = range(graph.vcount())
        # Dictionary that stores the similarities already calculated for the graph.
        for i in range(graph.vcount()):
            # Means a non-matched vertex.
            if(i == matching[i]):
                neighbors = graph.neighbors(i)
                best_similarity = -1
                # For each vertex neighbor, the similarity will be calculated. The for similar vertex will be selected.
                for j in neighbors:
                    # Means a non-matched neighbor.
                    if(matching[j] == j):
                        sim = similarity(graph, adjlist, i=i, j=j)
                        if(sim > best_similarity):
                            # Updates the best similarity found.
                            best_similarity = sim
                            # Corrects the old matching.
                            matching[matching[i]] = matching[i]
                            # Add the new matches.
                            matching[i] = j
                            matching[j] = i
        return matching

    # Implementation of the Least Similar Edge Matching (LSEM). For each vertex that was not matched yet,
    # The least similar (according to a similarity measure) neighbor is selected for matching. MSE - Least Similar Edge.
    def least_similar_edge_matching(self, graph, similarity):
        adjlist = map(set, graph.get_adjlist())
        # Creates an array that represents the matching array.
        matching = range(graph.vcount())
        # Dictionary that stores the similarities already calculated for the graph.
        for i in range(graph.vcount()):
            # Means a non-matched vertex.
            if(i == matching[i]):
                neighbors = graph.neighbors(i)
                worst_similarity = float("inf")
                # For each vertex neighbor, the similarity will be calculated. The for similar vertex will be selected.
                for j in neighbors:
                    # Means a non-matched neighbor.
                    if(matching[j] == j):
                        sim = similarity(graph, adjlist, i=i, j=j)
                        if(sim < worst_similarity):
                            # Updates the best similarity found.
                            worst_similarity = sim
                            # Corrects the old matching.
                            matching[matching[i]] = matching[i]
                            # Add the new matches.
                            matching[i] = j
                            matching[j] = i
        return matching


    # Implementation of the Heavy Edge Matching (HEM). Time complexity is O(|E|).
    def heavy_edge_matching(self, graph, similarity):
        matching = range(graph.vcount())

        for vertex in random.sample(matching, len(matching)):
            # Means that the vertice was not matched yet.
            if(matching[vertex] == vertex):
                # Gets the adjacent neighbors.
                neighbors = graph.neighbors(vertex)
                greatest_value = 0
                greatest_value_neighbor = -1
                for neighbor in neighbors:
                    if(matching[neighbor] == neighbor):
                        value = graph[min(vertex, neighbor), max(vertex, neighbor)]
                        if(value > greatest_value):
                            greatest_value = value
                            greatest_value_neighbor = neighbor
                if(greatest_value_neighbor != -1):
                    matching[greatest_value_neighbor] = vertex
                    matching[vertex] = greatest_value_neighbor

        return matching

    # Implementation of the Heavy Edge Matching (HEM). Time complexity is O(|E|).
    def light_edge_matching(self, graph, similarity):
        matching = range(graph.vcount())

        for vertex in random.sample(matching, len(matching)):
            # Means that the vertice was not matched yet.
            if(matching[vertex] == vertex):
                # Gets the adjacent neighbors.
                neighbors = graph.neighbors(vertex)
                lowest_value = float("inf")
                lowest_value_neighbor = -1
                for neighbor in neighbors:
                    if(matching[neighbor] == neighbor):
                        value = graph[min(vertex, neighbor), max(vertex, neighbor)]
                        if(value < lowest_value):
                            lowest_value = value
                            lowest_value_neighbor = neighbor
                if(lowest_value_neighbor != -1):
                    matching[lowest_value_neighbor] = vertex
                    matching[vertex] = lowest_value_neighbor

        return matching










