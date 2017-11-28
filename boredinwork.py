#!/usr/bin/env python3.5

import os
import sys
import json
import signal
import requests
from random import randint


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, GObject
from gi.repository import AppIndicator3
from gi.repository import Notify

app_name = 'BoredInWork'


def menu():
    menu = Gtk.Menu()
    item_bash = Gtk.MenuItem('Bash')
    item_bash.connect('activate', bash)
    menu.append(item_bash)
    
    item_chuck = Gtk.MenuItem('Chuck')
    item_chuck.connect('activate', chuck)
    menu.append(item_chuck)
    
    item_quit = Gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu

def fetch_bash_rand():
    url = 'http://bash.org.pl/random/'
    r = requests.get(url)
    result = r.text.split('<div class="quote post-content post-body">')[-1].split('</div>')[0]
    return result.lstrip()
    
def fetch_chuck_rand():
    url = 'http://api.icndb.com/jokes/random'
    r = requests.get(url)
    result = json.loads(r.text)['value']['joke']
    return result

def bash(_):
    n = Notify.Notification.new(" ", fetch_bash_rand(), None)
    n.set_timeout(200000)
    n.show()
    
def chuck(_):
    n = Notify.Notification.new(" ", fetch_chuck_rand(), None)
    n.set_timeout(200000)
    n.show()

def quit(_):
    Notify.uninit()
    Gtk.main_quit()

def main():
    indicator = AppIndicator3.Indicator.new(app_name, "indicator-messages", AppIndicator3.IndicatorCategory.APPLICATION_STATUS)    
    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    indicator.set_menu(menu())
    Notify.init(app_name)
    
    Gtk.main()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
