#!/usr/bin/env python
# -*- coding: utf-8 -*-

class FindRoute():
    def dequeue(self, x):
        ret = x[0]
        x[0:] = x[1:]
        return ret

    def enqueue(self, x, a):
        x[len(x):] = [a]

    def search(self, adjacent, start, goal):    
        q = [[start]]
        while len(q) > 0:
            path = self.dequeue(q)
            last_component = path[len(path) - 1]
            string = last_component.split("-")
            if string[0] in goal:
                return path
            else:
                for i in range(len(adjacent)):
                    if adjacent[i][0] == last_component:
                        break

                for x in range(1, len(adjacent[i])):
                    new_path = path[:] + [adjacent[i][x]]
                    self.enqueue(q, new_path)
