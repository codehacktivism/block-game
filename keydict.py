class KeyDict:
    def __init__(self):
        self.keys = {}
    
    def press_key(self, key):
        self.keys[key] = 1
        
    def release_key(self, key):
        self.keys[key] = 0
        
    def clear(self):
        self.keys = {}
        
    def poll_key(self, key):
        res = self.keys.setdefault(key, 0)
        if res > 0:
            self.keys[key] += 1
        return res
            
    def poll_key_once(self, key):
        res = self.keys.setdefault(key, 0)
        self.keys[key] = 0
        return res
