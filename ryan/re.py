class RE:
    def __init__(self):
        """docstring for __init__"""
        pass

    def __or__(self, obj):
        'save value as _ and return value'
        self.obj = obj
        # for func in dir(obj): setattr(self, func, getattr(obj, func)) # resolved through __getattr__
        return obj

    # def __coerce__(self, other): # will be called before __or__, and if not defined will goes to __getattr__
    #     """docstring for __coerce__"""
    #     print("other=", other)
    #     return None

    def __getitem__(self, key):
        if re.match("\d+", str(key)): # digital group
            return self.obj.group(int(key))
        else: # named group
            dict = self.obj.groupdict()
            if key in dict :
                return dict[key]
            else:
                return getattr(self.obj, key)

    def __getattr__(self, attr):
        """docstring for __getattr__"""

        if attr=="__coerce__" : raise AttributeError

        if attr[0]=="_" :
            grp = attr[1:]
            if re.match("\d+", grp): # digital group
                return self.obj.group(int(grp))
            else: # named group
                dict = self.obj.groupdict()
                if grp in dict :
                    return dict[grp]
                else:
                    return getattr(self.obj, attr)
        else :
            return getattr(self.obj, attr)
            #raise AttributeError

