
################################################################################
# exception
################################################################################
class RyanException() :
    """docstring for Exception"""
    def __init__(self):
        Exception.__init__(self)

class E (RyanException):
    def __init__(self, text, **args):
        self.text = text
        self.args = args
    def __repr__(self):
        return ("[ERROR] %s = " % self.text) + repr(self.args)
class W (RyanException):
    def __init__(self, text, **args):
        self.text = text
        self.args = args
    def __repr__(self):
        return ("[ERROR] %s = " % self.text) + repr(self.args)

