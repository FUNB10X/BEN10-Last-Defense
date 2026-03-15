"""
Ben 10 Last Defense — root entry point.
Run: python main.py
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from ben10_defense.main import main

if __name__ == '__main__':
    main()
