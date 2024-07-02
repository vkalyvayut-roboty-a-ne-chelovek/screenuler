from screenuler import run
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='screenuler', description='Simple Python Tkinter screen ruler')
    parser.add_argument('-b', '--background', type=str, default='red', help='color name (red) or hexcode (#f00)')
    parser.add_argument('-m', '--mark_color', type=str, default='black', help='color name (red) or hexcode (#f00)')
    parser.add_argument('-p', '--position_color', type=str, default='white', help='color name (red) or hexcode (#f00)')
    args = parser.parse_args()

    run(args)