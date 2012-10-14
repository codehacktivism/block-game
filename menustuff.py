
class Menu:
    def __init__(self, title, *options):
        self.title = title
        self.options = [t[0] for t in options]
        self.actions = [t[1] for t in options]
        self.selection = 0
    
    def select(self, drc):
        self.selection += drc
        self.selection %= len(self.options)
        
    def execute(self):
        self.actions[self.selection]()
