import subprocess
def call(cmd, verbose=0):
    if verbose != 0 :
        print("->", cmd)
        print('-' * 80)

    if verbose < 0 :
        return

    if isinstance(cmd, str):
        ret = subprocess.call(cmd,shell=True)
    elif isinstance(cmd, list):
        ret = subprocess.call(cmd,shell=False)
    return ret

def exe(cmd, verbose=-1):
    if verbose > 0:
        print("->", cmd)
        print('-' * 80)

    # print(cmd.__class__)
    try :
        ret = 0
        if isinstance(cmd, list):
            out = subprocess.check_output(cmd,shell=False)
        else : # isinstance(cmd, str): # could be either str or unicode!
            out = subprocess.check_output(cmd,shell=True)
    except subprocess.CalledProcessError as e:
        out = e.output
        ret = e.returncode
        if verbose >= 0 : # -1 to real silient
            logging.error("subprocess call failed : cmd=%s, ret=%s, out=%s", cmd, ret, out)

    if verbose > 0:
        print(out)
        print('-' * 80)
    return out, ret

def monitor (cmd, verbose=1):
    if verbose :
        print("->", cmd)
        print('-' * 80)

    # print(cmd.__class__)
    try :
        out = ""
        ret = 0
        if isinstance(cmd, list):
            shell=False
        else : # isinstance(cmd, str): # could be either str or unicode!
            shell=True
        p = subprocess.Popen(cmd, shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        while True:
            line = p.stdout.readline()
            if not line: break
            print(line,)
            out += line #.rstrip()
        # for line in p.stdout:
        #     print(">>> " +line,)
        #     out += line.rstrip()
    except subprocess.CalledProcessError as e:
        out = e.output
        ret = e.returncode
        logging.error("subprocess call failed : cmd=%s, ret=%s, out=%s", cmd, ret, out)

    # if verbose :
    #     print(out)
    #     print('-' * 80)
    return out, ret
