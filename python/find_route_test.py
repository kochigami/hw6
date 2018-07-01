#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, codecs
from find_route import FindRoute

f = open("net.json", 'r')
train_route = json.load(f)
line_num = len(train_route)
station_num = []
route = []
for i in range(line_num):
    station_num.append(len(train_route[i]['Stations']))

for i in range(line_num):
    for j in range(station_num[i]):
        current_station = train_route[i]['Stations'][j] + "-" + train_route[i]['Name']
        prev_station = None
        next_station = None
        route.append([current_station])
        current_pos = len(route) - 1
        if j > 0:
            prev_station = train_route[i]['Stations'][j-1] + "-" + train_route[i]['Name']
            route[current_pos].append(prev_station)
            #print prev_station
        if j < station_num[i] -1:
            next_station = train_route[i]['Stations'][j+1] + "-" + train_route[i]['Name']
            route[current_pos].append(next_station)
            #print next_station

    for i in range(len(route)):
        for j in range(len(route)):
            str1 = route[i][0].split("-")
            str2 = route[j][0].split("-")
            if i != j and str1[0] == str2[0]:
                route[i].append(route[j][0])

#print route

find_route = FindRoute()
start = u"品川-山手線"
end = u"自由が丘-大井町線"
end = u"五反田-山手線"
print(start + " => " + end)
path = find_route.search(route, start, end)
for i in range(len(path)):
    print(path[i])
