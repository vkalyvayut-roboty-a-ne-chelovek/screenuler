import time
import unittest

from screenuler.app import Statechart
from screenuler.app import GlobalBus
from screenuler.app import TestableGui
from screenuler.app import init_state
from screenuler.app import MoveEventPayload

from miros import stripped
from miros import Event
from miros import signals


class TestStates(unittest.TestCase):
    def setUp(self):
        bus = GlobalBus()
        self.statechart = Statechart('statechart', bus=bus)
        gui = TestableGui(bus=bus)

        self.statechart.start_at(init_state)

    @staticmethod
    def assert_traces(expected_trace, actual_trace):
        with stripped(expected_trace) as expected, stripped(actual_trace) as actual:
            assert len(expected) == len(actual)
            for e, a in zip(expected, actual):
                assert e == a, f'{e} != {a}'

    @staticmethod
    def assert_spies(expected_spy, actual_spy):
        assert len(expected_spy) == len(actual_spy)
        for e, a in zip(expected_spy, actual_spy):
            assert e == a, f'{e} != {a}'

    def test_statechart_horizontal_orientation_default_state(self):
        expected_trace = '''
        [2024-06-11 17:26:25.306161] [statechart] e->start_at() top->horizontal_state
        '''

        actual_trace = self.statechart.trace()

        self.assert_traces(expected_trace, actual_trace)

    def test_statechart_horizontal_orientation_changes_to_vertical_states_after_toggle_orientation_signal(self):
        expected_trace = '''
        [2024-06-11 17:31:55.800968] [statechart] e->start_at() top->horizontal_state
        [2024-06-11 17:31:55.801652] [statechart] e->TOGGLE_ORIENTATION() horizontal_state->vertical_state
        '''

        self.statechart.post_fifo(Event(signal=signals.TOGGLE_ORIENTATION))
        time.sleep(0.1)

        actual_trace = self.statechart.trace()

        self.assert_traces(expected_trace, actual_trace)

    def test_statechart_vertical_orientation_changes_back_to_horizontal_states_after_toggle_orientation_signal(self):
        expected_trace = '''
        [2024-06-11 17:34:45.862758] [statechart] e->start_at() top->horizontal_state
        [2024-06-11 17:34:45.863227] [statechart] e->TOGGLE_ORIENTATION() horizontal_state->vertical_state
        [2024-06-11 17:34:45.863306] [statechart] e->TOGGLE_ORIENTATION() vertical_state->horizontal_state
        '''

        self.statechart.post_fifo(Event(signal=signals.TOGGLE_ORIENTATION))
        self.statechart.post_fifo(Event(signal=signals.TOGGLE_ORIENTATION))
        time.sleep(0.1)

        actual_trace = self.statechart.trace()

        self.assert_traces(expected_trace, actual_trace)

    def test_statechart_change_size_signals_in_horizontal_state(self):
        self.statechart.post_fifo(Event(signal=signals.SET_SIZE_1))
        self.statechart.post_fifo(Event(signal=signals.SET_SIZE_2))
        self.statechart.post_fifo(Event(signal=signals.SET_SIZE_3))

        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init_state', 'ENTRY_SIGNAL:init_state', 'INIT_SIGNAL:init_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:horizontal_state', 'INIT_SIGNAL:horizontal_state', '<- Queued:(0) Deferred:(0)', 'SET_SIZE_1:horizontal_state', 'SET_SIZE_1:horizontal_state:HOOK', '<- Queued:(2) Deferred:(0)', 'SET_SIZE_2:horizontal_state', 'SET_SIZE_2:horizontal_state:HOOK', '<- Queued:(1) Deferred:(0)', 'SET_SIZE_3:horizontal_state', 'SET_SIZE_3:horizontal_state:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        self.assert_spies(expected_spy, actual_spy)

    def test_statechart_change_size_signals_in_vertical_state(self):
        self.statechart.post_fifo(Event(signal=signals.TOGGLE_ORIENTATION))
        self.statechart.post_fifo(Event(signal=signals.SET_SIZE_1))
        self.statechart.post_fifo(Event(signal=signals.SET_SIZE_2))
        self.statechart.post_fifo(Event(signal=signals.SET_SIZE_3))

        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init_state', 'ENTRY_SIGNAL:init_state', 'INIT_SIGNAL:init_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:horizontal_state', 'INIT_SIGNAL:horizontal_state', '<- Queued:(0) Deferred:(0)', 'TOGGLE_ORIENTATION:horizontal_state', 'SEARCH_FOR_SUPER_SIGNAL:vertical_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'EXIT_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:vertical_state', 'INIT_SIGNAL:vertical_state', '<- Queued:(3) Deferred:(0)', 'SET_SIZE_1:vertical_state', 'SET_SIZE_1:vertical_state:HOOK', '<- Queued:(2) Deferred:(0)', 'SET_SIZE_2:vertical_state', 'SET_SIZE_2:vertical_state:HOOK', '<- Queued:(1) Deferred:(0)', 'SET_SIZE_3:vertical_state', 'SET_SIZE_3:vertical_state:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        expected_trace = '''
        [2024-06-11 18:41:03.572177] [statechart] e->start_at() top->horizontal_state
        [2024-06-11 18:41:03.572656] [statechart] e->TOGGLE_ORIENTATION() horizontal_state->vertical_state
        '''
        actual_trace = self.statechart.trace()

        self.assert_spies(expected_spy, actual_spy)
        self.assert_traces(expected_trace, actual_trace)

    def test_statechart_2_move_signals_in_horizontal_state(self):
        self.statechart.post_fifo(Event(signal=signals.MOVE, payload=MoveEventPayload(direction=(0, 0), speedup=False)))
        self.statechart.post_fifo(Event(signal=signals.MOVE, payload=MoveEventPayload(direction=(0, 0), speedup=False)))

        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init_state', 'ENTRY_SIGNAL:init_state', 'INIT_SIGNAL:init_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:horizontal_state', 'INIT_SIGNAL:horizontal_state', '<- Queued:(0) Deferred:(0)', 'MOVE:horizontal_state', 'MOVE:init_state', 'MOVE:init_state:HOOK', '<- Queued:(1) Deferred:(0)', 'MOVE:horizontal_state', 'MOVE:init_state', 'MOVE:init_state:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        self.assert_spies(expected_spy, actual_spy)

    def test_statechart_2_move_signals_in_vertical_state(self):
        self.statechart.post_fifo(Event(signal=signals.TOGGLE_ORIENTATION))
        self.statechart.post_fifo(Event(signal=signals.MOVE, payload=MoveEventPayload(direction=(0, 0), speedup=False)))
        self.statechart.post_fifo(Event(signal=signals.MOVE, payload=MoveEventPayload(direction=(0, 0), speedup=False)))

        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init_state', 'ENTRY_SIGNAL:init_state', 'INIT_SIGNAL:init_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:horizontal_state', 'INIT_SIGNAL:horizontal_state', '<- Queued:(0) Deferred:(0)', 'TOGGLE_ORIENTATION:horizontal_state', 'SEARCH_FOR_SUPER_SIGNAL:vertical_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'EXIT_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:vertical_state', 'INIT_SIGNAL:vertical_state', '<- Queued:(2) Deferred:(0)', 'MOVE:vertical_state', 'MOVE:init_state', 'MOVE:init_state:HOOK', '<- Queued:(1) Deferred:(0)', 'MOVE:vertical_state', 'MOVE:init_state', 'MOVE:init_state:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        self.assert_spies(expected_spy, actual_spy)

    def test_statechart_shutdown_signal_in_horizontal_state(self):
        self.statechart.post_fifo(Event(signal=signals.SHUTDOWN))

        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init_state', 'ENTRY_SIGNAL:init_state', 'INIT_SIGNAL:init_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:horizontal_state', 'INIT_SIGNAL:horizontal_state', '<- Queued:(0) Deferred:(0)', 'SHUTDOWN:horizontal_state', 'SHUTDOWN:init_state', 'SHUTDOWN:init_state:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        expected_trace = '''
        [2024-06-11 18:21:06.089324] [statechart] e->start_at() top->horizontal_state
        '''
        actual_trace = self.statechart.trace()

        self.assert_spies(expected_spy, actual_spy)
        self.assert_traces(expected_trace, actual_trace)

    def test_statechart_shutdown_signal_in_vertical_state(self):
        self.statechart.post_fifo(Event(signal=signals.TOGGLE_ORIENTATION))
        self.statechart.post_fifo(Event(signal=signals.SHUTDOWN))

        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init_state', 'ENTRY_SIGNAL:init_state', 'INIT_SIGNAL:init_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:horizontal_state', 'INIT_SIGNAL:horizontal_state', '<- Queued:(0) Deferred:(0)', 'TOGGLE_ORIENTATION:horizontal_state', 'SEARCH_FOR_SUPER_SIGNAL:vertical_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'EXIT_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:vertical_state', 'INIT_SIGNAL:vertical_state', '<- Queued:(1) Deferred:(0)', 'SHUTDOWN:vertical_state', 'SHUTDOWN:init_state', 'SHUTDOWN:init_state:HOOK', '<- Queued:(0) Deferred:(0)']
        actual_spy = self.statechart.spy()

        expected_trace = '''
        [2024-06-11 18:21:06.089324] [statechart] e->start_at() top->horizontal_state
        [2024-06-11 18:21:06.089793] [statechart] e->TOGGLE_ORIENTATION() horizontal_state->vertical_state
        '''
        actual_trace = self.statechart.trace()

        self.assert_spies(expected_spy, actual_spy)
        self.assert_traces(expected_trace, actual_trace)

    def test_statechart_pointer_moved_signal_in_horizontal_state(self):
        self.statechart.post_fifo(Event(signal=signals.POINTER_MOVED, payload=(0, 0)))

        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init_state', 'ENTRY_SIGNAL:init_state', 'INIT_SIGNAL:init_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:horizontal_state', 'INIT_SIGNAL:horizontal_state', '<- Queued:(0) Deferred:(0)', 'POINTER_MOVED:horizontal_state', 'POINTER_MOVED:horizontal_state:HOOK', '<- Queued:(0) Deferred:(0)']

        actual_spy = self.statechart.spy()

        self.assert_spies(expected_spy, actual_spy)

    def test_statechart_pointer_moved_signal_in_vertical_state(self):
        self.statechart.post_fifo(Event(signal=signals.TOGGLE_ORIENTATION))
        self.statechart.post_fifo(Event(signal=signals.POINTER_MOVED, payload=(0, 0)))

        time.sleep(0.1)

        expected_spy = ['START', 'SEARCH_FOR_SUPER_SIGNAL:init_state', 'ENTRY_SIGNAL:init_state', 'INIT_SIGNAL:init_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:horizontal_state', 'INIT_SIGNAL:horizontal_state', '<- Queued:(0) Deferred:(0)', 'TOGGLE_ORIENTATION:horizontal_state', 'SEARCH_FOR_SUPER_SIGNAL:vertical_state', 'SEARCH_FOR_SUPER_SIGNAL:horizontal_state', 'EXIT_SIGNAL:horizontal_state', 'ENTRY_SIGNAL:vertical_state', 'INIT_SIGNAL:vertical_state', '<- Queued:(1) Deferred:(0)', 'POINTER_MOVED:vertical_state', 'POINTER_MOVED:vertical_state:HOOK', '<- Queued:(0) Deferred:(0)']

        actual_spy = self.statechart.spy()

        self.assert_spies(expected_spy, actual_spy)


if __name__ == '__main__':
    unittest.main()
