import xlrd
__all__ = ['book', 'sheet', '_book']

_book = None
def book(name):
    """docstring for book"""
    global _book
    _book = xlrd.open_workbook(name)
    return _book
def sheet(name):
    """docstring for sheet"""
    import re
    r = re.compile(r'%s' % name)
    for s in _book.sheets():
        if r.search(s.name):
            return s
    return None

def _code():
    pass

def main():
    book(r'H:\site\mad\razor\client\Verification Plan Template v001.xlsx')
    ##################################################################################
    ## book attribute
    ##################################################################################
    print book.codepage
    print book.countries
    print book.user_name

    ##################################################################################
    ## traverse whole book
    ##################################################################################

    ##  for sheet in book.sheets():
    ##      ##################################################################################
    ##      ## sheet attribute
    ##      ##################################################################################
    ##      print sheet.name,sheet.nrows, sheet.ncols, sheet.visibility
    ##  
    ##  print book.nsheets
    ##  for sheet_index in range(book.nsheets):
    ##      print book.sheet_by_index(sheet_index)
    ##  
    ##  print book.sheet_names()
    ##  for sheet_name in book.sheet_names():
    ##      print book.sheet_by_name(sheet_name)

    ##################################################################################
    ## fetch data
    ##################################################################################
    ##  for s in book.sheets():
    ##      print 'Sheet:',s.name
    ##      for row in range(s.nrows):
    ##          for col in range(s.ncols):
    ##              c = s.cell(row,col) # s.cell_value(row,col) is faster than get cell obj
    ##              print c.ctype , c.value
    ##              #print xlrd.cellname(row,col),'-' c.value
    ##  
    ##  for s in book.sheets():
    ##      if s.name != "ibis_writer": continue
    ##      print 'Sheet:',s.name
    ##      for c in s.row(18):
    ##          print c.value
    ##      print s.row_values(18)
    ##      print s.row_values(18,1,3)

if __name__ == '__main__':
    main() # Work as a script
else:
    pass # Work as a module
