#!/usr/bin/env python
# NOTE 
# all links and directory size are ignored, but in du it's calculated as 4.0K

import re, os, sys

################################################################################
##  utility
################################################################################
from ryan import size_fmt, time_fmt, date

bgcolors = {}
for i in range(0,101,1): # RRGGBB
    r = int(255*i/100)
    g = int(255*(100-i)/100)
    bgcolors[i] = "#%02X%02X%02X" % (r,g,0) # elegant style

WHITE = "#ffffff"
def progress_bar(ratio,colors=bgcolors,bgcolor=WHITE):
    if ratio > 100 :
        ratio = 100
    elif ratio < 1 and ratio != 0 :
        ratio = 1
    else:
        ratio = int(ratio)
    if isinstance(colors,str) :
        color = colors
    else:
        color = colors[ratio]
    RATIO_COLOR = '<span style="text-align:left;background-color:%s;">%s</span><span style="text-align:left;background-color:%s;color:lightgrey;">%s</span>' % (color, '&nbsp;' * ratio, bgcolor, '&nbsp;' * int(100-ratio) ) 
    return RATIO_COLOR

################################################################################
##  email
################################################################################
def user2email (user):
    m = re.compile(r'^nx.\d+$').search(user)
    if m:
        email = user
    else:
        email = ""
    return email

def mail(content, subject="DISK REPORT",to=[],cc=[],bcc=[],red=False):
    global opt
    if opt.cc  is not None and opt.cc  != [] :  cc.extend(opt.cc )
    if opt.bcc is not None and opt.bcc != [] : bcc.extend(opt.bcc)

    subject_content = "[disko] "+subject

    if to != [] :
        from ryan import cfg
        cfg.r()
        acc = cfg.get('email', 'account', prompt="Enter your email account: ")
        pwd = cfg.get('email', 'password', prompt="Enter your email password: ")

        u2e = {user:user2email(user) for user in to}
        u2e = cfg.get('user2email', u2e)
        to = [e for e in sorted(set(u2e.values())) if e!=""]

        from ryan.mail import Mail

        m = Mail(acc,pwd)
        m.write(content)
        #  text = get_template('email.txt'); text_content = text.render(d)

        m.send(to,cc,bcc, subject_content, red)

################################################################################
##  sub process
################################################################################
import time,datetime
from os import scandir
def p_dir(q_dir, q_out, file_count, working):
    global opt
    pid = os.getpid()

    data_users = {}
    data_files = []
    data_dirs  = []

    logging.debug("p_dir %10d start" , pid) 
    try:
        while True:
            # try : 
            #     path = q_dir.get(True, 100)
            # except Queue.Empty as e:
            #     break
            path = q_dir.get()
            if path is None :
                q_dir.put(None)
                break
            working.value = 1
            total_dirs = 0
            total_files = 0
            try:
                for entry in scandir(path):
                    p = entry.path
                    if entry.is_dir(follow_symlinks=opt.link):
                        total_dirs += 1
                        m = re.compile(r'/\.(snapshot|SYNC|Trash-[a-zA-Z0-9]+)$').search(p)
                        if m : continue
                        q_dir.put(p)
                    elif entry.is_file(follow_symlinks=opt.link) : # or entry.is_symlink()
                        total_files += 1
                        file_count.value += 1
                        stat = entry.stat(follow_symlinks=opt.link) 
                        size = stat.st_size
                        if size == 0 : continue

                        # if entry.is_symlink() : size = 4* 1024 # du show it as 4.0KB, but actually it's 66B

                        t = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                        user = stat.st_uid

                        if user in data_users :
                            s = data_users[user]
                        else:
                            s = 0
                        data_users[user] = s + size

                        if size > opt.report_size_file *1024*1024 :
                            data_files.append( (size, user, t, p) )
            except OSError as e:
                pass

            # time.sleep(1)
            if total_dirs+total_files > opt.report_size_dir : 
                stat = os.stat(path) 
                user = stat.st_uid
                t = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                data_dirs.append( (total_dirs+total_files, user, t, path+'/', total_dirs, total_files) )
                # logging.debug("huge direcotry '%s' with %d dirs and %d files inside", path, total_dirs, total_files)

            working.value = 0

        q_out.put( (data_dirs, data_files, data_users) )

    except KeyboardInterrupt as e:
        pass
        # logging.warning("p_dir %10d detected Ctrl+C and exit" , pid)
    logging.debug("p_dir %10d done" , pid) 

################################################################################
##  main process
################################################################################
import logging, argparse
import subprocess,os

def df (path) :
    quota, used, free, percent, mount = 1000, 1000, 0, "100%", "LOCAL"
    if opt.quota != 0 :
        quota = opt.quota/1000
    else:
        try :
            ret = 0
            out = subprocess.check_output("df -k %s" % (path),shell=True)
        except subprocess.CalledProcessError as e:
            out = e.output
            ret = e.returncode
        if ret == 0 :
            lines = out.decode().split("\n")
            if len(lines) == 4 :
                quota, used, free, percent, mount = lines[2].split()
            elif len(lines) == 3 :
                nfs, quota, used, free, percent, mount = lines[1].split()
            else :
                logging.error("not able to parse df result :\n%s", lines)
        else:
            pass
            # quota, used, free, percent, mount = 1000, 1000, 0, "100%", "LOCAL"
    quota  = int(quota)*1024
    used  = int(used)*1024
    free  = int(free)*1024
    return mount, quota, used, free

from multiprocessing import Value, Manager, Process, cpu_count
#  import Queue
class Monitor :
    mounts = {}

    @classmethod
    def new (klass, pathes) :
        for path in pathes:
            if not os.path.isdir(path) :
                logging.error("path %s is not a existing directory, skip it!", path)
                continue
            mount, quota, used, free  = df(path)
            if mount not in Monitor.mounts:
                Monitor.mounts[mount] = Monitor(mount, quota, used, free)

            j = Monitor.mounts[mount]
            j.pathes.append(path)
        return Monitor.mounts.values()

    def __init__(self, mount, quota, used, free):
        self.pathes = []
        self.mount = mount
        self.quota  = quota
        self.used  = used
        self.free  = free
        self.t    = 0
        if quota != 0 :
            self.percent = float(used*100)/float(quota)
        else:
            self.percent = 0
        logging.info("QUOTA %s (%s) = %s + %s (%2.2f%% used)", mount, size_fmt(quota), size_fmt(free), size_fmt(used), self.percent)

    def refresh_quota (self):
        mount, self.quota, self.used, self.free  = df(self.mount)
        if self.quota != 0 :
            self.percent = float(self.used*100)/float(self.quota)
        else:
            self.percent = 0
        return self.percent

    def run (self):
        global opt
        if opt.quota_min != 0 : # monitor
            q = self.refresh_quota()
            if q < opt.quota_min :
                return
            else:
                now = time.time()
                if q > opt.quota_max : # check every hour after > max
                    interval = 1
                else:
                    interval = opt.interval               # otherwise based on opt (default to 8 hours)
                if now - self.t < interval * 3600 :
                    return
                else:
                    logging.warning("%s checked %d second(s) before, recheck", self.mount, now-self.t )

        self._run()

    def _run (self):
        self.t = time.time()
        try:
            m = Manager()
            q_dir = m.Queue()
            q_out = m.Queue()

            for path in self.pathes: q_dir.put(path)

            ps = []
            cs = [] # file count
            ws = [] # working
            for i in range(opt.n):
                c = Value('i', 0)
                w = Value('i', 0)
                p = Process(target=p_dir , args=(q_dir, q_out, c, w))
                p.start()
                ps.append(p)
                cs.append(c)
                ws.append(w)
            logging.info("-> analyzing %s (quota=%s, %2.1f%% used) for :\n  %s", self.mount, size_fmt(self.quota), self.percent, "\n".join(["   " +i for i in self.pathes]) )

            while 1:
                time.sleep(1)
                counts = [c.value for c in cs]
                total  = sum(counts)
                working = sum([w.value for w in ws])
                sys.stdout.write("\r%s %10d DIRs ==(%2d)==> %10d FILEs" % (date(), q_dir.qsize(), working, total)); sys.stdout.flush()
                if q_dir.empty() and working == 0:
                    sys.stdout.write("\n"); sys.stdout.flush()
                    self.count = total
                    break
                elif q_dir.empty() :
                    logging.info("queue is empty but %d workers are still parsing dirs", working)
                    pass

            q_dir.put(None)
            for p in ps:
                logging.debug("p_dir %s is joining ...", p.pid);
                p.join(60)
                logging.debug("p_dir %s joined", p.pid);

            self.report(q_out)

        except KeyboardInterrupt as e:
            # logging.warning("main detected Ctrl+C and exit" )
            for p in ps: p.join(10)
            raise e

    def report (self, q_out):
        import pwd
        global opt

        data_users = {}
        data_files = []
        data_dirs  = []
        try :
            for dirs, files, users in iter(q_out.get_nowait, None):
                data_files.extend(files)
                data_dirs.extend(dirs)
                for user in users:
                    if user in data_users:
                        data_users[user] += users[user]
                    else :
                        data_users[user]  = users[user]
        except Exception as e:
            print(e)
            pass

        # FILES
        try:
            f = open('disko.rpt','w')
        except:
            f = None

        files_by_user = {}
        report_files = []
        for size, uid, t, path in sorted(data_files, key=lambda x:x[0], reverse=True):
            if f : f.write("%16d\t%10d\t%20s\t%-s\n" % (size, uid, t, path))
            if uid not in files_by_user: files_by_user[uid] = []
            files_by_user[uid].append( (size_fmt(size), t, path) )
            report_files.append ((
                    size_fmt(size),
                    user_fmt(uid),
                    t,
                    path
                    ))
        for size, uid, t, path, dirs, files in sorted(data_dirs, key=lambda x:x[0], reverse=True):
            if f : f.write("%16d\t%10d\t%20d\t%-s\n" % (size, dirs, files, path))
            if uid not in files_by_user: files_by_user[uid] = []
            files_by_user[uid].append( (size, t, path) )
            report_files.append ((
                    size,
                    user_fmt(uid),
                    t,
                    path
                    ))
        if f : f.close()

        # USERS
        report_users = []
        users = []
        total_size = 0

        if len(data_users) > 0 :
            MAX_USER = max(data_users.values())
            import operator
            for uid, size in sorted(data_users.items(), key=operator.itemgetter(1), reverse=True) :
                total_size += size
                if size < opt.report_size_user*1024*1024 : continue
                email = ""
                try: #TODO duplication
                    user_pw = pwd.getpwuid(uid)
                    user = user_pw.pw_name # login name (ID)
                    uname = user_pw.pw_gecos #user full name
                    users.append(user)
                except KeyError as e:
                    uname = "UNKNOWN-%d"% (uid,)
                bar = progress_bar(100*size/MAX_USER)
                report_users.append( (user, uname, size_fmt(size), bar, email, files_by_user[uid] if uid in files_by_user else "") )
                logging.info("%-10s\t%20d(%10s) %-30s ", uid, size, size_fmt(size), uname)

        if opt.quota != 0 :
            logging.info("SUMMARY : %d FILEs, %s / %s = %2.2f%%", self.count, size_fmt(total_size), size_fmt(opt.quota), total_size*100/opt.quota)
        else:
            logging.info("SUMMARY : %d FILEs, %s ", self.count, size_fmt(total_size))

        summary = [
                ('QUOTA'       , "%2.1f%%(%s) used @ %s(%s)" % ( self.percent, size_fmt(self.used), self.mount, size_fmt(self.quota))          ,                   ),
                ('PERFORMANCE' , "took %s analyzing %d files (%s) under : %s" % ( time_fmt(time.time()-self.t), self.count, size_fmt(total_size), self.pathes) ,      ),
                ('CONFIG'      , "%s" % (opt, ) ,                                                                                         ),
                ]

        logging.info("generating report for %s (quota=%s, %2.1f%% used) to :\n%s", self.mount, size_fmt(self.quota), self.percent, users)
        from mako.template import Template
        temp = Template(html); content = temp.render(users= report_users, files=report_files, summary=summary)
        try:
            f = open('disko.html','w')
            f.write(content)
        except Exception as e:
            print(e)

        if opt.quota_min > 0 or opt.email :
            mail (content, "%2.1f%% @ %s (%s)" % (self.percent, self.mount, size_fmt(self.quota) ) , users , red = (self.percent > opt.quota_max))

################################################################################
##  main
################################################################################
def main():
    from ryan import arg
    with arg.parser("disko", """
examples :
    disko -n  8 <directory>
                 one time run on arbitratry dir with 8 processes
    disko -n 16 <PATH1> <PATH2>
                 one time report on two project disks with 16 processes
    disko -p 90 <PATH1> <PATH2> 
                 keep monitoring all quota disks and report when > 90%
    """) as p :

        p.add('-i', '--interval', type=int, default=8, help="checking interval, unit is HOUR, default to 8")
        p.add('-q', '--quota', type=int, default=0, help="specify quota if df -k not available, unit = MB")
        p.add('-p', '-quota_min', '--quota_min', type=int, default=0, help="min quota percent to analyze and report, default to 0, which is only report to yourself")
        p.add(      '-quota_max', '--quota_max', type=int, default=98, help="max quota percent to analyze and report every hour")

        # p.add('-t', '--timeout', default=0, help="timeout setting for all monitors in this run, default to '24' hour")
        p.add('-n', '--n', type=int, default=cpu_count(), help="multiprocess number, default to all cores (%d)" % cpu_count() )

        p.add('-link', '--link', default=False, action='store_true',help="enable link dereference") 
        p.add('-dir' , '--report_size_dir' , type=int, default=  1000, help="directory have more items above this will be reported, default to 1000 (files+dirs)")
        p.add('-file', '--report_size_file', type=int, default=   10, help="file size above this will be reported, default to 10MB (unit is MB)")
        p.add('-user', '--report_size_user', type=int, default=   10, help="user size above this will be reported, default to 10MB (unit is MB)")

        p.add('-email', '--email', action='store_true', help="send email first time it runs")
        p.add('-cc', '--cc', nargs='+', help="email cc list")
        p.add('-bcc', '--bcc', nargs='+', help="email bcc list")

        p.add('inputs'    , nargs='*', help="multiple pathes supported even crossing mounts")

    global opt
    opt = p.opt
    opt.quota *= 1024*1024

    ################################################################################
    ##  calculate quota and seperate paths for multiple loop
    ################################################################################
    monitors = Monitor.new(opt.inputs)
    if len(monitors) == 0 :
        p.help()
        return

    ################################################################################
    ##  minitor all workers
    ################################################################################
    try :
        while True:
            percents = []
            for monitor in monitors:
                monitor.run()
                percents.append("%s@%2.0f%%" %(monitor.mount,monitor.percent))
            if opt.quota_min == 0 : # one time
                break
            else:
                s = "\r%s %s" % (date(), " ".join(percents))
                sys.stdout.write(s); sys.stdout.flush()
                time.sleep(60) # NOTE: interval decide whether we run full analysis, df is checked per minitues incase it's > max, then report per hour
                sys.stdout.write("\r" + ' '*len(s) + "\r"); sys.stdout.flush()
            opt.email = True
    except KeyboardInterrupt as e:
        pass

html = """
<html lang="en">
<head>
	<script>
	function toggle(id) {
		var x = document.getElementById(id);
		if (x.style.display === "none") {
			x.style.display = "block";
		} else {
			x.style.display = "none";
		}
	}
	</script>
	<style media="all" type="text/css">
		body {
			/*font-family:'Lucida Grande', 'Lucida Sans Unicode', 'Trebuchet MS', Calibri, Verdana, Arial, sans-serif;*/
			font-family: Calibri;
			font-size:10pt; 
		}
		thead tr {
			background-color: #92D050;
		}
		tr.odd {
			background-color: #DDD;
		}
		table.hide {
			display:none;
		}
		tr.even {
			background-color: white;
		}
		td,th {
			border-collapse: collapse;
			white-space:nowrap;
			border:solid windowtext 1.0pt;
			padding : 2pt;
			border-color: #AAA;
			/* word-wrap:nowrap; */
		}
		th {
			border-color: black;
			/* word-wrap:nowrap; */
		}
		a:link {
			color: #5B80B2;                                                               
			text-decoration: none;                                                        
			font-weight: bold;                                                            
		}
	</style>
</head>
<body> 
	
<h2> Summary </h2>
<table class="rel" rules="all"  frame="box" cellpadding="0" cellspacing="0" >
%for k,v in summary :
<tr class="${loop.cycle('even', 'odd')}">                        
	<th > ${k}</th>
	<td > ${v}</td>
</tr>
%endfor 
</table>

<h2> User Report </h2>
<table class="rel" rules="all"  frame="box" cellpadding="0" cellspacing="0" >
	<thead>
		<tr>
			<th > User ID </th>
			<th > User Name </th>
			<th > Usage </th>
			<th >  </th>
		</tr>
	</thead>
	<tbody>
%for user,uname, size,bar,email, files_by_user in users :
	<tr class="${loop.cycle('even', 'odd')}">
		<td>
		%if email != "" :
			<a href='mailto:${email}'>${user}</a>
		%else :
			${user}
		% endif
		</td>
		<td style="white-space: nowrap;">${uname}</td>
		<td style="text-align:right"> ${size} </td>
		<td> ${bar|n} </td>
	</tr>
%endfor
	</tbody>
</table>
<br/>
<br/>

<h2> <a class='zip' href="javascript:void(0)" onclick="toggle('file_report')"> File Report (${len(files)}) </a></h2>
	<table id="file_report" class="hide" style="display:block">
	<thead>
		<tr>
			<th > SIZE </th>
			<th > USER </th>
			<th > DATE </th>
			<th > PATH </th>
		</tr>
	</thead>
	<tbody>
		%for size_fmt, user, t, path in files :
		<tr class="${loop.cycle('even', 'odd')}">
			<td bgcolor="" style="white-space: nowrap;"> ${size_fmt} </td>     
			<td bgcolor="" style="white-space: nowrap;"> ${user} </td>     
			<td bgcolor="" style="white-space: nowrap;"> ${t} </td>     
			<td bgcolor="" > <font face="courier new" size='2'>${path}</font> </td>     
		</tr>                                                        
		%endfor
	</tbody>
	</table>
<br/>
<br/>

<h2> File Report By User</h2>
%for user,uname, size,bar,email, files_by_user in users:
<h3> <a class='zip' href="javascript:void(0)" onclick="toggle('file_report_${user}')"> ${uname} (${len(files_by_user)}) </a></h3>
	<table id="file_report_${user}" class="hide" style="display:block">
		%for size_fmt, t, path in files_by_user:
		<tr class="${loop.cycle('even', 'odd')}">
			<td bgcolor="" style="white-space: nowrap;"> ${size_fmt} </td>     
			<td bgcolor="" style="white-space: nowrap;"> ${t} </td>     
			<td bgcolor="" > <font face="courier new" size='2'>${path}</font> </td>     
		</tr>                                                        
		%endfor
	</table>
%endfor

<hr/>
this is disk analysis report generated by <a href="/">disko</a> <br>
-- <a href=''>Ryan</a>
<br/>
</body>
</html>
"""

if __name__ == '__main__':
    main() # Work as a script
else:
    pass # Work as a module


