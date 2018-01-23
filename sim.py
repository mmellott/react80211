#!/usr/bin/python

from helpers.conn_matrix import ConnMatrix
from react.auctioneer import Auctioneer
from react.bidder import Bidder

from collections import namedtuple
import Queue
import sys

class ReactSimNode(object):
    ReactMessage = namedtuple('ReactMessage', 'name claim offer')

    def __init__(self, name, capacity, demand):
        self.name = name
        self.auctioneer = Auctioneer(capacity)
        self.bidder = Bidder(demand)

        self.last_claim = None
        self.last_offer = None

    def store(self, msg):
        self.auctioneer.store(msg.name, msg.claim)
        self.bidder.store(msg.name, msg.offer)

    def update(self):
        msg = self.ReactMessage(name=self.name, claim=self.bidder.update(),
                offer=self.auctioneer.update())

        changed = False
        if msg.claim != self.last_claim:
            changed = True
            self.last_claim = msg.claim
        if msg.offer != self.last_offer:
            changed = True
            self.last_offer = msg.offer

        return msg, changed

#names = ['a', 'b', 'c', 'd']
cm = ConnMatrix()
nodes = {}

nodes['a'] = ReactSimNode('a', 1.0, 1.0)
nodes['b'] = ReactSimNode('b', 1.0, 1.0)
nodes['c'] = ReactSimNode('c', 1.0, 1.0)
nodes['d'] = ReactSimNode('d', 1.0, 1.0)
nodes['e'] = ReactSimNode('e', 1.0, 1.0)
nodes['f'] = ReactSimNode('e', 1.0, 1.0)

cm.add('a', r'f|b')
cm.add('b', r'a|c')
cm.add('c', r'b|d')
cm.add('d', r'c|e')
cm.add('e', r'd|f')
cm.add('f', r'e|a')

done = False
rnd = 0
q = Queue.Queue()
while not(done):
    done = True

    for n in nodes:
        msg, changed = nodes[n].update()
        q.put(msg)
        if changed:
            done = False

    while not(q.empty()):
        msg = q.get()

        for n in cm.links(msg.name):
            nodes[n].store(msg)

    sys.stdout.write('After {} rounds:'.format(rnd))
    for n in nodes:
        sys.stdout.write(' ({}, {})'.format(nodes[n].last_claim,
                nodes[n].last_offer))
    sys.stdout.write('\n')

    rnd += 1