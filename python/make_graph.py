#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, codecs
import networkx
import datetime

class MakeGraph():
    def make_graph(self, train_time, train_route):
        # make_graph_of_same_line
        Graph, node_dict = self.make_graph_of_same_line(train_time)
        # make_graph_of_transfer_station
        Graph = self.make_graph_of_transfer_stations(Graph, node_dict, train_route)
        return Graph, node_dict

    def make_graph_of_same_line(self, train_time):
        Graph = networkx.DiGraph()
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
                station_j_depart = self.split_time(depart)
                
                # Arrives
                arrive = train_time[i]["Stops"][j+1]["Arrives"]
                station_j_plus_1_arrive = self.split_time(arrive)
                
                # make node name
                station_j_node = station_j + "+" + line + "+" + str(direction) + "+" + str(station_j_depart[0]) + "+" + str(station_j_depart[1]) + "+" + "depart"
                station_j_plus_1_node = station_j_plus_1 + "+" + line + "+" + str(direction) + "+" + str(station_j_plus_1_arrive[0]) + "+" + str(station_j_plus_1_arrive[1]) + "+" + "arrive"
                Graph.add_node(station_j_node)
                Graph.add_node(station_j_plus_1_node)

                # make edge with weight
                depart = self.fetch_time(station_j_node)
                arrive = self.fetch_time(station_j_plus_1_node)
                weight = self.compare_time(depart, arrive)
                Graph.add_edge(station_j_node, station_j_plus_1_node, weight = weight )
                
                # add node_dict
                # ex. key: 品川-山手線 => [node_name1, node_name2, ...]
                if station_j + "-" + line in node_dict.keys():
                    node_dict[station_j + "-" + line].append(station_j_node)
                else:
                    node_dict[station_j + "-" + line] = [station_j_node]

                if station_j_plus_1 + "-" + line in node_dict.keys():
                    node_dict[station_j_plus_1 + "-" + line].append(station_j_plus_1_node)
                else:
                    node_dict[station_j_plus_1 + "-" + line] = [station_j_plus_1_node]

        return Graph, node_dict

    def split_time(self, time_str):
        time_str = time_str.split(":")
        hour = time_str[0].split("T")
        hour = hour[1]
        if hour[0] == '0' and len(hour) > 1:
            hour = hour[1]
        minute = time_str[1]
        return [hour, minute]

    def transfer_station_list (self, train_route):
        line_num = len(train_route)
        station_num = []
        route = []
        transfer_station = []
        for i in range(line_num):
            station_num.append(len(train_route[i]['Stations']))
        
        for i in range(line_num):
            for j in range(station_num[i]):
                current_station = train_route[i]['Stations'][j] + "-" + train_route[i]['Name']
                route.append(current_station)

        for i in range(len(route)):
            for j in range(len(route)):
                str1 = route[i].split("-")
                str2 = route[j].split("-")
                if  str1[0] == str2[0] and route[i] != route[j] and not(route[i] in transfer_station):
                    transfer_station.append(route[i])

        return transfer_station

    def add_transfer_station(self, train_route):
        transfer_list = self.transfer_station_list(train_route)    
        transfer_dict = {}

        for i in range(len(transfer_list)):
            tmp_list = []
            for j in range(len(transfer_list)):
                if i != j:
                    if transfer_list[i].split("-")[0] == transfer_list[j].split("-")[0]:
                        tmp_list.append(transfer_list[j])
            transfer_dict[transfer_list[i]] = tmp_list
            tmp_list = []
        return transfer_list, transfer_dict

    def fetch_station_name(self, node_name):
        word = node_name.split("+")
        return word[0] + "-" + word[1]

    def fetch_time(self, node_name):
        word = node_name.split("+")
        if word[3][0] == '0' and len(word[3]) > 1:
            hour = word[3][1]
        else:
            hour = word[3]
        return [int(hour), int(word[4])]

    def compare_time(self, start, end):
        start_min = start[0] * 60 + start[1]
        end_min = end[0] * 60 + end[1]
        return end_min - start_min

    def make_graph_of_transfer_stations(self, Graph, node_dict, train_route):
        ts, transfer_list = self.add_transfer_station(train_route)    
        nodes = Graph.nodes()
        # nodes[i] : arrive
        # j: depart
        for i in range(len(nodes)):
            target_station = self.fetch_station_name(nodes[i])
            if target_station in ts:
                stations = transfer_list[target_station]
                for j in stations:
                    train_list = node_dict[j]
                    for k in train_list:
                        arrive_time = self.fetch_time(nodes[i])
                        depart_time = self.fetch_time(k)
                        weight = self.compare_time(arrive_time, depart_time)
                        if weight > 0:
                            Graph.add_edge(nodes[i], k, weight = weight)

        return Graph

    def fetch_line(self, name, node_dict, mode, time):
        answer_list = []
        tmp = None
        train_candidates = node_dict[name]
        for i in train_candidates:
            # 品川+山手線+-1+4+14+depart
            word = i.split('+')
            if word[2] == '-1' and mode == word[5]:
                hour = time[0]
                minute = time[1]
                if (hour < int(word[3]) or hour == int(word[3])) and (minute < int(word[4]) or minute == int(word[4])):
                    if mode == "depart":
                        answer_list.append(i)
                        break
                    elif mode == "arrive":
                        answer_list.append(i)

        for i in train_candidates:
            # 品川+山手線+-1+4+14+depart
            word = i.split('+')
            if word[2] == '1' and mode == word[5]:
                hour = time[0]
                minute = time[1]
                if (hour < int(word[3]) or hour == int(word[3])) and (minute < int(word[4]) or minute == int(word[4])):
                    if mode == "depart":
                        answer_list.append(i)
                        break
                    elif mode == "arrive":
                        answer_list.append(i)
        return answer_list

    def what_time_now(self):
        today = datetime.datetime.now()
        hour = today.hour
        minute = today.minute
        return [hour, minute]

def make_graph_test(train_data, train_route):
    make_graph = MakeGraph()
    print "start"
    graph, node_dict = make_graph.make_graph(train_data, train_route)
    print "end"
    
    start = u"品川-山手線"
    end = u"中目黒-日比谷線"
    #end = u"品川-山手線"

    time = make_graph.what_time_now()
    start_st = make_graph.fetch_line(start, node_dict, "depart", time=time)
    end_st = make_graph.fetch_line(end, node_dict, "arrive", time=time)
    
    # for i in start_st:
    #     print i

    # for  i in end_st:
    #     print i

    #for i in node_dict[start]:
    #    print i

    #for i in node_dict[end]:
    #    print i

    path = networkx.dijkstra_path(graph, u'品川+山手線+-1+15+04+depart', u'中目黒+日比谷線+-1+16+22+arrive')
    #path = networkx.dijkstra_path(graph, u'品川+山手線+-1+4+14+depart', u'田町+山手線+-1+4+19+arrive')
    print path

    for i in start_st:
        for j in end_st:
            try:
                print i + ", " + j
                path = networkx.dijkstra_path(graph, i, j)

                for k in path:
                    print k
            except:
                print "not found"

# file reading #

f = open("trains.json", 'r')
train_time = json.load(f)

f2 = open("net.json", 'r')
train_route = json.load(f2)

make_graph_test(train_time, train_route)

