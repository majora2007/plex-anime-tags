class AniDBTag():
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight  
    
    def __repr__(self):
        return '{} ({})'.format(self.name, self.weight)
    
    def toJSON(self):
        return {'name': self.name, 'weight': self.weight}