import os
import sys
import signal
import curses
from copy import deepcopy
from datetime import datetime
from argparse import ArgumentParser
from curses.textpad import Textbox,rectangle
from haproxystats import HAProxyServer

from haproxytop.menu import run_menu
from haproxytop.util import format_bytes
from haproxytop.version import version

_startcol = 2

"""
*VIEWS*
Columns for each view are defined in a tuple:
(<HEADER>, <WIDTH>, <ATTRIBUTE>, <SORT FUNC>)
"""

_realtime = [
        ('NAME', 30, 'name', lambda x: x.name),
        ('STATUS', 7, 'status', lambda x: x.status),
        ('SESSIONS', 9, ('scur', 'slim'), lambda x: x.scur),
        ('REQUESTS', 9, ('req_rate', 'req_tot'), lambda x: x.req_rate),
        ('NET I/O', 20, ('bin', 'bout'), lambda x: x.bin + x.bout),
        ('CRQ TIME', 20, ('ctime', 'rtime', 'qtime', 'ttime'), None),
        ('PROXY', 15, 'proxy_name', lambda x: x.proxy_name)
    ]

views = { 'realtime': _realtime }

class HAProxyTop(object):
    def __init__(self, server_list, filter=None):
        #set initial display options
        self.tree = True
        self.filter = filter
        self.counters = {}
        self.active_view = 'realtime'
        self.valid_filters = [ 'proxy_name', 'name' ]
        self.sort = { 'func': views[self.active_view][0][3], 'reversed': False }


        self.servers = [ HAProxyServer(s) for s in server_list ]

        while True:
            self.display(self.poll())

    def sig_handler(self, signal, frame):
        curses.endwin()
        sys.exit(0)

    def poll(self):
        display_items = []
        
        for s in self.servers:
            s.update()
            display_items += s.backends

        self.counters['proxies'] = len(self.servers)
        self.counters['backends'] = len(display_items)
        self.counters['listeners'] = sum([len(i.listeners) for i in display_items]) 

        return sorted(display_items, key=self.sort['func'], reverse=self.sort['reversed'])

#        if self.filter:
#            ftype,fvalue = self.filter.split(':')
#            self.display_stats = [ s for s in self.display_stats \
#                                         if fvalue in s[ftype] ]

    def _get_counter_msg(self):
        return '%d proxy %d backends %d listeners' % \
                (self.counters['proxies'],
                 self.counters['backends'],
                 self.counters['listeners'])

    def _truncate(self, s, max_len):
        i = max_len -4
        return s[:i] + '...'

    def display(self, backends):
        s = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.noecho()
        curses.curs_set(0)
        s.timeout(1000)
        s.border(0)

        h,w = s.getmaxyx()
        signal.signal(signal.SIGINT, self.sig_handler)
        s.clear()
       
        #first line
        s.addstr(1, 2, 'haproxytop -')
        s.addstr(1, 15, datetime.now().strftime('%H:%M:%S'))
        s.addstr(1, 26, self._get_counter_msg())
        if self.filter:
            s.addstr(1, 42, ('filter: %s' % self.filter))

        columns = views[self.active_view]

        #second line, column headers
        x_pos = _startcol
        for c in columns:
            s.addstr(3, x_pos, c[0], curses.A_BOLD)
            x_pos += c[1]

        #remainder of lines
        y_pos = 5
        maxlines = h - 2

        for b in backends:
            x_pos = _startcol
            for c in columns:
                width = c[1]
                if isinstance(c[2], tuple):
                    if c[0] == 'NET I/O':
                        values = [ format_bytes(b.__getattribute__(i)) for i in c[2] ]
                    else:
                        values = [ str(b.__getattribute__(i)) for i in c[2] ]
                    value = ' / '.join([ v if v else '-' for v in values ])
                else:
                    value = str(b.__getattribute__(c[2]))


                if len(value) >= width:
                    value = self._truncate(value, width)

                if c[0] == 'NAME':
                    if not self.tree:
                        value = '%s (%d listeners)' % (value, len(b.listeners))
                    s.addstr(y_pos, x_pos, value, curses.color_pair(6))
                elif c[0] == 'STATUS':
                    if value == 'UP':
                        s.addstr(y_pos, x_pos, value, curses.color_pair(3))
                    else:
                        s.addstr(y_pos, x_pos, value, curses.color_pair(1))
                else:
                    s.addstr(y_pos, x_pos, value)

                x_pos += width
            if y_pos >= maxlines:
                break
            else:
                y_pos += 1
            
            if self.tree:
                for l in b.listeners:
                    x_pos = _startcol
                    for c in columns:
                        width = c[1]
                        if isinstance(c[2], tuple):
                            if c[0] == 'NET I/O':
                                values = [ format_bytes(l.__getattribute__(i)) for i in c[2] ]
                            else:
                                values = [ str(l.__getattribute__(i)) for i in c[2] ]
                            value = ' / '.join([ v if v else '-' for v in values ])
                        else:
                            value = str(l.__getattribute__(c[2]))
                        
                        if c[0] == 'NAME':
                            value = '├ ' + value

                        if len(value) >= width:
                            value = self._truncate(value, width)
                        
                        if c[0] == 'STATUS':
                            if value == 'UP':
                                s.addstr(y_pos, x_pos, value, curses.color_pair(3))
                            else:
                                s.addstr(y_pos, x_pos, value, curses.color_pair(1))
                        else:
                            s.addstr(y_pos, x_pos, value)

                        x_pos += width

                    if y_pos >= maxlines:
                        break
                    else:
                        y_pos += 1

        s.refresh()

        x = s.getch()
        if x == ord('q'):
            curses.endwin()
            sys.exit(0)

        if x == ord('h') or x == ord('?'):
            s.clear()
            startx = int(w / 2 - 20) # I have no idea why this offset of 20 is needed

            print(type(startx))
            s.addstr(6, startx+1, 'haproxy-top version %s' % version)
            s.addstr(8, startx+1, 't - tree')
            s.addstr(9, startx+1, 's - select sort field')
            s.addstr(9, startx+1, 'r - reverse sort order')
            s.addstr(10, startx+1, 'f - filter by container name')
            s.addstr(11, startx+5, '(e.g. source:localhost)')
            s.addstr(12, startx+1, 'h - show this help dialog')
            s.addstr(13, startx+1, 'q - quit')

            rectangle(s, 7,startx, 14,(startx+48))
            s.refresh()
            s.nodelay(0)
            s.getch()
            s.nodelay(1)
            
        if x == ord('t'):
            self.tree = not self.tree

        if x == ord('r'):
            self.sort['reversed'] = not self.sort['reversed']

        if x == ord('s'):
            startx = w / 2 - 20 # I have no idea why this offset of 20 is needed

            opts = [ i[0] for i in views[self.active_view] if i[3] ]
            selected = run_menu(tuple(opts), x=int(startx), y=6, name="sort")
            self.sort['func'] = views[self.active_view][selected][3]

        if x == ord('f'):
            startx = w / 2 - 20 # I have no idea why this offset of 20 is needed

            s.addstr(6, startx, 'String to filter for:')

            editwin = curses.newwin(1,30, 12,(startx+1))
            rectangle(s, 11,startx, 13,(startx+31))
            curses.curs_set(1) #make cursor visible in this box
            s.refresh()

            box = Textbox(editwin)
            box.edit()

            self.filter = str(box.gather()).strip(' ')
            curses.curs_set(0)
            
            #check if valid filter
            if not self._validate_filter():
                self.filter = None
                s.clear()
                s.addstr(6, startx+5, 'Invalid filter')
                s.refresh()
                curses.napms(800)


    def _sorter(self,d):
        return d[self.sort['key']]

    def _validate_filter(self):
        if not self.filter:
            return True

        if ':' not in self.filter:
            return False

        ftype,fvalue = self.filter.split(':')
        if ftype not in self.valid_filters:
            return False

        return True

def main():
    parser = ArgumentParser(description='haproxy-top v%s' % version)
    parser.add_argument('endpoints', nargs='*', action='append')
    args = parser.parse_args()

    endpoints = args.endpoints[0]
    if len(endpoints) == 0:
        print('no haproxy stat endpoints provided')

    HAProxyTop(endpoints)

if __name__ == '__main__':
    main()
