class Item:
    def __init__(self, data):
        self.data = data

    def __getattr__(self, item):
        return self.data[item]
