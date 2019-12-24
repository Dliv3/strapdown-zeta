#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pyinotify
import sys
import logging
import json

WEB_DIR = sys.argv[1]

if len(sys.argv) > 2:
    LOG_FILE = sys.argv[2]
else:
    LOG_FILE = "/tmp/log"

# 递归监控
WATCHED_DIR = [
    WEB_DIR,
]

UNWATCHED_DIR = os.path.join(WEB_DIR, ".git")

def json_save():
    with open(os.path.join(WEB_DIR, "list.json"),"w") as f:
        json.dump(MARKDOWNS, f)

MARKDOWNS = []

# 初始化markdown
for root, dirs, files in os.walk(WEB_DIR, topdown=True):
    for name in files:
        # print(os.path.join(root, name))
        path = os.path.join(root, name)
        if not path.startswith(UNWATCHED_DIR):
            MARKDOWNS.append(path[len(WEB_DIR)+1:])

print MARKDOWNS

LOG_FORMAT = '%(asctime)s: %(message)s'

logging.basicConfig(level=logging.DEBUG,
                    iformat=LOG_FORMAT,
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=LOG_FILE,
                    filemode='a')

console = logging.StreamHandler()
formatter = logging.Formatter(LOG_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class Monitor(pyinotify.ProcessEvent):

    def process_IN_CREATE(self, event):
        target = event.pathname
        if target.startswith(UNWATCHED_DIR):
            return
        if target.endswith(".md"):
            MARKDOWNS.append(event.pathname[len(WEB_DIR)+1:])
            logging.critical('[CREATE]'+event.pathname)
            json_save()


class Reload(Exception):
    pass

wm = pyinotify.WatchManager()
mask = pyinotify.IN_CREATE
wdd = wm.add_watch(WATCHED_DIR, mask, auto_add=True, rec=True)
process = Monitor()
notifier = pyinotify.Notifier(wm, process)

while True:
    try:
        while True:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        break
