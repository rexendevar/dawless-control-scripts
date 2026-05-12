import curses
from curses import wrapper

def main(stdscr):
    # Clear screen
    stdscr.clear()

    begin_x = 20; begin_y = 7
    height = 5; width = 40
    win = curses.newwin(1, curses.COLS, curses.LINES-1, 0)

    current = -1
    key = "KEY_RIGHT"
    i = 0

    while True:
        i +=1
        if key == "KEY_RIGHT":
            current += 1
        elif key == "KEY_LEFT":
            current -= 1
        else:
            stdscr.addstr(key)

        #current = current % 10
        v = current-10
        stdscr.addstr(0, 0, '10 divided by {} is {}'.format(v, 10/v))
        win.addstr(0,0," ")
        for n in range(10):
            if current == n:
                attr = curses.A_BOLD
            else:
                attr = curses.A_DIM
            win.addstr(str(n)+" ", attr)

        stdscr.refresh()
        win.refresh()
        key = str(stdscr.getkey())


wrapper(main)