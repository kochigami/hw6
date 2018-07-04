#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, codecs

f = open("trains.json", 'r')
train_time = json.load(f)
print train_time[0]["Stops"][0] # Station, Arrives, Departs 
print train_time[0]["Stops"][0]["Station"] # 品川
print train_time[0]["Stops"][0]["Arrives"]

train_num = len(train_time)
print train_num

yamanote_up = []
yamanote_down = []

print train_time[0]["LineId"]["Line"]["Name"]


# start, end, line
# time 
# start -> end の順番 (事前に計算できるといいのかな) 1

#start_arrive = []
for i in range(train_num):
    if train_time[i]["LineId"]["Line"]["Name"] == u"山手線" and train_time[i]["LineId"]["Direction"] == 1:
        for j in range(len(train_time[i])):
            #yamanote_down.append
            if train_time[i]["Stops"][j]["Station"] == u"品川": # start
                # time < train_time[i]["Stops"][j]["Departs"]なら追加し，
                # time > train_time[i]["Stops"][j]["Departs"]になった手前のものを採用
                # end の駅まで辿って，Arrivesを取得 => 次の乗り換えのDepartsになる
                pass
                #start_arrive.append(train_time[i]["Stops"][j]["Arrives"])

#print start_arrive

# choose time
