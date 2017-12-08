import argparse
import logging
import subprocess
import threading
import tkinter as tk

LOG = logging.getLogger(__name__)


def coalesce(*values):
    return next(
        (value for value in values if value is not None),
        None)


class TimerCanvas(tk.Canvas):
    def __init__(self, parent, seconds=None, **kwargs):
        super().__init__(parent, background='white', **kwargs)

        self.seconds = int(seconds)
        self.current = self.seconds

        self.angle = 0
        self.bind('<Configure>', self.resize)
        self.draw_circle()

    def update(self, seconds=None):
        if seconds is None:
            seconds = self.current

        self.current = seconds

        r = float(seconds)/self.seconds
        angle = 360 - (360 * r)

        x = self.winfo_width()
        y = self.winfo_height()
        size = min(x, y)

        self.delete('arc')

        if angle == 360:
            self.create_oval(0, 0, size, size,
                             tag='arc', fill='white')
        else:
            self.create_arc(0, 0, size, size,
                            tag='arc', fill='white',
                            start=90, extent=-angle)

    def draw_circle(self):
        x = self.winfo_width()
        y = self.winfo_height()
        r = min(x, y)
        self.create_oval(0, 0, r, r, tag='circle', fill='red')
        self.update()

    def resize(self, event):
        self.delete('circle')
        self.draw_circle()


class TimerApp(tk.Tk):
    default_width = 100
    default_height = 100
    tock_time = 100

    def __init__(self,
                 seconds=None,
                 repeat=None,
                 interval=None,
                 action=None,
                 width=None,
                 height=None,
                 **kwargs):

        self.timer = None
        self.seconds = int(seconds)
        self.current = self.seconds
        self.repeat = int(coalesce(repeat, 0))
        self.interval = int(coalesce(interval, 0))
        self.action = action

        self.quit = False
        self.running = False

        width = coalesce(width, self.default_width)
        height = coalesce(height, self.default_height)

        super().__init__(**kwargs)

        self.geometry('{}x{}'.format(width, height))
        self.protocol('WM_DELETE_WINDOW', self.on_delete)
        self.canvas = TimerCanvas(self, seconds=seconds)
        self.canvas.pack(fill="both", expand=True)

        self.bind('<Button-1>', self.toggle)
        self.bind('<Button-3>', self.reset)

        self.tock()

    def on_delete(self):
        LOG.debug('deleting window')
        self.quit = True
        self.destroy()

    def start_timer(self):
        LOG.info('starting timer (%d seconds left)', self.current)
        self.running = True
        self.tick()

    def stop_timer(self):
        LOG.info('stopping timer (%d seconds left)', self.current)
        if self.timer:
            self.timer.cancel()
        self.running = False

    def toggle(self, event):
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()

    def run_action(self):
        if self.action is None:
            return

        LOG.info('running action: %s', self.action)
        ret = subprocess.call(self.action, shell=True)
        LOG.debug('action returned %d', ret)

    def tick(self):
        LOG.debug('tick %d', self.current)
        if (not self.running) or self.quit:
            return

        try:
            self.canvas.update(self.current)
        except RuntimeError:
            LOG.debug('tick called after window was destroyed')
            return

        if self.current == 0:
            self.stop_timer()
            self.run_action()

            if self.repeat > 0:
                self.repeat -= 1

            if self.repeat > 0 or self.repeat == 1:
                self.reset()
                self.start_timer()
        else:
            self.current -= 1
            self.timer = threading.Timer(1, self.tick)
            self.timer.start()

    def reset(self, event=None):
        LOG.info('reset timer to %d seconds', self.seconds)
        self.current = self.seconds
        self.canvas.update(self.current)

    def tock(self):
        '''Force an event check once in a while.

        If the timer window isn't active, the application may not
        respond to a ^C because it won't be check for events.  This
        forces a check every 50ms.

        See https://stackoverflow.com/a/13784297/147356
        '''

        self.after(self.tock_time, self.tock)


def int_or_inf(value):
    if value.isdigit() and int(value) >= 0:
        return int(value)
    elif value == 'inf':
        return -1
    else:
        raise ValueError('--repeat must be a positive integer or "inf"')


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--seconds', '-s', default=10, type=int)
    p.add_argument('--interval', '-i', default=0, type=int)
    p.add_argument('--repeat', '-r', default=0, type=int_or_inf)
    p.add_argument('--action', '-a')
    p.add_argument('--width', '-W', type=int)
    p.add_argument('--height', '-H', type=int)

    g = p.add_argument_group('Logging options')
    g.add_argument('--verbose', dest='loglevel', action='store_const',
                   const='INFO')
    g.add_argument('--debug', dest='loglevel', action='store_const',
                   const='DEBUG')

    p.set_defaults(loglevel='WARNING')

    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=args.loglevel)

    root = TimerApp(width=args.width, height=args.height,
                    seconds=args.seconds,
                    repeat=args.repeat,
                    interval=args.interval,
                    action=args.action)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.on_delete()

if __name__ == "__main__":
    main()
