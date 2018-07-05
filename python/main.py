#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from google.appengine.api import urlfetch
import json, codecs
from find_route import FindRoute

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        self.response.write(
            """
            <form action="shuffle_words" method="post">
            <input type="submit" value="Shuffle Words">
            </form>
            <form action="train_transit" method="post">
            <input type="submit" value="Train Transit">
            </form>
            """
            )

class Utils():    
    def check_input(self, q1, q2):
        if len(q1) > 0 and len(q2) > 0:
            return True
        else:
            return False

    def back_to_menu(self):
        back_to_menu="""
        <form action="/" method="get">
        <input type="submit" value="Back to Menu">
        </form>
        """
        return back_to_menu

class ShuffleWords(webapp2.RequestHandler):
    def post(self):
        utils = Utils()
        self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        self.response.write(
            """
            <form action="shuffle_words" method="post">
            <input type=text placeholder="１つ目の単語を入力してね" name=q1>
            <br>
            <input type=text placeholder="２つ目の単語を入力してね" name=q2>
            <br>
            <input type=submit>
            </form>
            """
            )
        q1 = self.request.get('q1')
        q2 = self.request.get('q2')
        if utils.check_input(q1, q2):
            q3 = self.mix_query(q1, q2)
            self.response.write("=> " + q3)
        self.response.write(utils.back_to_menu())

    def mix_query(self, q1, q2):
        i = 0
        string = ''
        min_string = min(len(q1), len(q2))
        for i in range(min_string):
            string += q1[i] + q2[i]
        i+=1
        if len(q1) - i > 0:
            for j in range(i, len(q1)):
                string += q1[j]
        elif len(q2)- i > 0:
            for j in range(i, len(q2)):
                string += q2[j]
        return string

class TrainTransit(webapp2.RequestHandler):
    def read_route(self, url):
        route = []
        station = {}
        response = urlfetch.fetch(url)
        if response.status_code == 200:
            train_route = json.loads(response.content)
            line_num = len(train_route)
            station_num = []
            for i in range(line_num):
                station_num.append(len(train_route[i]['Stations']))

            for i in range(line_num):
                for j in range(station_num[i]):
                    current_station = train_route[i]['Stations'][j] + "-" + train_route[i]['Name']
                    prev_station = None
                    next_station = None
                    route.append([current_station])
                    current_pos = len(route) - 1
                    station[current_station] = current_pos
                    if j > 0:
                        prev_station = train_route[i]['Stations'][j-1] + "-" + train_route[i]['Name']
                        route[current_pos].append(prev_station)
                    if j < station_num[i] -1:
                        next_station = train_route[i]['Stations'][j+1] + "-" + train_route[i]['Name']
                        route[current_pos].append(next_station)

            for i in range(len(route)):
                for j in range(len(route)):
                    str1 = route[i][0].split("-")
                    str2 = route[j][0].split("-")
                    if  str1[0] == str2[0] and route[i][0] != route[j][0]:
                        route[i].append(route[j][0])
            ###
            # for i in range(len(route)):
            #     self.response.write("---" + route[i][0] + "---")
            #     self.response.write("<br>")
            #     self.response.write("<br>")

            #     for j in range(1,len(route[i])):
            #         print self.response.write(route[i][j])
            #         self.response.write("<br>")
            #     self.response.write("<br>")

        return station, route
    
    def train_option(self, url):
        response = urlfetch.fetch(url)
        if response.status_code == 200:
            train_route = json.loads(response.content)
            line_num = len(train_route)
            station_num = []
            for i in range(line_num):
                station_num.append(len(train_route[i]['Stations']))

            tag = ""
            for i in range(line_num):
                tag += "<optgroup label=" + train_route[i]['Name'] + ">"

                for j in range(station_num[i]):
                    current_station = train_route[i]['Stations'][j]
                    current_station_with_line = current_station + "-" + train_route[i]['Name']
                    tag += "<option value=" + current_station_with_line + ">" + current_station + "</option>"
                tag += "</optgroup>"
        return tag

    def show_path(self, path):
        self.response.write(path[0].split("-")[0])
        self.response.write(" (" + path[0].split("-")[1] + ") ")
        self.response.write("<br>")
        self.response.write("↓ ")
        self.response.write("<br>")

        current_line = path[0].split("-")[1]
        for i in range(1, len(path)-1):
            station = path[i].split("-")[0]
            line = path[i].split("-")[1]
            if current_line != line:
                current_line = line
                self.response.write(path[i-1].split("-")[0])
                self.response.write(" (" + path[i-1].split("-")[1] + ") ")
                self.response.write("<br>")
                self.response.write("↓ ")
                self.response.write("<br>")
                self.response.write(path[i].split("-")[0])
                self.response.write(" (" + path[i].split("-")[1] + ") ")
                self.response.write("<br>")
                self.response.write("↓ ")
                self.response.write("<br>")

        line = path[len(path)-1].split("-")[1]
        if current_line != line and len(path) > 1:
            self.response.write(path[len(path)-2].split("-")[0])
            self.response.write(" (" + path[len(path)-2].split("-")[1] + ")")
            self.response.write("<br>")
            self.response.write("↓ ")
            self.response.write("<br>")
        self.response.write(path[len(path)-1].split("-")[0])
        self.response.write(" (" + path[len(path)-1].split("-")[1] + ")")
        self.response.write("<br>")

    def post(self):
        utils = Utils()
        url = "http://fantasy-transit.appspot.com/net?format=json"
        station, route = self.read_route(url)

        self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        
        self.response.write(
            """
            <form action="train_transit" method="post">
            <select name="start">
            """
            +
            self.train_option(url)
            +
            """
            </select>
            <br>
            <select name="end">
            """
            +
            self.train_option(url)
            +
            """
            </select>
            <br>
            <input type=submit value="Search">
            </form>
            """
        )
        
        start = self.request.get('start')
        end = self.request.get('end')
        if utils.check_input(start, end):
            self.response.write(start + " => " + end)
            self.response.write("<br>")
            self.response.write("<br>")
            find_route = FindRoute()
            path = find_route.search(station, route, start, end)
            self.show_path(path)
        
        self.response.write(utils.back_to_menu())

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/shuffle_words', ShuffleWords),
    ('/train_transit', TrainTransit)
], debug=True)
