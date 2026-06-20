import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Frontend import colorize_formula

print(repr(colorize_formula("P(x, y) + z", mode="ansi")))
