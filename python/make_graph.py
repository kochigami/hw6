#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, codecs
import networkx
import datetime

class MakeGraph():
    # 乗り換え駅リスト["五反田-山手線", "目黒-山手線", ..., "目黒-目黒線", "五反田-池上線", ...]
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

    # 乗り換え駅 dict dict["五反田-山手線"] = ["五反田-池上線"], dict["五反田-池上線"] = ["五反田-山手線"], ... 
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

    # 駅名，路線名が同じで時間が違うノードをつなぐ
    # arrive（昔） => depart （新） の流れでつなぐ
    def connect_same_station(self, graph, all_node_dict):
        for i in all_node_dict.keys():
            node_name = i.split("-")
            node_name1 = node_name[0] + "-" + node_name[1] # station-line
            node_name2 = node_name[2] # depart or arrive
            if node_name2 == "arrive":
                for j in all_node_dict.keys():
                    node_name_c = j.split("-")
                    node_name1_c = node_name_c[0] + "-" + node_name_c[1] # station-line
                    node_name2_c = node_name_c[2] # depart or arrive
                    if node_name1 == node_name1_c and node_name2_c == "depart":
                        for k in all_node_dict[i]:
                            for l in all_node_dict[j]:
                                arrive = self.fetch_time(k)
                                depart = self.fetch_time(l)
                                # depart - arrive (arrive => depart)
                                weight = self.compare_time(arrive, depart)
                                # 30分未満の乗り換え時間になるものをつなぐ
                                if weight > 0 and weight < 30:
                                    graph.add_edge(k, l, weight = weight )

        return graph

    # make graph 全体の関数 (乗り換え駅リスト，乗り換え駅dict作成，同じ路線で辺をつなぐ，同じ駅で辺をつなぐ，乗り換え駅で辺をつなぐ)
    def make_graph(self, train_time, train_route):
        transfer_list, transfer_dict = self.add_transfer_station(train_route)
        # make_graph_of_same_line
        Graph, node_dict, all_node_dict = self.make_graph_of_same_line(train_time, transfer_list)
        # connect same station with different time
        Graph = self.connect_same_station(Graph, all_node_dict)
        # make_graph_of_transfer_station
        Graph = self.make_graph_of_transfer_stations(Graph, transfer_dict, node_dict)
        return Graph, node_dict, all_node_dict

    # 同じ路線で辺をつなぐ　例：品川-山手線　=> 田町-山手線
    # arrive (古) => depart (新)　の順につなぐ
    # trains.json の電車の番号ごとに駅をつなぐ

    # all_node_dict 
    # all_node_dict[品川-山手線-arrive] = [nodeA, nodeB, nodeC, ..., nodeZ]
    # all_node_dict[品川-山手線-depart] = [nodeA', nodeB', nodeC', ..., nodeZ']

    # node_dict
    # 乗り換えリストに含まれる駅のみ辞書にしたもの
    # node_dict["五反田-池上線"] = [nodeA, nodeB, ..., nodeZ]
    def make_graph_of_same_line(self, train_time, transfer_list):
        Graph = networkx.DiGraph()
        train_num = len(train_time)
        node_dict = {}
        all_node_dict = {}
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

                before_depart_node = station_depart_node

                # add all_node_dict
                if station + "-" + line + "-depart" in all_node_dict.keys():
                        all_node_dict[station + "-" + line + "-depart"].append(station_depart_node)
                        all_node_dict[station + "-" + line + "-arrive"].append(station_arrive_node)
                else:
                    all_node_dict[station + "-" + line + "-depart"] = [station_depart_node]
                    all_node_dict[station + "-" + line + "-arrive"] = [station_arrive_node]

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
        
        return Graph, node_dict, all_node_dict

    # jsonファイルの文字列から時間と分をとりだす
    # 03 => 3 のように，頭に0がついていたら取る
    def split_time(self, time_str):
        time_str = time_str.split(":")
        hour = time_str[0].split("T")
        hour = hour[1]
        if hour[0] == '0' and len(hour) > 1:
            hour = hour[1]
        if time_str[1][0] == '0' and len(time_str[1]) > 1:
            minute = time_str[1][1]
        else:
            minute = time_str[1]
        return [hour, minute]

    # node名から駅名-路線名を取り出す
    def fetch_station_name(self, node_name):
        word = node_name.split("+")
        return word[0] + "-" + word[1]

    # node名から時間と分を取り出す
    # 03 => 3 のように，頭に0がついていたら取る
    def fetch_time(self, node_name):
        word = node_name.split("+")
        if word[3][0] == '0' and len(word[3]) > 1:
            hour = word[3][1]
        else:
            hour = word[3]
        if word[4][0] == '0' and len(word[4]) > 1:
            minute = word[4][1]
        else:
            minute = word[4]            
        return [int(hour), int(minute)]

    # かかる時間を計算する
    # weightとして加える
    def compare_time(self, start, end):
        start_min = start[0] * 60 + start[1]
        end_min = end[0] * 60 + end[1]
        return end_min - start_min

    # 乗り換え駅の間をつなぐ
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
                        for l in node_list_c:
                            depart = self.fetch_time(l)
                            arrive = self.fetch_time(k)
                            # depart - arrive (arrive => depart)
                            weight = self.compare_time(arrive, depart)
                            # 30分未満の乗り換え時間になるものをつなぐ
                            if weight > 0 and weight < 30:
                               Graph.add_edge(k, l, weight = weight )
        return Graph

    # 現在の時間より遅い時間のノードのリストを返す
    # 無駄が多いと思う
    # 品川-山手線のみ，出発で終点の品川駅 (trains.jsonの山手線30番目に出てくる品川駅) を選ぶと進めなくなるので，省いている
    def fetch_line(self, name, node_dict, time):
        answer_list = []
        tmp = None
        train_candidates = node_dict[name]
        flag1 = True
        flag2 = True
        name = name.split("-")
        hour = time[0]
        minute = time[1]
        current_time = datetime.datetime(2018, 1, 1, int(hour), int(minute))
        if name[2] == "depart":
            for i in range(len(train_candidates)):
                # ex. train_candidates[i]: 品川+山手線+-1+4+14+depart
                word = train_candidates[i].split('+')
                if u"品川+山手線" in train_candidates[i]: 
                    if i%2 == 0:
                        if word[5] == "depart": # direction (depart/ arrive) is equal
                            planned_time = datetime.datetime(2018, 1, 1, int(word[3]), int(word[4]))
                            if current_time < planned_time:
                                if word[2] == "1":
                                    answer_list.append(train_candidates[i])
                                    break

                else:
                    if word[5] == "depart": # direction (depart/ arrive) is equal
                        planned_time = datetime.datetime(2018, 1, 1, int(word[3]), int(word[4]))
                        if current_time < planned_time:
                            if word[2] == "1":
                                answer_list.append(train_candidates[i])
                                break

            for i in range(len(train_candidates)):
                word = train_candidates[i].split('+')
                if u"品川+山手線" in train_candidates[i]: 
                    if i%2 == 0:
                        if word[5] == "depart": # direction (depart/ arrive) is equal
                            planned_time = datetime.datetime(2018, 1, 1, int(word[3]), int(word[4]))
                            if current_time < planned_time:
                                if word[2] == "-1":
                                    answer_list.append(train_candidates[i])
                                    break
                else:
                    if word[5] == "depart": # direction (depart/ arrive) is equal
                        planned_time = datetime.datetime(2018, 1, 1, int(word[3]), int(word[4]))
                        if current_time < planned_time:
                            if word[2] == "-1":
                                answer_list.append(train_candidates[i])
                                break
        else:
            for i in range(len(train_candidates)):
                word = train_candidates[i].split('+')
                if word[5] == "arrive": # direction (depart/ arrive) is equal
                    planned_time = datetime.datetime(2018, 1, 1, int(word[3]), int(word[4]))
                    if current_time < planned_time:
                        answer_list.append(train_candidates[i])

        return answer_list

    # 現在の時間を返す
    def what_time_now(self):
        today = datetime.datetime.now()
        hour = today.hour
        minute = today.minute
        return [hour, minute]

# 経路検索のテスト
def test(train_data, train_route, option="fastest"):

    make_graph = MakeGraph()

    # make graph (station with time)
    print "start making graph structure"
    graph, node_dict, all_node_dict = make_graph.make_graph(train_data, train_route)
    print "finish making graph structure"


    # set start and end
    # TODO: if application, add information via pushed button to "-depart" or "-start"
    start = u"品川-山手線-depart"
    start = u"大崎-山手線-depart"
    start = u"渋谷-東横線-depart"

    end = u"自由が丘-大井町線-arrive"
    end = u"中目黒-日比谷線-arrive"
    end = u"目黒-目黒線-arrive"
    end = u"大崎-山手線-arrive"
    end = u"品川-山手線-arrive"


    # get current time
    time = make_graph.what_time_now()
    
    # check same station?
    s = start.split("-")
    e = end.split("-")
    if s[0] == e[0]:
        print "You already reach the goal!"

    # if start and end are different, search path
    else:
        start_st = make_graph.fetch_line(start, all_node_dict, time=time)
        end_st = make_graph.fetch_line(end, all_node_dict, time=time)
    
        # 時間優先
        if option == "fastest":
            path = None
            min_weight = 10000
            for i in start_st:
                for j in end_st:
                    if networkx.has_path(graph, i, j):
                        weight = networkx.dijkstra_path_length(graph, i, j)
                        print weight
                        if min_weight > weight:
                            path = networkx.dijkstra_path(graph, i, j)
                            min_weight = weight
            if path is None:
                print "not found"
            else:
                for i in path:
                    print i

        else:
            # 乗り換え回数優先
            path_list = []
            for i in start_st:
                for j in end_st:
                    if networkx.has_path(graph, i, j):
                        path_list.append(networkx.dijkstra_path(graph, i, j))

            if len(path_list) == 0:
                print "not found"
            else:
                min_transfer = 10000
                path = None
                for i in range(len(path_list)):
                    count = 0
                    current_line = ""
                    for j in path_list[i]:
                        word = j.split("+")
                        if current_line != word[1]:
                            count += 1
                            current_line = word[1]
                    if min_transfer > count:
                        path = path_list[i]
                        min_transfer = count

                if path is None:
                    print "not found"
                else:
                    for i in path:
                        print i

# file reading #

f = open("trains.json", 'r')
train_time = json.load(f)

f2 = open("net.json", 'r')
train_route = json.load(f2)

test(train_time, train_route)

