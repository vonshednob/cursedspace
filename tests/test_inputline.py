import unittest
import curses

from cursedspace import InputLine


class FakeApp:
    def __init__(self):
        self.screen = FakeWin()


class FakeWin:
    def addstr(self, *args, **kwargs):
        pass

    def move(self, *args, **kwargs):
        pass

    def noutrefresh(self):
        pass

    def clear(self):
        pass

    def mvwin(self, *args, **kwargs):
        pass

    def touchwin(self):
        pass


def newwin(*args, **kwargs):
    return FakeWin()


def nothing():
    pass


curses.newwin = newwin


class TestCurrentWord(unittest.TestCase):
    def setUp(self):
        self.inputline = InputLine(FakeApp(), 20, (0, 0))
        self.inputline.win = FakeWin()
        self.inputline.paint = nothing

    def test_empty_case(self):
        self.inputline.text = ''
        self.inputline.scroll()

        self.assertIsNone(self.inputline.current_word())

    def test_no_word(self):
        self.inputline.text = 'there is  space'
        self.inputline.cursor = 9

        span = self.inputline.current_word()

        self.assertIsNone(span)

    def test_basic_case1(self):
        self.inputline.text = 'this is a test'
        self.inputline.cursor = 5

        span = self.inputline.current_word()

        self.assertEqual(span, (5, 7))

    def test_basic_case2(self):
        self.inputline.text = 'a word'
        self.inputline.cursor = 6

        span = self.inputline.current_word()

        self.assertEqual(span, (2, 6))

    def test_ws_end(self):
        self.inputline.text = 'there be blanks '
        self.inputline.cursor = 16

        span = self.inputline.current_word()

        self.assertIsNone(span)

    def test_ws_start(self):
        self.inputline.text = ' there be blanks'
        self.inputline.cursor = 0

        span = self.inputline.current_word()

        self.assertIsNone(span)

    def test_cursor_after_word(self):
        self.inputline.text = 'this is a test'
        self.inputline.cursor = 7

        span = self.inputline.current_word()

        self.assertEqual(span, (5, 7))


class TestReplaceWord(unittest.TestCase):
    def setUp(self):
        self.inputline = InputLine(FakeApp(), 20, (0, 0))
        self.inputline.win = FakeWin()
        self.inputline.paint = nothing

    def test_empty_case(self):
        self.inputline.text = ''
        self.inputline.scroll()

        self.inputline.replace_word('hello')

        self.assertEqual(self.inputline.text, 'hello')

    def test_insert_case(self):
        self.inputline.text = 'there is  space'
        self.inputline.cursor = 9

        self.inputline.replace_word('enough')

        self.assertEqual(self.inputline.text, 'there is enough space')

    def test_basic_case1(self):
        self.inputline.text = 'this is a test'
        self.inputline.cursor = 5

        self.inputline.replace_word('was')

        self.assertEqual(self.inputline.text, 'this was a test')

    def test_basic_case2(self):
        self.inputline.text = 'this is a test'
        self.inputline.cursor = 6

        self.inputline.replace_word('was')

        self.assertEqual(self.inputline.text, 'this was a test')

    def test_insert1(self):
        self.inputline.text = 'another test'
        self.inputline.cursor = 7
        
        self.inputline.replace_word('funky')

        self.assertEqual(self.inputline.text, 'funky test')

    def test_last_word(self):
        self.inputline.text = 'one more test'
        self.inputline.cursor = 10

        self.inputline.replace_word('forkup')

        self.assertEqual(self.inputline.text, 'one more forkup')

    def test_first_word(self):
        self.inputline.text = 'test this scenario'
        self.inputline.cursor = 2

        self.inputline.replace_word('fudge')

        self.assertEqual(self.inputline.text, 'fudge this scenario')

