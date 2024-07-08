import argparse
import tkinter
import typing
from collections import namedtuple

from miros import ActiveObject
from miros import return_status
from miros import Event
from miros import signals
from miros import spy_on

MoveEventPayload = namedtuple('MoveEventPayload', ['direction', 'speedup'])

import screenuler.helpers as helpers

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

    def move(self, x, y, speedup: int = 0):
        pass

    def update_position_markers(self, pos, direction='horizontal'):
        pass

    def send_event(self, signal: signals, payload: typing.Any = None):
        self.bus.statechart.post_fifo(Event(signal=signal, payload=payload))


class Gui(TestableGui):
    sizes = {
        1: (250, 75),
        2: (500, 75),
        3: (750, 75)
    }

    default_size = 1

    def __init__(self, bus: GlobalBus, background='red', mark_color='black', position_color='white'):
        super().__init__(bus=bus)

        self.background = background
        self.mark_color = mark_color
        self.position_color = position_color

        self.canvas_figures = []
        self.position_marker = None
        self.position_text = None

        self.root = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.root, background=self.background)
        self.external_position_marker = tkinter.Toplevel(background=self.position_color)

        self.root.title('screenuler 🤡')
        self.root.resizable(False, False)
        self._set_geometry(0, 0, 50, 50)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.canvas.grid(column=0, row=0, sticky='nesw')

        self.external_position_marker.overrideredirect(True)
        self.external_position_marker.geometry('0x0+0+0')

    def bind_events(self):
        self.root.bind('<Control-q>', lambda _: self.send_event(signal=signals.SHUTDOWN))
        self.root.bind('<Escape>', lambda _: self.send_event(signal=signals.SHUTDOWN))

        self.root.bind('<Control-KeyRelease-t>', lambda _: self.send_event(signal=signals.TOGGLE_ORIENTATION))
        self.root.bind('<Control-s>', lambda _: self.send_event(signal=signals.SET_SIZE_1))
        self.root.bind('<Control-m>', lambda _: self.send_event(signal=signals.SET_SIZE_2))
        self.root.bind('<Control-l>', lambda _: self.send_event(signal=signals.SET_SIZE_3))

        self.root.bind('<Left>', lambda e: self.send_event(signal=signals.MOVE, payload=MoveEventPayload(direction=(-1, 0), speedup=helpers.is_speedup_modifier_active(e.state))))

        self.root.bind('<Right>', lambda e: self.send_event(signal=signals.MOVE, payload=MoveEventPayload(direction=(1, 0), speedup=helpers.is_speedup_modifier_active(e.state))))

        self.root.bind('<Up>', lambda e: self.send_event(signal=signals.MOVE, payload=MoveEventPayload(direction=(0, -1), speedup=helpers.is_speedup_modifier_active(e.state))))

        self.root.bind('<Down>', lambda e: self.send_event(signal=signals.MOVE, payload=MoveEventPayload(direction=(0, 1), speedup=helpers.is_speedup_modifier_active(e.state))))

        self.root.bind('<Motion>', lambda e: self.send_event(signal=signals.POINTER_MOVED, payload=(e.x, e.y)))

        self.root.bind('<Enter>', lambda e: self.send_event(signal=signals.SHOW_EXTERNAL_MARKER))

        self.root.bind('<Leave>', lambda e: self.send_event(signal=signals.HIDE_EXTERNAL_MARKER))

    def run(self):
        self.bind_events()
        self.root.mainloop()

    def quit(self):
        self.root.quit()

    def _set_geometry(self, width: int, height: int, x: int, y: int):
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _clear_canvas_figures(self):
        while self.canvas_figures:
            self.canvas.delete(self.canvas_figures.pop())

    def _draw_mark(self, pos, direction='horizontal'):
        if direction == 'horizontal':
            fig = self.canvas.create_rectangle(pos, 0, pos, 25, fill=self.mark_color, outline=self.mark_color)
            self.canvas_figures.append(fig)
            if pos % 50 == 0:
                fig = self.canvas.create_text(pos, 40, justify='center', text=pos, angle=90.0, fill=self.mark_color)
                self.canvas_figures.append(fig)
        elif direction == 'vertical':
            fig = self.canvas.create_rectangle(50, pos, 75, pos, fill=self.mark_color, outline=self.mark_color)
            self.canvas_figures.append(fig)
            if pos % 50 == 0:
                fig = self.canvas.create_text(25, pos, justify='center', text=pos, fill=self.mark_color)
                self.canvas_figures.append(fig)

    def update_position_markers(self, pos, direction='horizontal'):
        if self.position_marker:
            self.canvas.delete(self.position_marker)
            self.position_marker = None

        if self.position_text:
            self.canvas.delete(self.position_text)
            self.position_text = None

        if direction == 'horizontal':
            self.position_marker = self.canvas.create_rectangle(pos, 0, pos, 50, fill=self.position_color, outline=self.position_color)
            self.position_text = self.canvas.create_text(15, 50, text=pos, justify='center', fill=self.position_color)

            x, y = helpers.get_position(self.root.geometry())
            self.external_position_marker.geometry(f'+{self.root.winfo_pointerx()}+{y-25}')
        elif direction == 'vertical':
            self.position_marker = self.canvas.create_rectangle(25, pos, 75, pos, fill=self.position_color, outline=self.position_color)
            self.position_text = self.canvas.create_text(15, 25, text=pos, justify='center', fill=self.position_color)

            x, y = helpers.get_position(self.root.geometry())
            self.external_position_marker.geometry(f'+{x+75}+{self.root.winfo_pointery()}')

    def show_external_marker(self):
        self.external_position_marker.state('normal')

    def hide_external_marker(self):
        self.external_position_marker.state('withdrawn')

    def make_horizontal(self, size: int = 1):
        geometry = self.root.geometry()
        x, y = helpers.get_position(geometry)
        width, height = Gui.sizes.get(size, Gui.sizes.get(Gui.default_size))
        self._set_geometry(width, height, x, y)

        self._clear_canvas_figures()

        for pos in range(0, width + 50, 10):
            self._draw_mark(pos)

        self.external_position_marker.geometry('1x50+50+50')

    def make_vertical(self, size: int = 1):
        geometry = self.root.geometry()
        x, y = helpers.get_position(geometry)
        height, width = Gui.sizes.get(size, Gui.sizes.get(Gui.default_size))
        self._set_geometry(width, height, x, y)

        self._clear_canvas_figures()

        for pos in range(0, height + 50, 10):
            self._draw_mark(pos, direction='vertical')

        self.external_position_marker.geometry('50x1+50+50')

    def move(self, x, y, speedup: int = 0):
        geometry = self.root.geometry()
        _x, _y = helpers.get_position(geometry)
        width, height = helpers.get_size(geometry)

        new_x = max(0, _x + x * speedup)
        new_y = max(0, _y + y * speedup)

        self._set_geometry(width, height, new_x, new_y)


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
        c.bus.gui.update_position_markers(e.payload[0])
        status = return_status.HANDLED
    elif e.signal == signals.SHOW_EXTERNAL_MARKER:
        c.bus.gui.show_external_marker()
        status = return_status.HANDLED
    elif e.signal == signals.HIDE_EXTERNAL_MARKER:
        c.bus.gui.hide_external_marker()
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
        c.bus.gui.update_position_markers(e.payload[1], direction='vertical')
        status = return_status.HANDLED
    elif e.signal == signals.SHOW_EXTERNAL_MARKER:
        c.bus.gui.show_external_marker()
        status = return_status.HANDLED
    elif e.signal == signals.HIDE_EXTERNAL_MARKER:
        c.bus.gui.hide_external_marker()
        status = return_status.HANDLED
    else:
        status = return_status.SUPER
        c.temp.fun = init_state

    return status


def run(args):
    b = GlobalBus()
    s = Statechart('statechart', bus=b)
    g = Gui(bus=b, background=args.background, mark_color=args.mark_color, position_color=args.position_color)

    s.start_at(init_state)

    g.run()

def make_arguments_and_run():
    parser = argparse.ArgumentParser(prog='screenuler', description='Simple Python Tkinter screen ruler')
    parser.add_argument('-b', '--background', type=str, default='red', help='color name (red) or hexcode (#f00)')
    parser.add_argument('-m', '--mark_color', type=str, default='black', help='color name (red) or hexcode (#f00)')
    parser.add_argument('-p', '--position_color', type=str, default='white', help='color name (red) or hexcode (#f00)')
    args = parser.parse_args()

    run(args)

if __name__ == '__main__':
    make_arguments_and_run()