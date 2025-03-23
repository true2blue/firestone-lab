import sys
import os
import runpy

# Check if running in a PyInstaller bundle
if hasattr(sys, '_MEIPASS'):
    # Add the bundled 'src' directory to sys.path
    base_dir = sys._MEIPASS
else:
    # Add the local 'src' directory to sys.path (for development/testing)
    base_dir = os.path.abspath(os.path.dirname(__file__))

# Add the 'src' directory to sys.path
sys.path.insert(0, os.path.join(base_dir, 'src'))

# Run the app module as part of the src.lab package
runpy.run_module('src.lab.app', run_name='__main__')