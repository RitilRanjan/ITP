import sys, os
sys.path.append(os.path.abspath("."))
import pickle
import uuid

class SwapRef:
    def __init__(self, obj):
        self.filename = f"scratch/swap_{uuid.uuid4().hex}.pkl"
        with open(self.filename, "wb") as f:
            pickle.dump(obj, f)
            
    def load(self):
        with open(self.filename, "rb") as f:
            obj = pickle.load(f)
        os.remove(self.filename)
        return obj

data = {"test": 123}
ref = SwapRef(data)
print("Loaded:", ref.load())
