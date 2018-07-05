#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, codecs
import networkx
import datetime

class MakeGraph():
    # 乗り換え駅リスト
    def make_transfer_station_list (self, train_net):
        line_num = len(train_net)
        station_num = []
        route = []
        transfer_station_list = []
        for i in range(line_num):
            station_num.append(len(train_net[i]['Stations']))
        
        for i in range(line_num):
            for j in range(station_num[i]):
                current_station = train_net[i]['Stations'][j] + "-" + train_net[i]['Name']
                route.append(current_station)

        for i in range(len(route)):
            for j in range(len(route)):
                str1 = route[i].split("-")
                str2 = route[j].split("-")
                if  str1[0] == str2[0] and route[i] != route[j] and not(route[i] in transfer_station_list):
                    transfer_station_list.append(route[i])

        return transfer_station_list

    # 乗り換え駅 dict
    def add_transfer_station(self, train_net):
        transfer_list = self.make_transfer_station_list(train_net)    
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

    def make_graph(self, train_time, train_route):
        transfer_list, transfer_dict = self.add_transfer_station(train_route)
        # make_graph_of_same_line
        Graph, node_dict = self.make_graph_of_same_line(train_time, transfer_list)
        # make_graph_of_transfer_station
        Graph = self.make_graph_of_transfer_stations(Graph, transfer_dict, node_dict)
        return Graph, node_dict

    def make_graph_of_same_line(self, train_time, transfer_list):
        Graph = networkx.DiGraph()
        train_num = len(train_time)
        node_dict = {}
        before_arrive_node = None
        before_depart_node = None
        for i in range(train_num):
            # line
            line = train_time[i]["LineId"]["Line"]["Name"]
            direction = train_time[i]["LineId"]["Direction"]
            for j in range(len(train_time[i]["Stops"])):
                # Station
                station = train_time[i]["Stops"][j]["Station"]
            
                # Departs
                depart = train_time[i]["Stops"][j]["Departs"]
                station_depart = self.split_time(depart)
                
                # Arrives
                arrive = train_time[i]["Stops"][j]["Arrives"]
                station_arrive = self.split_time(arrive)
                
                # make node name
                station_depart_node = station + "+" + line + "+" + str(direction) + "+" + str(station_depart[0]) + "+" + str(station_depart[1]) + "+" + "depart"
                station_arrive_node = station + "+" + line + "+" + str(direction) + "+" + str(station_arrive[0]) + "+" + str(station_arrive[1]) + "+" + "arrive"
                Graph.add_node(station_depart_node)
                Graph.add_node(station_arrive_node)

                weight = None
                if before_depart_node is not None:
                    # make edge with weight
                    depart = self.fetch_time(before_depart_node)
                    arrive = self.fetch_time(station_arrive_node)
                    # arrive - depart (depart => arrive)
                    weight = self.compare_time(depart, arrive)
                    Graph.add_edge(before_depart_node, station_arrive_node, weight = weight )

                if i==1000 and weight is not None:
                    print before_depart_node + " -> " + station_arrive_node + " " + str(weight)

                before_depart_node = station_depart_node

                # add node_dict
                # ex. key: 品川-山手線-depart => [node_name1, node_name2, ...]
                if station + "-" + line in transfer_list:
                    if station + "-" + line + "-depart" in node_dict.keys():
                        node_dict[station + "-" + line + "-depart"].append(station_depart_node)
                        node_dict[station + "-" + line + "-arrive"].append(station_arrive_node)
                    else:
                        node_dict[station + "-" + line + "-depart"] = [station_depart_node]
                        node_dict[station + "-" + line + "-arrive"] = [station_arrive_node]

            # reset
            before_depart_node = None
        
        # for i in Graph.edges():
        #     if u"品川+山手線+-1" in i[0]:
        #         print i[0], i[1]

        return Graph, node_dict

    def split_time(self, time_str):
        time_str = time_str.split(":")
        hour = time_str[0].split("T")
        hour = hour[1]
        if hour[0] == '0' and len(hour) > 1:
            hour = hour[1]
        minute = time_str[1]
        return [hour, minute]

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

    def make_graph_of_transfer_stations(self, Graph, transfer_dict, node_dict):
        for i in node_dict.keys():
            node_name = i.split("-")
            node_name1 = node_name[0] + "-" + node_name[1] # station-line
            node_name2 = node_name[2] # depart or arrive
            if node_name2 == "arrive":
                transfer_stations = transfer_dict[node_name1]
                node_list_p = node_dict[i]
                for j in transfer_stations:
                    j_new = j + "-" + "depart"
                    node_list_c = node_dict[j_new]
                    for k in node_list_p:
                        min_weight = 100
                        for l in node_list_c:
                            depart = self.fetch_time(l)
                            arrive = self.fetch_time(k)
                            # depart - arrive (arrive => depart)
                            weight = self.compare_time(arrive, depart)
                            # if min_weight > weight:
                            #     min_weight = weight
                            #     tmp_k = k
                            #     tmp_l = l
                            #     Graph.add_edge(tmp_k, tmp_l, weight = weight )
                            if weight > 0 and weight < 30:
                               Graph.add_edge(k, l, weight = weight )
                               #print k + " -> " + l + " " + str(weight)
        return Graph

    def fetch_line(self, name, node_dict, mode, time):
        answer_list = []
        tmp = None
        train_candidates = node_dict[name]
        flag1 = True
        flag2 = True
        for i in train_candidates:
            # 品川+山手線+-1+4+14+depart
            word = i.split('+')
            if mode == word[5]:
                hour = time[0]
                minute = time[1]
                if (hour < int(word[3]) or hour == int(word[3])) and (minute < int(word[4]) or minute == int(word[4])):
                    if mode == "depart" and flag1:
                        if word[2] == "1":
                            answer_list.append(i)
                            flag1 = False
                    if mode == "depart" and flag2:
                        if word[2] == "-1":
                            answer_list.append(i)
                            flag2 = False
                        #break
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

    # for i in graph.edges():
    #     print i[0], i[1]

    start = u"品川-山手線-depart"
    start = u"渋谷-東横線-depart"
    #end = u"中目黒-日比谷線"
    end = u"品川-山手線-arrive"
    end = u"自由が丘-大井町線-arrive"
    start_st = node_dict[start]
    end_st = node_dict[end]


    #end = u"渋谷-東横線-arrive"

    time = make_graph.what_time_now()
    
    #start_st = make_graph.fetch_line(start, node_dict, "depart", time=time)
    #end_st = make_graph.fetch_line(end, node_dict, "arrive", time=time)
    
    for i in start_st:
        print i

    # for  i in end_st:
    #     print i

    #for i in node_dict[start]:
    #    print i

    #for i in node_dict[end]:
    #    print i

    #path = networkx.dijkstra_path(graph, u'品川+山手線+-1+15+04+depart', u'中目黒+日比谷線+-1+16+22+arrive')
    #path = networkx.dijkstra_path(graph, u'品川+山手線+-1+4+14+depart', u'田町+山手線+-1+4+19+arrive')
    #print path

    for i in start_st:
        for j in end_st:
            try:
                print i + ", " + j
                path = networkx.dijkstra_path(graph, i, j)

                for k in path:
                    print k
            except:
                print " "

# file reading #

f = open("trains.json", 'r')
train_time = json.load(f)

f2 = open("net.json", 'r')
train_route = json.load(f2)

make_graph_test(train_time, train_route)

