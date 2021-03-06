import os, sys, subprocess, tempfile

pushed_logs = "/opt/monitor/pushed_logs"
archive_dir = "/opt/monitor/var/archives"

class SubcommandException(Exception):
	pass

## log commands ##
# force running push_logs on poller and peer systems
def cmd_fetch(args):
	"""[--incremental=<timestamp>]
	Fetches logfiles from remote nodes and stashes them in a local path,
	making them available for the 'sortmerge' command.
	"""
	since = ''
	for arg in args:
		if arg.startswith('--incremental='):
			since = '--since=' + arg[14:]

	for node in mconf.configured_nodes.values():
		if node.ntype == 'master':
			continue
		ctrl = "mon log push"
		if since:
			ctrl += ' ' + since
		if not node.ctrl(ctrl):
			print("Failed to force %s to push its logs. Exiting" % node.name)
			sys.exit(1)

def cmd_sortmerge(args):
	"""[--since=<timestamp>]
	Runs a mergesort algorithm on logfiles from multiple systems to
	create a single unified logfile suitable for importing into the
	reports database.
	"""
	since = False
	for arg in args:
		if (arg.startswith('--since=')):
			since = arg.split('=', 1)[1]

	if since:
		since = '--incremental=' + since

	pushed = {}
	for (name, node) in mconf.configured_nodes.items():
		if node.ntype == 'master':
			continue
		if not os.access(pushed_logs + '/' + node.name, os.X_OK):
			print("Failed to access() pushed_logs dir for %s" % node.name)
			return False

		pushed[name] = os.listdir(pushed_logs + '/' + node.name)
		if len(pushed[name]) == 0:
			print("%s hasn't pushed any logs yet" % name)
			return False

		if 'in-transit.log' in pushed[name]:
			print("Log files still in transit for node '%s'" % node.name)
			return False

	if len(pushed) != mconf.num_nodes['peer'] + mconf.num_nodes['poller']:
		print("Some nodes haven't pushed their logs. Aborting")
		return False

	last_files = False
	for (name, files) in pushed.items():
		if last_files and not last_files == files:
			print("Some nodes appear to not have pushed the files they should have done")
			return False
		last_files = files

	app = merlin_dir + "/import"
	cmd_args = [app, '--list-files', args, archive_dir]
	stuff = subprocess.Popen(cmd_args, stdout=subprocess.PIPE)
	output = stuff.communicate()[0]
	sort_args = ['sort']
	sort_args += output.strip().split('\n')
	for (name, more_files) in pushed.items():
		for fname in more_files:
			sort_args.append(pushed_logs + '/' + name + '/' + fname)

	print("sort-merging %d files. This could take a while" % (len(sort_args) - 1))
	(fileno, tmpname) = tempfile.mkstemp()
	retno = subprocess.call(sort_args, stdout=fileno)
	if retno:
		raise SubcommandException()
	print("Logs sorted into temporary file %s" % tmpname)
	return tmpname


# run the import program
def cmd_import(args):
	"""[--fetch]
	This commands run the external log import helper.
	If --fetch is specified, logs are first fetched from remote systems
	and sorted using the merge sort algorithm provided by the sortmerge
	command.
	"""
	since = ''
	fetch = False
	i = 0
	for arg in args:
		if arg.startswith('--incremental='):
			since = arg[14:]
		elif arg == '--truncate-db':
			since = '1'
		elif arg == '--fetch':
			fetch = True
			args.pop(i)
		i += 1

	if not '--list-files' in args:
		db_user = mconf.dbopt.get('user', 'merlin')
		db_pass = mconf.dbopt.get('pass', 'merlin')
		db_type = mconf.dbopt.get('type', 'mysql')
		args.insert(0, '--db-user=%s' % db_user)
		args.insert(0, '--db-pass=%s' % db_pass)
		args.insert(0, '--db-type=%s' % db_type)
		conn_str = mconf.dbopt.get('conn_str', False)
		if conn_str != False:
			args.insert(0, '--db-conn-str=%s' % mconf.dbopt.get('conn_str', False))
		else:
			db_name = mconf.dbopt.get('name', 'merlin')
			db_host = mconf.dbopt.get('host', 'localhost')
			db_port = mconf.dbopt.get('port', False)
			args.insert(0, '--db-host=%s' % db_host)
			args.insert(0, '--db-name=%s' % db_name)
			if db_port != False:
				args.insert(0, '--db-port=%s' % db_port)

		if mconf.num_nodes['poller'] or mconf.num_nodes['peer']:
			if fetch == True:
				cmd_fetch(since)
				tmpname = cmd_sortmerge(['--since=' + since])
				print("importing from %s" % tmpname)
				import_args = [merlin_dir + '/import', tmpname] + args
			else:
				import_args = [merlin_dir + '/import'] + args
			retcode = subprocess.call(import_args, stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno())
			if retcode:
				print("Failed to run log import subcommand")
				print("  %s" % ' '.join(import_args))
				raise SubcommandException()
			return True

	app = merlin_dir + "/import"
	ret = os.spawnv(os.P_WAIT, app, [app] + args)
	if ret < 0:
		print("The import program was killed by signal %d" % ret)
	return ret


# run the showlog program
def cmd_show(args):
	"""
	Runs the showlog helper program. Arguments passed to this command
	will get sent to the showlog helper. Use 'mon log show --help' for
	details.
	"""
	app = merlin_dir + "/showlog"
	ret = os.spawnv(os.P_WAIT, app, [app] + args)
	if ret < 0:
		print("The showlog helper was killed by signal %d" % ret)
	return ret

def cmd_purge(args):
	"""[--remove-older-than=<difference>]
	Remove data no longer in use.

	If --remove-older-than is specified, also removes log files and database
	entries older than <difference>. The difference is specified as a number,
	followed by a unit - 'y' for year, 'm' for month, 'w' for week, 'd' for day.
	For instance, to delete all logs older than 1 year:
		mon log purge --remove-older-than=1y
	"""
	import time, glob, merlin_db
	# units rounded upwards
	units = {'y':31622400, 'm':2678400, 'w':604800, 'd':86400}
	if os.path.exists('/opt/monitor/op5/pnp/perfdata/.trash'):
		subprocess.call(['find', '/opt/monitor/op5/pnp/perfdata/.trash', '-mindepth', '1', '-delete'])
	oldest = False
	for arg in args:
		if arg.startswith('--remove-older-than='):
			if not arg[-1] in units.keys():
				print("Invalid unit: " + arg[-1])
				return False
			try:
				diff = float(arg[20:-1]) * units[arg[-1]]
			except ValueError:
				print "Invalid number: " + arg[20:-1]
				return False
			oldest = time.mktime(time.gmtime()) - diff
	if not oldest:
		return True
	conn = merlin_db.connect(mconf)
	dbc = conn.cursor()
	dbc.execute('DELETE FROM notification WHERE end_time < %s', int(oldest))
	dbc.execute('DELETE FROM report_data WHERE timestamp < %s', int(oldest))
	for log in glob.glob(archive_dir + '/nagios-*.log'):
		if time.mktime(time.strptime(log, archive_dir + '/nagios-%m-%d-%Y-%H.log')) < oldest:
			os.remove(log)
	return True
