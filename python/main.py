#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
from google.appengine.api import urlfetch
import json, codecs

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
        response = urlfetch.fetch(url)
        if response.status_code == 200:
            train_route = json.loads(response.content)
            line_num = len(train_route)
            station_num = []
            route = []
            for i in range(line_num):
                station_num.append(len(train_route[i]['Stations']))

            for i in range(line_num):
                for j in range(station_num[i]):
                    current_station = train_route[i]['Stations'][j]
                    prev_station = None
                    next_station = None
                    if j > 0:
                        prev_station = train_route[i]['Stations'][j-1]
                    if j < station_num[i] -1:
                        next_station = train_route[i]['Stations'][j+1]
                    new_station = True
                    for k in range(len(route)):
                        if route[k][0] == current_station:
                            new_station = False
                            if prev_station is not None:
                                flag = True
                                for s in range(1, len(route[k])):
                                    if prev_station == route[k][s]:
                                        flag = False
                                        break
                                if flag:
                                    route[k].append(prev_station)
                            if next_station is not None:
                                flag = True
                                for s in range(1, len(route[k])):
                                    if next_station == route[k][s]:
                                        flag = False
                                        break
                                if flag:
                                    route[k].append(next_station)
                            break
                        
                    if new_station:
                        m = len(route)
                        route.append([current_station])
                        if prev_station is not None:
                            route[m].append(prev_station)
                        if next_station is not None:
                            route[m].append(next_station)
            return route
    
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
                    tag += "<option value=" + current_station + ">" + current_station + "</option>"
                tag += "</optgroup>"
        return tag

    def post(self):
        utils = Utils()
        url = "http://fantasy-transit.appspot.com/net?format=json"
        self.read_route(url)

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
            <input type=submit>
            </form>
            """
        )
        
        start = self.request.get('start')
        end = self.request.get('end')
        if utils.check_input(start, end):
            self.response.write(start + " => " + end)
        
        # FIXME: find route

        self.response.write(utils.back_to_menu())

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/shuffle_words', ShuffleWords),
    ('/train_transit', TrainTransit)
], debug=True)
