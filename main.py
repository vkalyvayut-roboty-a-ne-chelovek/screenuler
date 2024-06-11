import sys
import time
import tkinter

from miros import ActiveObject
from miros import return_status
from miros import Event
from miros import signals
from miros import spy_on

import helpers
from collections import namedtuple

MoveEventPayload = namedtuple('MoveEventPayload', ['direction', 'speedup'])

class GlobalBus:
    def __init__(self):
        self.gui = None
        self.statechart = None

    def register_gui(self, gui):
        self.gui = gui

    def register_statechart(self, statechart):
        self.statechart = statechart


class Statechart(ActiveObject):
    def __init__(self, name: str, bus: GlobalBus):
        super().__init__(name=name)
        self.bus = bus
        self.bus.register_statechart(self)


class TestableGui:
    def __init__(self, bus: GlobalBus):
        self.bus = bus
        self.bus.register_gui(self)

    def run(self):
        pass

    def quit(self):
        pass

    def make_horizontal(self, size: int = 1):
        pass

    def make_vertical(self, size: int = 1):
        pass

    def move(self, x, y, speedup: bool = False):
        pass

    def update_pointer_info_horizontal(self, x, y):
        pass

    def update_pointer_info_vertical(self, x, y):
        pass


class Gui(TestableGui):
    sizes = {
        1: (250, 75),
        2: (500, 75),
        3: (750, 75)
    }

    default_size = 1

    def __init__(self, bus: GlobalBus):
        self.bus = bus
        self.bus.register_gui(self)

        self.root = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.root, background='red')
        self.canvas_figures = []
        self.position_marker = None
        self.position_text = None

        self.root.title('screenuler 🤡')
        self.root.resizable(False, False)
        self.root.geometry('0x0+0+0')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.canvas.grid(column=0, row=0, sticky='nesw')

    def bind_events(self):
        self.root.bind('<Control-q>', lambda _: self.bus.statechart.post_fifo(Event(signal=signals.SHUTDOWN)))
        self.root.bind('<Escape>', lambda _: self.bus.statechart.post_fifo(Event(signal=signals.SHUTDOWN)))

        self.root.bind('<Control-KeyRelease-t>', lambda _: self.bus.statechart.post_fifo(Event(signal=signals.TOGGLE_ORIENTATION)))
        self.root.bind('<Control-s>', lambda _: self.bus.statechart.post_fifo(Event(signal=signals.SET_SIZE_1)))
        self.root.bind('<Control-m>', lambda _: self.bus.statechart.post_fifo(Event(signal=signals.SET_SIZE_2)))
        self.root.bind('<Control-l>', lambda _: self.bus.statechart.post_fifo(Event(signal=signals.SET_SIZE_3)))

        self.root.bind('<Left>', lambda e: self.bus.statechart.post_fifo(
            Event(
                signal=signals.MOVE,
                payload=MoveEventPayload(
                    direction=(-10, 0),
                    speedup=helpers.is_speedup_modifier_active(e.state)))))

        self.root.bind('<Right>', lambda e: self.bus.statechart.post_fifo(
            Event(
                signal=signals.MOVE,
                payload=MoveEventPayload(
                    direction=(10, 0),
                    speedup=helpers.is_speedup_modifier_active(e.state)))))

        self.root.bind('<Up>', lambda e: self.bus.statechart.post_fifo(
            Event(
                signal=signals.MOVE,
                payload=MoveEventPayload(
                    direction=(0, -10),
                    speedup=helpers.is_speedup_modifier_active(e.state)))))

        self.root.bind('<Down>', lambda e: self.bus.statechart.post_fifo(
            Event(
                signal=signals.MOVE,
                payload=MoveEventPayload(
                    direction=(0, 10),
                    speedup=helpers.is_speedup_modifier_active(e.state)))))

        self.root.bind('<Motion>', lambda e: self.bus.statechart.post_fifo(
            Event(signal=signals.POINTER_MOVED, payload=(e.x, e.y))))

    def run(self):
        self.bind_events()
        self.root.mainloop()

    def quit(self):
        self.root.quit()

    def make_horizontal(self, size: int = 1):
        geometry = self.root.geometry()
        x, y = helpers.get_position(geometry)
        width, height = Gui.sizes.get(size, Gui.sizes.get(Gui.default_size))
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        while self.canvas_figures:
            self.canvas.delete(self.canvas_figures.pop())

        for pos in range(0, width + 50, 10):
            fig = self.canvas.create_rectangle(pos, 0, pos, 25)
            self.canvas_figures.append(fig)
            if pos % 50 == 0:
                fig = self.canvas.create_text(pos, 40, justify='center', text=pos, angle=90.0)
                self.canvas_figures.append(fig)

    def make_vertical(self, size: int = 1):
        geometry = self.root.geometry()
        x, y = helpers.get_position(geometry)
        height, width = Gui.sizes.get(size, Gui.sizes.get(Gui.default_size))
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        while self.canvas_figures:
            self.canvas.delete(self.canvas_figures.pop())

        for pos in range(0, height + 50, 10):
            fig = self.canvas.create_rectangle(50, pos, 75, pos)
            self.canvas_figures.append(fig)
            if pos % 50 == 0:
                fig = self.canvas.create_text(25, pos, justify='center', text=pos)
                self.canvas_figures.append(fig)

    def move(self, x, y, speedup: bool = False):
        geometry = self.root.geometry()
        _x, _y = helpers.get_position(geometry)
        speedup_factor = 5 if speedup else 1
        self.root.geometry(f'+{_x + x * speedup_factor}+{_y + y * speedup_factor}')

    def update_pointer_info_horizontal(self, x, y):
        if self.position_marker:
            self.canvas.delete(self.position_marker)
            self.position_marker = None

        if self.position_text:
            self.canvas.delete(self.position_text)
            self.position_text = None

        self.position_marker = self.canvas.create_rectangle(x, 0, x, 50, fill='black')
        self.position_text = self.canvas.create_text(15, 50, text=x, justify='center', fill='white')

    def update_pointer_info_vertical(self, x, y):
        if self.position_marker:
            self.canvas.delete(self.position_marker)
            self.position_marker = None

        if self.position_text:
            self.canvas.delete(self.position_text)
            self.position_text = None

        self.position_marker = self.canvas.create_rectangle(25, y, 75, y, fill='black')
        self.position_text = self.canvas.create_text(15, 25, text=y, justify='center', fill='white')


@spy_on
def init_state(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.INIT_SIGNAL:
        status = c.trans(horizontal_state)
    elif e.signal == signals.MOVE:
        c.bus.gui.move(e.payload.direction[0], e.payload.direction[1], e.payload.speedup)
        status = return_status.HANDLED
    elif e.signal == signals.SHUTDOWN:
        status = return_status.HANDLED
        c.bus.gui.quit()
    else:
        status = return_status.SUPER
        c.temp.fun = c.top

    return status


@spy_on
def horizontal_state(c: Statechart, e: Event) -> return_status:
    status = return_status.UNHANDLED

    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.INIT_SIGNAL:
        c.bus.gui.make_horizontal()
        status = return_status.HANDLED
    elif e.signal == signals.TOGGLE_ORIENTATION:
        status = c.trans(vertical_state)
    elif e.signal == signals.SET_SIZE_1:
        c.bus.gui.make_horizontal(1)
        status = return_status.HANDLED
    elif e.signal == signals.SET_SIZE_2:
        c.bus.gui.make_horizontal(2)
        status = return_status.HANDLED
    elif e.signal == signals.SET_SIZE_3:
        c.bus.gui.make_horizontal(3)
        status = return_status.HANDLED
    elif e.signal == signals.POINTER_MOVED:
        c.bus.gui.update_pointer_info_horizontal(e.payload[0], e.payload[1])
        status = return_status.HANDLED
    else:
        status = return_status.SUPER
        c.temp.fun = init_state

    return status


@spy_on
def vertical_state(c: Statechart, e: Event) -> return_status:
    if e.signal == signals.ENTRY_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.EXIT_SIGNAL:
        status = return_status.HANDLED
    elif e.signal == signals.INIT_SIGNAL:
        c.bus.gui.make_vertical()
        status = return_status.HANDLED
    elif e.signal == signals.TOGGLE_ORIENTATION:
        status = c.trans(horizontal_state)
    elif e.signal == signals.SET_SIZE_1:
        c.bus.gui.make_vertical(1)
        status = return_status.HANDLED
    elif e.signal == signals.SET_SIZE_2:
        c.bus.gui.make_vertical(2)
        status = return_status.HANDLED
    elif e.signal == signals.SET_SIZE_3:
        c.bus.gui.make_vertical(3)
        status = return_status.HANDLED
    elif e.signal == signals.POINTER_MOVED:
        c.bus.gui.update_pointer_info_vertical(e.payload[0], e.payload[1])
        status = return_status.HANDLED
    else:
        status = return_status.SUPER
        c.temp.fun = init_state

    return status


if __name__ == '__main__':
    b = GlobalBus()
    s = Statechart('statechart', bus=b)
    g = Gui(bus=b)

    s.live_spy = True
    s.live_trace = True
    s.start_at(init_state)

    g.run()

