"""
this module is excel ole wrapper
"""

# __all__ = [ 'tracer', 'trace', 'date', 'RUNTIME' ]

import os
################################################################################
# start application
################################################################################

from win32com.client import *
C = constants
Excel = Dispatch("Excel.Application")
# print C.xlLastCell
print "Excel = '" + repr(Excel) + "'"


################################################################################
# functions
################################################################################

class Book :
    """docstring for Book"""
    obj = None
    format = "xlsx" # "csv"

    def csv (self):
        return self.format == "csv"

    def __init__(self, path, must_exist=0):

        self.path = path
        self.base = os.path.splitext(os.path.basename(path))[0]
        self.name = os.path.basename(path)
        self.Sheets = []
        self.SheetsHash = {}

        if   path.endswith(".xlsx") :
            self.format = "xlsx"
        elif path.endswith(".csv") :
            self.format = "csv"
            import csv
            with open(path, 'rb') as f:
                self.obj = csv.reader(f)
            return
        else:
            self.format = "xlsx"

        # 1st try : get opened
        for book in Excel.Workbooks:
            if self.name == book.Name : 
                self.obj = book
                print "get opened workbook '%s'" % self.name
                break

        if not self.obj : # print "failed to find existing workbook '%s'" % book_name
            #! local $Win32::OLE::Warn = 3;  # ignore on errors
            # 2nd try : open it
            try:
                self.obj = Excel.Workbooks.Open(path)
                print "opened existing workbook '%s'" % path
            except Exception, e:
                if must_exist :
                    raise e, "failed to find existing workbook '%s'" % path
                    return

                # 3rd try : create it
                try:
                    self.obj = Excel.Workbooks.Add()
                    self.obj.SaveAs(path)
                    print "created new workbook '%s'" % self.name
                except Exception, e:
                    raise e, "failed to create new workbook '%s'" % self.name

        # Excel.Visible = 1
        self.Sheets = [Sheet(x) for x in self.obj.Worksheets]
        for s in self.Sheets : 
            self.SheetsHash[s.Name] = s

    def __getattr__(self, attr):
        """docstring for __getattr__"""
        return getattr(self.obj, attr)
    def __repr__(self):
        """docstring for __repr__"""
        return "excel.Book(%s) = %s" % (self.path, repr(self.obj))
    def __getitem__(self, key):
        """docstring for __getitem__"""
        if self.csv(): return None
        if isinstance(key,int) :
            return self.Sheets[key]
        else:
            return self.SheetsHash[key]
        return None


class Sheet :
    """docstring for Sheet"""
    def __init__(self, obj):
        self.obj = obj
    def __getattr__(self, attr):
        """docstring for __getattr__"""
        return getattr(self.obj, attr)
    def __repr__(self):
        """docstring for __repr__"""
        return "excel.Sheet(%s) = %s" % (self.Name, repr(self.obj))
    def lastcell(self):
        """docstring for last_cell"""
        return self.obj.Cells.SpecialCells(C.xlLastCell)
    def cell(self,row,col):
        """docstring for last_cell"""
        return self.obj.Cells(row,col)
    def cells(self):
        """docstring for Cells"""
        if self.obj.FilterMode : self.obj.ShowAllData()
        return self.obj.Range(self.obj.Cells(1,1), self.lastcell());

    def data(self):
        """docstring for data"""
        return self.cells().Value

    def data_rowhash(self):
        """return data in hash format"""
        d = self.data()
        ROW = len(d   )
        COL = len(d[0])
        res = {}
        for col, row in enumerate(d) : # header
            key = row[0].strip()
            if key : 
                res[key] = row[1:]
    def data_colhash(self):
        """return data in hash format"""
        d = self.data()
        ROW = len(d   )
        COL = len(d[0])
        res = {}
        for col, key in enumerate(d[0]) : # header
            key = key.strip()
            if key : 
                res[key] = [row[col] for row in d[1:]]
        
################################################################################
# parser
################################################################################

class HeadSheet (Sheet):
    """docstring for row"""

    mapping = {
        'module'  : 'mod' ,
        'inst'    : 'inst',
        'pin'     : 'pin' ,
        'net'     : 'net' ,
        'IO'      : 'io'  ,
        'term'    : 'term',
        'protocol': 'protocol',
        'fixme'   : 'fixme', 
        'comment' : 'comment'
    }

    class RowData :
        """docstring for RowData"""
        def __init__(self, head, data, row):
            self._head = head
            self._data = data
            self._row  = row
            for k,v in zip(head, data):
                if k : setattr(self, k, v)
        def __repr__(self):
            d = dict(zip(self._head,self._data))
            return repr(d)

    def __init__(self, sheet): # def __init__(self, head_data, module):
        Sheet.__init__(self,sheet.obj)

        self._data = self.data()

        self._ROW  = len(self._data) # last row
        self._row  = 1 # 1 based (same as excel), point to current processed row

        self._head = []
        head = [str(x) and str(x).strip() for x in self._data[self._row-1]]
        if not self.mapping :
            self._head = head
        else:
            for x in head:
                if self.mapping.has_key(x) :
                    self._head.append(self.mapping[x])
                else:
                    # print "head '%s' not recognized!" % x
                    self._head.append('')

    def post(self, row):
        """docstring for post"""
        return 1 # valid enum

    # def enum(self):
    #     """docstring for set"""
    #     for r , row_data in enumerate(self._data[1:]):
    #         self._row = r+2
    #         self.pre()
    #         for i in range(len(row_data)):
    #             d = row_data[i]
    #             setattr(self, self._head[i], d)
    #             # print self._head[i], "<=", row_data[i]
    #         if self.post() : yield

    def __iter__(self): # Get iterator object on iter( )
        return self
    def next(self): # Return a square on each iteration
        self._row += 1
        if self._row > self._ROW:
            self._row == 1
            raise StopIteration
        
        self._rowdata = self.RowData(self._head, self._data[self._row-1], self._row)
        if self.post(self._rowdata) :
            return self._rowdata
        else:
            return next(self)

if __name__ == '__main__':
    # for book in Excel.Workbooks: print book.Name

    book = Book(r'H:\site\mad\razor\client\Verification Plan Template v001.xlsx',1)
    s = book['apbh']
    print s
    hs = HeadSheet(s)
    print hs
    print hs._row , hs._ROW
    for row in hs:
        print row._data

    # print test.Sheets[0].cells().Value
else:
    pass # Work as a module

#print repr(o)
#<COMObject Word.Application>
#<win32com.gen_py.Microsoft Excel 12.0 Object Library._Application instance at 0x17111960>

#o.Visible = 1
#o.Workbooks.Add() # for office 97 95 a bit different!
#o.Cells(1,1).Value = "Hello" 
