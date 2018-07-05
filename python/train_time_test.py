#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, codecs
import networkx
from find_route_test import FindRouteTest

f = open("trains.json", 'r')
train_time = json.load(f)

f2 = open("net.json", 'r')
train_route = json.load(f2)

def print_test():
    train_num = len(train_time)
    print train_num

    # Line
    print train_time[0]["LineId"]["Line"]["Name"]
    
    # Direction
    print train_time[0]["LineId"]["Direction"]
    
    # station_num
    station_num = len(train_time[0]["Stops"])
    print station_num

    # Station
    print train_time[0]["Stops"][0]["Station"] # 品川
    
    # Arrive time
    arrive = train_time[0]["Stops"][0]["Arrives"]
    arrive = arrive.split(":")
    hour = arrive[0].split("T")
    hour = hour[1]
    minute = arrive[1]
    print hour, minute

    # Departs time
    depart = train_time[0]["Stops"][0]["Departs"]
    depart = depart.split(":")
    hour = depart[0].split("T")
    hour = hour[1]
    minute = depart[1]
    print hour, minute

def make_graph_test():
    Graph=networkx.DiGraph()
    Graph.add_node("a")
    Graph.add_node("b")
    
    Graph.nodes()
    # Out[5]: ['a', 'b']
    
    Graph.add_edge("a", "b", weight = 2 )
    
    Graph.edges()
    # Out[7]: [('a', 'b')]
    
    Graph.edges(data=True)
    # Out[8]: [('a', 'b', {'weight': 2})]
    
    # 全探索
    for path in networkx.all_simple_paths(Graph, source='a', target='b'):
        print path
    # ['a', 'b']

    # ダイクストラ法
    print networkx.dijkstra_path(Graph, 'a', 'b')

def split_time(time_str):
    time_str = time_str.split(":")
    hour = time_str[0].split("T")
    hour = hour[1]
    minute = time_str[1]
    return [hour, minute]

def make_graph(train_time):
    Graph=networkx.DiGraph()
    train_num = len(train_time)
    for i in range(train_num):
        # line
        line = train_time[i]["LineId"]["Line"]["Name"]
        direction = train_time[i]["LineId"]["Direction"]
        for j in range(len(train_time[i]["Stops"])-1):
            # Station
            station_j = train_time[i]["Stops"][j]["Station"]
            station_j_plus_1 = train_time[i]["Stops"][j+1]["Station"]
            
            # Departs
            depart = train_time[i]["Stops"][j]["Departs"]
            station_j_depart = split_time(depart)
            
            # Arrives
            arrive = train_time[i]["Stops"][j+1]["Arrives"]
            station_j_plus_1_arrive = split_time(arrive)

            # node name
            station_j_node = station_j + "+" + line + "+" + str(direction) + "+" + str(station_j_depart[0]) + "+" + str(station_j_depart[1]) + "+" + "depart"
            station_j_plus_1_node = station_j_plus_1 + "+" + line + "+" + str(direction) + "+" + str(station_j_plus_1_arrive[0]) + "+" + str(station_j_plus_1_arrive[1]) + "+" + "arrive"
            Graph.add_node(station_j_node)
            Graph.add_node(station_j_plus_1_node)

            # weight
            if int(station_j_plus_1_arrive[1]) < int(station_j_depart[1]):
                weight = int(station_j_plus_1_arrive[1]) + 60 - int(station_j_depart[1])
            else:
                weight = int(station_j_plus_1_arrive[1]) - int(station_j_depart[1])

            # edge j-j+1
            # weight
            Graph.add_edge(station_j_node, station_j_plus_1_node, weight = weight )

    #Graph.nodes()
    #Graph.edges(data=True)
    #path = networkx.dijkstra_path(Graph, u'品川+山手線+-1+04+14', u'田町+山手線+-1+04+19')
    #for i in path:
    #    print i

    return Graph

def add_transfer_station():
    find_route_test = FindRouteTest()
    ts = find_route_test.transfer_station(train_route)
    
    transfer_list = {}
    
    # 1駅ずつ取り出す
    for i in range(len(ts)):
        tmp_list = []
        for j in range(len(ts)):
            if i != j:
                if ts[i].split("-")[0] == ts[j].split("-")[0]:
                    # make edge between ts[i] and ts[j] 
                    tmp_list.append(ts[j])
        transfer_list[ts[i]] = tmp_list
        tmp_list = []
    return ts, transfer_list

def connect_transfer():
    ts, transfer_list = add_transfer_station()    
    Graph = make_graph(train_time)
    nodes = Graph.nodes()
    #print len(nodes)
    #for i in nodes:
    #    print i
    
    # FIXME
    # nodes[i] : arrive
    # j: depart
    # for i in range(len(nodes)):
    #     if nodes[i] in ts:
    #         # nodes[i] => arrive time
    #         stations = transfer_list[nodes[i]]
    #         for j in stations:
    #             #j => depart time
    #             if j_depart_time < nodes[i]_arrive_time:
    #                 weight
    #                 add edge


ts, transfer_list = add_transfer_station()
#print ts
#for i in ts:
#    print i

print transfer_list

for i in transfer_list.keys():
    for j in transfer_list[i]:
        print i + ": " + j
    print "\n"

