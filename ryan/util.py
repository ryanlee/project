import pandas as pd
import numpy as np
import logging

from multiprocessing import Pool
def mdict(dic, **kwargs):
    keep = []
    only = 0
    for t,f in kwargs.items():
        if t == "_keep":
            assert(type(f) is list)
            keep.extend(f)
            only = 1
        elif t== "_kill":
            assert(type(f) is list)
            for i in f:
                if i in dic:
                    dic.pop(i)
        else:
            keep.append(f)
            if isinstance(f,str) and f in dic:
                v = dic.pop(f)
            else:
                v = f
            if t[0:4] != "_no" :
                keep.append(t)
                dic[t] = v
    if only:
        keys = dic.keys() - keep
        for k in keys:
            del dic[k]
    return dic

import multiprocessing.dummy
def par(func, l, n=100, extend=True):
    threads = multiprocessing.dummy.Pool(n)
    if isinstance(l, pd.core.frame.DataFrame):
        l = l.to_dict('records')
    list_of_res = threads.map(func, l)
    if extend :
        res = []
        for x in list_of_res :
            if x is not None:
                res.extend(x)
        res = [r for r in res if r is not None]
        return res
    else:
        res = [r for r in list_of_res if r is not None]
        return res
def chunks(l, n=25):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

from   datetime import timezone, timedelta
EST = timezone(timedelta(hours=-4))

################################################################################
##  cache
################################################################################
import os, hashlib, logging
cached_mem = {}
cached_folder = os.path.join('.', '.cache')
def cached(dt=None, timer_name=None):
    global cached_mem, cached_folder
    if not os.path.exists(cached_folder) : os.mkdir(cached_folder)
    def wrap(f):
        fname = f.__name__
        def wrapped_f(*args, **kwargs):
            cacheable = kwargs.pop('cacheable', True)
            args_for_tag = list(args[0:])
            for i,arg in enumerate(args_for_tag):
                if isinstance(arg, pd.DataFrame):
                    if 'symbol' in arg.columns :
                        args_for_tag[i] = sorted(set(arg['symbol']))
                    else:
                        args_for_tag[i] = "dataframe"
            tag = f"{args_for_tag}, {kwargs}"
            hash_tag = hashlib.md5(tag.encode('utf-8')).hexdigest()
            ff = os.path.join(cached_folder, f'{fname}-{dt}-{hash_tag}.h5')
            df = None
            if cacheable :
                if ff in cached_mem:
                    logging.debug("reuse  MEM cache %s for %s" , ff, tag)
                    df = cached_mem[ff]
                elif os.path.exists(ff):
                    logging.debug("reuse FILE cache %s for %s" , ff, tag)
                    df = pd.read_hdf(ff, 'data')

            if df is None:
                logging.info("-> refreshing cache %s for %s" , ff, tag)
                with timer(timer_name=='' and fname or timer_name) :
                    df = f(*args, **kwargs)
                df.to_hdf(ff, 'data', index=False)
            cached_mem[ff] = df
            return df
        return wrapped_f
    return wrap

