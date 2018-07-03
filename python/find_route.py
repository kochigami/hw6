#!/usr/bin/env python
# -*- coding: utf-8 -*-

class FindRoute():
    def dequeue(self, x):
        ret = x[0]
        x[0:] = x[1:]
        return ret

    def enqueue(self, x, a):
        x[len(x):] = [a]

    def search(self, station, adjacent, start, goal):
        q = [[start]]
        path_list = [] #
        while len(q) > 0:
            path = self.dequeue(q)
            last_component = path[len(path) - 1]
            if last_component == goal:
                path_list.append(path) #
                #return path
            else:
                pos = station[last_component]
                for x in range(1, len(adjacent[pos])):
                    if not (adjacent[pos][x] in path):
                        new_path = path[:] + [adjacent[pos][x]]
                        self.enqueue(q, new_path)
        return path_list #
