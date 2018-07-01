#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

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

class ShuffleWords(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        self.response.write(
            """
            <form action="shuffle_words" method="post">
            <input type=text placeholder="１番目の単語を入力してね" name=q1>
            <br>
            <input type=text placeholder="２番目の単語を入力してね" name=q2>
            <br>
            <input type=submit>
            </form>
            """
            )
        q1 = self.request.get('q1')
        q2 = self.request.get('q2')
        if self.check_input(q1, q2):
            q3 = self.mix_query(q1, q2)
            self.response.write("=> " + q3)
        self.response.write(
            """
            <form action="/" method="get">
            <input type="submit" value="Back to Menu">
            </form>
            """
            )


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

    def check_input(self, q1, q2):
        if len(q1) > 0 and len(q2) > 0:
            return True
        else:
            return False

class TrainTransit(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
        self.response.write("train trainsit")
        self.response.write(
            """
            <form action="/" method="get">
            <input type="submit" value="Back to Menu">
            </form>
            """
            )

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/shuffle_words', ShuffleWords),
    ('/train_transit', TrainTransit)
], debug=True)
