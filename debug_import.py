import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
print(f"Path: {sys.path[0]}")
try:
    import exo_inventory
    print(f"Success! File: {exo_inventory.__file__}")
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
