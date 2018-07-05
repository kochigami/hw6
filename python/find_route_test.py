#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, codecs
from find_route import FindRoute

f = open("net.json", 'r')
train_route = json.load(f)

class FindRouteTest():
    def transfer_station(self,train_route):
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

        #for i in transfer_station:
        #    print i

        return transfer_station

# for i in range(len(route)):
#     print "---" + route[i][0] + "---"
#     for j in range(1,len(route[i])):
#         print route[i][j]
#     print "\n"


find_route = FindRoute()
#start = u"品川-山手線"
#start = u"秋葉原-日比谷線"
#end = u"千鳥町-池上線"

start=u"品川-山手線"
end=u"目黒-目黒線"
#end = u"五反田-山手線"
print(start + " => " + end)
#path = find_route.search(station, route, start, end)
#path = find_route.choose_least_transfers(path)
#for i in range(len(path)):
#    print(path[i])
