from xml.etree import ElementTree as ET
import logging
import ryan
class XML :
    """docstring for XML"""
    product = ""
    feature = ""

    def __init__(self, xml_obj, product="",feature=[]):
        if product : XML.product = product
        if feature : XML.feature = feature

        if xml_obj is None :
            raise AttributeError
        if isinstance(xml_obj, str):
            self.__dict__['_ET'] = oET = ET.parse(xml_obj)
            self.__dict__['_obj'] = xml_obj = oET.getroot()
    def ET (self) :
        return self.__dict__['_ET']

    def __iter__(self)    :
        for o in          self._obj : yield XML(o)
    def __reversed__(self):
        for o in reversed(self._obj): yield XML(o)

    def __setattr__(self, attr, value): # self.attr
        # if attr=="__coerce__" : raise AttributeError
        setattr(self._obj, attr, value)
        if isinstance(value,basestring):
            l = attr.lower()
            u = attr.upper()
            if attr == l :
                logging.debug("settting %s %s", u, value )
                setattr(self._obj, u, value.upper())

    @classmethod
    def valid(klass,obj) :
        is_valid = 0
        prod = obj.get("product")
        feat = obj.get("feature")
        if not klass.product and not klass.feature : is_valid = 1
        elif not prod and not feat : is_valid = 1
        else :
            is_valid = 1
            if prod and klass.product :
                if klass.product not in prod :
                    logging.debug("%s is in %s", klass.product, prod)
                    is_valid = 0

            if feat and klass.feature :
                if feat not in klass.feature :
                    is_valid = 0

        # ryan.trace("isvalid="+str(is_valid))
        return is_valid

            
    def __getattr__(self, attr): # self.attr
        obj = self._obj
        if hasattr(obj,attr): return getattr(obj,attr)
        
        if attr.startswith("_") : # list style
            return_list = 1
            tag = attr[1:]
        else :
            return_list = 0
            tag = attr

        found = list(obj.iter(tag))
        if found is None or len(found)==0: 
            raise ryan.E( "XML element '%s' not found under :\n%s" %(tag,repr(self)))
        else :
            if return_list :
                return [XML(x) for x in found if XML.valid(x)]
            else :
                found_and_valid = [x for x in found if XML.valid(x)]
                if len(found_and_valid)>1:
                    raise ryan.E( "XML element '%s' is actually a list, you can't use it as single item :\n%s" %(tag,repr(self)))
                elif len(found_and_valid)==0:
                    raise ryan.E( "XML elemtn '%s' not valid due to product condition : %s" %(tag,repr(self)))
                else :
                    return XML(found_and_valid[0])

    def __len__ (self):
        return len(self._obj)

    def __getitem__(self, key): # self[key]
        obj = self._obj
        if key in obj.keys() :
            return obj.get(key)
        else :
            return getattr(self, key)

    def __trunc__(self):
        return int(self._obj.text)
    def __str__(self):
        t = self._obj.text 
        if t is None: return ""
        else : return t
        return str()
        return "XML("+str(self._obj)+")"
    def __repr__(self):
        return "XML("+repr(self._obj)+")={\n"+ET.tostring(self)+"}" 

    def tostring(self):
        return ET.tostring(self._obj)

    def search(self,what):
        obj = self._obj
        for text in obj.itertext():
            if what in text :
                return 1
        else :
            return 0

    def add(self,tag,att={},**kwargs):
        """docstring for add"""
        return XML(ET.SubElement(self,tag,att,**kwargs))
        
if __name__ == '__main__':
    root = XML(r'U:\script\python\OmniCoder\data\regs_epdc_mx6sl.xml')
    for r in root._register :
        print r.tag, r.registerName, r.registerDescription.search("_CLR")

    # for r in regs :
    #     print r.hwreg_name
    #     print r.hwreg_addr

    # upd = r[0]
    # # print "%s @ %s" % (upd.hwreg_name["mnemonic"], upd.hwreg_addr)
    # print upd
    # print upd.hwreg_encoding.hwreg_bitfld[2]["name"]
    # h = upd.hwreg_encoding.hwreg_bitfld[2]
    # print h
else:
    pass # Work as a module
