#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, codecs
import networkx
from find_route_test import FindRouteTest

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
    if hour[0] == '0' and len(hour) > 1:
        hour = hour[1]
    minute = time_str[1]
    return [hour, minute]

def make_graph(train_time):
    # make_graph_of_same_line
    Graph, node_dict = make_graph_of_same_line(train_time)
    Graph = make_graph_of_transfer_stations(Graph, node_dict)
    return Graph, node_dict

def make_graph_of_same_line(train_time):
    Graph=networkx.DiGraph()
    train_num = len(train_time)
    node_dict = {}
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

            # add node_dict
            if station_j + "-" + line in node_dict.keys():
                node_dict[station_j + "-" + line].append(station_j_node)
            else:
                node_dict[station_j + "-" + line] = [station_j_node]

            if station_j_plus_1 + "-" + line in node_dict.keys():
                node_dict[station_j_plus_1 + "-" + line].append(station_j_plus_1_node)
            else:
                node_dict[station_j_plus_1 + "-" + line] = [station_j_plus_1_node]

            # weight
            depart = fetch_time(station_j_node)
            arrive = fetch_time(station_j_plus_1_node)
            weight = compare_time(depart, arrive)
            Graph.add_edge(station_j_node, station_j_plus_1_node, weight = weight )

    return Graph, node_dict

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

def fetch_station_name(node_name):
    word = node_name.split("+")
    return word[0] + "-" + word[1]

def fetch_time(node_name):
    word = node_name.split("+")
    if word[3][0] == '0' and len(word[3]) > 1:
        hour = word[3][1]
    else:
        hour = word[3]
    return [int(hour), int(word[4])]

def compare_time(start, end):
    start_min = start[0] * 60 + start[1]
    end_min = end[0] * 60 + end[1]
    return end_min - start_min

def make_graph_of_transfer_stations(Graph, node_dict):
    ts, transfer_list = add_transfer_station()    
    nodes = Graph.nodes()
    # nodes[i] : arrive
    # j: depart
    for i in range(len(nodes)):
        target_station = fetch_station_name(nodes[i])
        if target_station in ts:
            stations = transfer_list[target_station]
            for j in stations:
                train_list = node_dict[j]
                for k in train_list:
                    arrive_time = fetch_time(nodes[i])
                    depart_time = fetch_time(k)
                    weight = compare_time(arrive_time, depart_time)
                    if weight > 0:
                        Graph.add_edge(nodes[i], k, weight = weight)

    return Graph


def make_graph_test(train_data):
    print "start"
    graph, node_dict = make_graph(train_data)
    print "end"
    path = networkx.dijkstra_path(graph, u'品川+山手線+-1+4+14+depart', u'田町+山手線+-1+4+19+arrive')
    #for i in path:
    #    print i
    for i in node_dict.keys():
        print i
        for j in node_dict[i]:
            print j


# file reading #

f = open("trains.json", 'r')
train_time = json.load(f)

f2 = open("net.json", 'r')
train_route = json.load(f2)

make_graph_test(train_time)

