from merlin_apps_utils import *

class tap:
	"""Nifty class for testing particular subsystems"""
	def __init__(self, name, master=False):
		self.passed = 0
		self.failed = 0
		self.verbose = 1
		self.failures = []

	def test(self, a, b, msg):
		if a == b:
			return self.ok(msg)

		return self.fail(msg, a, b)


	def ok(self, msg):
		if self.verbose:
			print("  %sok%s   %s" % (color.green, color.reset, msg))
		self.passed += 1
		return True


	def fail(self, msg, a=False, b=False):
		if self.verbose:
			msg = "  %sfail%s %s" % (color.red, color.reset, msg)
			self.failures.append(msg)
			print(msg)
			if a != b:
				print(a, b)
		self.failed += 1
		return False


failed = 0
passed = 0
def test(a, b, msg):
	global passed, failed

	if a == b:
		if verbose:
			print("  %sok%s   %s" % (color.green, color.reset, msg))
		passed += 1
	else:
		print("  %sfail%s %s" % (color.red, color.reset, msg))
		print(a, b)
		failed += 1
	return a == b


class test_config_in:
	nagios_config_in = """log_file=@@DIR@@/nagios.log
broker_module=@@MODULE_PATH@@ @@DIR@@/merlin/merlin.conf
broker_module=@@LIVESTATUS_O@@ @@DIR@@/var/rw/live
query_socket=@@DIR@@/var/rw/nagios.qh
cfg_dir=@@DIR@@/etc/oconf
object_cache_file=@@DIR@@/var/objects.cache
temp_file=nagios.tmp
temp_path=@@DIR@@/var
status_file=@@DIR@@/var/status.log
status_update_interval=30
nagios_user=monitor
nagios_group=apache
enable_notifications=1
execute_service_checks=0
accept_passive_service_checks=1
execute_host_checks=0
accept_passive_host_checks=1
enable_event_handlers=1
log_rotation_method=d
log_archive_path=@@DIR@@/var/archives
check_external_commands=1
command_check_interval=1s
command_file=@@DIR@@/var/rw/nagios.cmd
lock_file=@@DIR@@/var/nagios.lock
retain_state_information=1
state_retention_file=@@DIR@@/var/status.sav
retention_update_interval=60
use_retained_program_state=1
use_retained_scheduling_info=1
use_syslog=0
log_notifications=1
log_service_retries=1
log_host_retries=1
log_event_handlers=1
log_initial_states=1
log_external_commands=1
log_passive_checks=1
sleep_time=0.25
service_inter_check_delay_method=s
max_service_check_spread=30
service_interleave_factor=s
max_concurrent_checks=0
check_result_path=@@DIR@@/var/spool/checkresults
max_check_result_file_age=3600
host_inter_check_delay_method=s
max_host_check_spread=30
interval_length=15
auto_reschedule_checks=0
auto_rescheduling_interval=30
auto_rescheduling_window=180
use_aggressive_host_checking=0
translate_passive_host_checks=0
passive_host_checks_are_soft=0
enable_predictive_host_dependency_checks=1
enable_predictive_service_dependency_checks=1
cached_host_check_horizon=15
cached_service_check_horizon=15
use_large_installation_tweaks=1
free_child_process_memory=0
child_processes_fork_twice=0
enable_environment_macros=0
enable_flap_detection=1
low_service_flap_threshold=5.0
high_service_flap_threshold=20.0
low_host_flap_threshold=5.0
high_host_flap_threshold=20.0
service_check_timeout=60
host_check_timeout=60
event_handler_timeout=60
notification_timeout=60
ocsp_timeout=5
perfdata_timeout=5
obsess_over_services=0
obsess_over_hosts=0
process_performance_data=1
check_for_orphaned_services=1
check_for_orphaned_hosts=1
check_service_freshness=1
service_freshness_check_interval=60
check_host_freshness=1
host_freshness_check_interval=60
date_format=iso8601
illegal_object_name_chars=`~!$%^&*|'\"<>?,()=
illegal_macro_output_chars=`~$&|'\"<>
use_regexp_matching=0
use_true_regexp_matching=0
admin_email=support@op5.com
admin_pager=support@op5.com
event_broker_options=-1
debug_file=@@DIR@@/var/nagios.debug
debug_level=-1
debug_verbosity=1
max_debug_file_size=104857600
daemon_dumps_core=1
"""

	merlin_config_in = """ipc_socket = @@DIR@@/merlin/ipc.sock;

log_level = debug

module {
	log_file = @@DIR@@/neb.log;
}

daemon {
	pidfile = @@DIR@@/merlin/merlind.pid;
	log_file = @@DIR@@/daemon.log;
	import_program = @@OCIMP_PATH@@ --force
	port = @@NETWORK_PORT@@;
	database {
		name = @@DB_NAME@@;
		user = merlin;
		pass = merlin;
		host = localhost;
		type = mysql;
		commit_interval = 3
		commit_queries = 2000
	}
}
#NODECONFIG
"""
	shared_object_config = """
define timeperiod{
    timeperiod_name                24x7
    alias                          24 Hours A Day, 7 Days A Week
    monday                         00:00-24:00
    tuesday                        00:00-24:00
    wednesday                      00:00-24:00
    thursday                       00:00-24:00
    friday                         00:00-24:00
    saturday                       00:00-24:00
    sunday                         00:00-24:00
    }
define timeperiod{
    timeperiod_name                none
    alias                          No Time Is A Good Time
    }
define command{
    command_name                   mon_check_random
    command_line                   /usr/bin/mon check random
    }
define command{
    command_name                   mon_notify
    command_line                   /bin/echo Notifying '$CONTACTNAME$' of '$PROBLEMTYPE$' on '$HOSTNAME$' '$SERVICEDESCRIPTION$' >> /tmp/merlin-dtest/sent-notifications
    }
define command{
    command_name                   host-notify
    command_line                   /bin/echo -c '$CONTACTNAME$' -h '$HOSTNAME$' -f '$NOTIFICATIONTYPE$' -m '$CONTACTEMAIL$' -p '$CONTACTPAGER$' 'HOSTNAME=$HOSTNAME$' 'HOSTDISPLAYNAME=$HOSTDISPLAYNAME$' 'HOSTALIAS=$HOSTALIAS$' 'HOSTADDRESS=$HOSTADDRESS$' 'HOSTSTATE=$HOSTSTATE$' 'HOSTSTATEID=$HOSTSTATEID$' 'LASTHOSTSTATE=$LASTHOSTSTATE$' 'LASTHOSTSTATEID=$LASTHOSTSTATEID$' 'HOSTSTATETYPE=$HOSTSTATETYPE$' 'HOSTATTEMPT=$HOSTATTEMPT$' 'MAXHOSTATTEMPTS=$MAXHOSTATTEMPTS$' 'HOSTEVENTID=$HOSTEVENTID$' 'LASTHOSTEVENTID=$LASTHOSTEVENTID$' 'HOSTPROBLEMID=$HOSTPROBLEMID$' 'LASTHOSTPROBLEMID=$LASTHOSTPROBLEMID$' 'HOSTLATENCY=$HOSTLATENCY$' 'HOSTEXECUTIONTIME=$HOSTEXECUTIONTIME$' 'HOSTDURATION=$HOSTDURATION$' 'HOSTDURATIONSEC=$HOSTDURATIONSEC$' 'HOSTDOWNTIME=$HOSTDOWNTIME$' 'HOSTPERCENTCHANGE=$HOSTPERCENTCHANGE$' 'HOSTGROUPNAME=$HOSTGROUPNAME$' 'HOSTGROUPNAMES=$HOSTGROUPNAMES$' 'LASTHOSTCHECK=$LASTHOSTCHECK$' 'LASTHOSTSTATECHANGE=$LASTHOSTSTATECHANGE$' 'LASTHOSTUP=$LASTHOSTUP$' 'LASTHOSTDOWN=$LASTHOSTDOWN$' 'LASTHOSTUNREACHABLE=$LASTHOSTUNREACHABLE$' 'HOSTOUTPUT=$HOSTOUTPUT$' 'LONGHOSTOUTPUT=$LONGHOSTOUTPUT$' 'HOSTPERFDATA=$HOSTPERFDATA$' 'HOSTCHECKCOMMAND=$HOSTCHECKCOMMAND$' 'HOSTACKAUTHOR=$HOSTACKAUTHOR$' 'HOSTACKAUTHORNAME=$HOSTACKAUTHORNAME$' 'HOSTACKAUTHORALIAS=$HOSTACKAUTHORALIAS$' 'HOSTACKCOMMENT=$HOSTACKCOMMENT$' 'HOSTACTIONURL=$HOSTACTIONURL$' 'HOSTNOTESURL=$HOSTNOTESURL$' 'HOSTNOTES=$HOSTNOTES$' 'TOTALHOSTSERVICES=$TOTALHOSTSERVICES$' 'TOTALHOSTSERVICESOK=$TOTALHOSTSERVICESOK$' 'TOTALHOSTSERVICESWARNING=$TOTALHOSTSERVICESWARNING$' 'TOTALHOSTSERVICESUNKNOWN=$TOTALHOSTSERVICESUNKNOWN$' 'TOTALHOSTSERVICESCRITICAL=$TOTALHOSTSERVICESCRITICAL$' 'HOSTGROUPALIAS=$HOSTGROUPALIAS$' 'HOSTGROUPNOTES=$HOSTGROUPNOTES$' 'HOSTGROUPNOTESURL=$HOSTGROUPNOTESURL$' 'HOSTGROUPACTIONURL=$HOSTGROUPACTIONURL$' 'SERVICEGROUPALIAS=$SERVICEGROUPALIAS$' 'SERVICEGROUPNOTES=$SERVICEGROUPNOTES$' 'SERVICEGROUPNOTESURL=$SERVICEGROUPNOTESURL$' 'SERVICEGROUPACTIONURL=$SERVICEGROUPACTIONURL$' 'CONTACTNAME=$CONTACTNAME$' 'CONTACTALIAS=$CONTACTALIAS$' 'CONTACTEMAIL=$CONTACTEMAIL$' 'CONTACTPAGER=$CONTACTPAGER$' 'CONTACTADDRESSn=$CONTACTADDRESSn$' 'CONTACTGROUPALIAS=$CONTACTGROUPALIAS$' 'CONTACTGROUPMEMBERS=$CONTACTGROUPMEMBERS$' 'TOTALHOSTSUP=$TOTALHOSTSUP$' 'TOTALHOSTSDOWN=$TOTALHOSTSDOWN$' 'TOTALHOSTSUNREACHABLE=$TOTALHOSTSUNREACHABLE$' 'TOTALHOSTSDOWNUNHANDLED=$TOTALHOSTSDOWNUNHANDLED$' 'TOTALHOSTSUNREACHABLEUNHANDLED=$TOTALHOSTSUNREACHABLEUNHANDLED$' 'TOTALHOSTPROBLEMS=$TOTALHOSTPROBLEMS$' 'TOTALHOSTPROBLEMSUNHANDLED=$TOTALHOSTPROBLEMSUNHANDLED$' 'TOTALSERVICESOK=$TOTALSERVICESOK$' 'TOTALSERVICESWARNING=$TOTALSERVICESWARNING$' 'TOTALSERVICESCRITICAL=$TOTALSERVICESCRITICAL$' 'TOTALSERVICESUNKNOWN=$TOTALSERVICESUNKNOWN$' 'TOTALSERVICESWARNINGUNHANDLED=$TOTALSERVICESWARNINGUNHANDLED$' 'TOTALSERVICESCRITICALUNHANDLED=$TOTALSERVICESCRITICALUNHANDLED$' 'TOTALSERVICESUNKNOWNUNHANDLED=$TOTALSERVICESUNKNOWNUNHANDLED$' 'TOTALSERVICEPROBLEMS=$TOTALSERVICEPROBLEMS$' 'TOTALSERVICEPROBLEMSUNHANDLED=$TOTALSERVICEPROBLEMSUNHANDLED$' 'NOTIFICATIONTYPE=$NOTIFICATIONTYPE$' 'NOTIFICATIONRECIPIENTS=$NOTIFICATIONRECIPIENTS$' 'NOTIFICATIONISESCALATED=$NOTIFICATIONISESCALATED$' 'NOTIFICATIONAUTHOR=$NOTIFICATIONAUTHOR$' 'NOTIFICATIONAUTHORNAME=$NOTIFICATIONAUTHORNAME$' 'NOTIFICATIONAUTHORALIAS=$NOTIFICATIONAUTHORALIAS$' 'NOTIFICATIONCOMMENT=$NOTIFICATIONCOMMENT$' 'HOSTNOTIFICATIONNUMBER=$HOSTNOTIFICATIONNUMBER$' 'HOSTNOTIFICATIONID=$HOSTNOTIFICATIONID$' 'SERVICENOTIFICATIONNUMBER=$SERVICENOTIFICATIONNUMBER$' 'SERVICENOTIFICATIONID=$SERVICENOTIFICATIONID$' 'LONGDATETIME=$LONGDATETIME$' 'SHORTDATETIME=$SHORTDATETIME$' 'DATE=$DATE$' 'TIME=$TIME$' 'TIMET=$TIMET$' 'MAINCONFIGFILE=$MAINCONFIGFILE$' 'STATUSDATAFILE=$STATUSDATAFILE$' 'COMMENTDATAFILE=$COMMENTDATAFILE$' 'DOWNTIMEDATAFILE=$DOWNTIMEDATAFILE$' 'RETENTIONDATAFILE=$RETENTIONDATAFILE$' 'OBJECTCACHEFILE=$OBJECTCACHEFILE$' 'TEMPFILE=$TEMPFILE$' 'TEMPPATH=$TEMPPATH$' 'LOGFILE=$LOGFILE$' 'RESOURCEFILE=$RESOURCEFILE$' 'COMMANDFILE=$COMMANDFILE$' 'HOSTPERFDATAFILE=$HOSTPERFDATAFILE$' 'SERVICEPERFDATAFILE=$SERVICEPERFDATAFILE$' 'PROCESSSTARTTIME=$PROCESSSTARTTIME$' 'EVENTSTARTTIME=$EVENTSTARTTIME$' 'ADMINEMAIL=$ADMINEMAIL$' 'ADMINPAGER=$ADMINPAGER$' 'ARG1=$ARG1$' 'ARG2=$ARG2$' 'ARG3=$ARG3$' 'ARG4=$ARG4$' 'ARG5=$ARG5$' 'ARG6=$ARG6$' 'ARG7=$ARG7$' 'ARG8=$ARG8$' 'ARG9=$ARG9$' 'ARG10=$ARG10$' 'ARG11=$ARG11$' 'ARG12=$ARG12$' 'ARG13=$ARG13$' 'ARG14=$ARG14$' 'ARG15=$ARG15$' 'ARG16=$ARG16$' 'ARG17=$ARG17$' 'ARG18=$ARG18$' 'ARG19=$ARG19$' 'ARG20=$ARG20$' 'ARG21=$ARG21$' 'ARG22=$ARG22$' 'ARG23=$ARG23$' 'ARG24=$ARG24$' 'ARG25=$ARG25$' 'ARG26=$ARG26$' 'ARG27=$ARG27$' 'ARG28=$ARG28$' 'ARG29=$ARG29$' 'ARG30=$ARG30$' 'ARG31=$ARG31$' 'ARG32=$ARG32$' 'USER1=$USER1$' 'USER2=$USER2$' 'USER3=$USER3$' 'USER4=$USER4$' 'USER5=$USER5$' 'USER6=$USER6$' 'USER7=$USER7$' 'USER8=$USER8$' 'USER9=$USER9$' 'USER10=$USER10$' 'USER11=$USER11$' 'USER12=$USER12$' 'USER13=$USER13$' 'USER14=$USER14$' 'USER15=$USER15$' 'USER16=$USER16$' 'USER17=$USER17$' 'USER18=$USER18$' 'USER19=$USER19$' 'USER20=$USER20$' 'USER21=$USER21$' 'USER22=$USER22$' 'USER23=$USER23$' 'USER24=$USER24$' 'USER25=$USER25$' 'USER26=$USER26$' 'USER27=$USER27$' 'USER28=$USER28$' 'USER29=$USER29$' 'USER30=$USER30$' 'USER31=$USER31$' 'USER32=$USER32$'
    }
define command{
    command_name                   service-notify
    command_line                   /bin/echo -c '$CONTACTNAME$' -h '$HOSTNAME$' -f '$NOTIFICATIONTYPE$' -m '$CONTACTEMAIL$' -p '$CONTACTPAGER$' -s '$SERVICEDESC$' 'HOSTNAME=$HOSTNAME$' 'HOSTDISPLAYNAME=$HOSTDISPLAYNAME$' 'HOSTALIAS=$HOSTALIAS$' 'HOSTADDRESS=$HOSTADDRESS$' 'HOSTSTATE=$HOSTSTATE$' 'HOSTSTATEID=$HOSTSTATEID$' 'LASTHOSTSTATE=$LASTHOSTSTATE$' 'LASTHOSTSTATEID=$LASTHOSTSTATEID$' 'HOSTSTATETYPE=$HOSTSTATETYPE$' 'HOSTATTEMPT=$HOSTATTEMPT$' 'MAXHOSTATTEMPTS=$MAXHOSTATTEMPTS$' 'HOSTEVENTID=$HOSTEVENTID$' 'LASTHOSTEVENTID=$LASTHOSTEVENTID$' 'HOSTPROBLEMID=$HOSTPROBLEMID$' 'LASTHOSTPROBLEMID=$LASTHOSTPROBLEMID$' 'HOSTLATENCY=$HOSTLATENCY$' 'HOSTEXECUTIONTIME=$HOSTEXECUTIONTIME$' 'HOSTDURATION=$HOSTDURATION$' 'HOSTDURATIONSEC=$HOSTDURATIONSEC$' 'HOSTDOWNTIME=$HOSTDOWNTIME$' 'HOSTPERCENTCHANGE=$HOSTPERCENTCHANGE$' 'HOSTGROUPNAME=$HOSTGROUPNAME$' 'HOSTGROUPNAMES=$HOSTGROUPNAMES$' 'LASTHOSTCHECK=$LASTHOSTCHECK$' 'LASTHOSTSTATECHANGE=$LASTHOSTSTATECHANGE$' 'LASTHOSTUP=$LASTHOSTUP$' 'LASTHOSTDOWN=$LASTHOSTDOWN$' 'LASTHOSTUNREACHABLE=$LASTHOSTUNREACHABLE$' 'HOSTOUTPUT=$HOSTOUTPUT$' 'LONGHOSTOUTPUT=$LONGHOSTOUTPUT$' 'HOSTPERFDATA=$HOSTPERFDATA$' 'HOSTCHECKCOMMAND=$HOSTCHECKCOMMAND$' 'HOSTACTIONURL=$HOSTACTIONURL$' 'HOSTNOTESURL=$HOSTNOTESURL$' 'HOSTNOTES=$HOSTNOTES$' 'TOTALHOSTSERVICES=$TOTALHOSTSERVICES$' 'TOTALHOSTSERVICESOK=$TOTALHOSTSERVICESOK$' 'TOTALHOSTSERVICESWARNING=$TOTALHOSTSERVICESWARNING$' 'TOTALHOSTSERVICESUNKNOWN=$TOTALHOSTSERVICESUNKNOWN$' 'TOTALHOSTSERVICESCRITICAL=$TOTALHOSTSERVICESCRITICAL$' 'HOSTGROUPALIAS=$HOSTGROUPALIAS$' 'HOSTGROUPNOTES=$HOSTGROUPNOTES$' 'HOSTGROUPNOTESURL=$HOSTGROUPNOTESURL$' 'HOSTGROUPACTIONURL=$HOSTGROUPACTIONURL$' 'SERVICEDESC=$SERVICEDESC$' 'SERVICEDISPLAYNAME=$SERVICEDISPLAYNAME$' 'SERVICESTATE=$SERVICESTATE$' 'SERVICESTATEID=$SERVICESTATEID$' 'LASTSERVICESTATE=$LASTSERVICESTATE$' 'LASTSERVICESTATEID=$LASTSERVICESTATEID$' 'SERVICESTATETYPE=$SERVICESTATETYPE$' 'SERVICEATTEMPT=$SERVICEATTEMPT$' 'MAXSERVICEATTEMPTS=$MAXSERVICEATTEMPTS$' 'SERVICEISVOLATILE=$SERVICEISVOLATILE$' 'SERVICEEVENTID=$SERVICEEVENTID$' 'LASTSERVICEEVENTID=$LASTSERVICEEVENTID$' 'SERVICEPROBLEMID=$SERVICEPROBLEMID$' 'LASTSERVICEPROBLEMID=$LASTSERVICEPROBLEMID$' 'SERVICELATENCY=$SERVICELATENCY$' 'SERVICEEXECUTIONTIME=$SERVICEEXECUTIONTIME$' 'SERVICEDURATION=$SERVICEDURATION$' 'SERVICEDURATIONSEC=$SERVICEDURATIONSEC$' 'SERVICEDOWNTIME=$SERVICEDOWNTIME$' 'SERVICEPERCENTCHANGE=$SERVICEPERCENTCHANGE$' 'SERVICEGROUPNAME=$SERVICEGROUPNAME$' 'SERVICEGROUPNAMES=$SERVICEGROUPNAMES$' 'LASTSERVICECHECK=$LASTSERVICECHECK$' 'LASTSERVICESTATECHANGE=$LASTSERVICESTATECHANGE$' 'LASTSERVICEOK=$LASTSERVICEOK$' 'LASTSERVICEWARNING=$LASTSERVICEWARNING$' 'LASTSERVICEUNKNOWN=$LASTSERVICEUNKNOWN$' 'LASTSERVICECRITICAL=$LASTSERVICECRITICAL$' 'SERVICEOUTPUT=$SERVICEOUTPUT$' 'LONGSERVICEOUTPUT=$LONGSERVICEOUTPUT$' 'SERVICEPERFDATA=$SERVICEPERFDATA$' 'SERVICECHECKCOMMAND=$SERVICECHECKCOMMAND$' 'SERVICEACKAUTHOR=$SERVICEACKAUTHOR$' '8=$8$' 'SERVICEACKAUTHORNAME=$SERVICEACKAUTHORNAME$' '8=$8$' 'SERVICEACKAUTHORALIAS=$SERVICEACKAUTHORALIAS$' '8=$8$' 'SERVICEACKCOMMENT=$SERVICEACKCOMMENT$' '8=$8$' 'SERVICEACTIONURL=$SERVICEACTIONURL$' 'SERVICENOTESURL=$SERVICENOTESURL$' 'SERVICENOTES=$SERVICENOTES$' 'SERVICEGROUPALIAS=$SERVICEGROUPALIAS$' 'SERVICEGROUPNOTES=$SERVICEGROUPNOTES$' 'SERVICEGROUPNOTESURL=$SERVICEGROUPNOTESURL$' 'SERVICEGROUPACTIONURL=$SERVICEGROUPACTIONURL$' 'CONTACTNAME=$CONTACTNAME$' 'CONTACTALIAS=$CONTACTALIAS$' 'CONTACTEMAIL=$CONTACTEMAIL$' 'CONTACTPAGER=$CONTACTPAGER$' 'CONTACTADDRESSn=$CONTACTADDRESSn$' 'CONTACTGROUPALIAS=$CONTACTGROUPALIAS$' 'CONTACTGROUPMEMBERS=$CONTACTGROUPMEMBERS$' 'TOTALHOSTSUP=$TOTALHOSTSUP$' 'TOTALHOSTSDOWN=$TOTALHOSTSDOWN$' 'TOTALHOSTSUNREACHABLE=$TOTALHOSTSUNREACHABLE$' 'TOTALHOSTSDOWNUNHANDLED=$TOTALHOSTSDOWNUNHANDLED$' 'TOTALHOSTSUNREACHABLEUNHANDLED=$TOTALHOSTSUNREACHABLEUNHANDLED$' 'TOTALHOSTPROBLEMS=$TOTALHOSTPROBLEMS$' 'TOTALHOSTPROBLEMSUNHANDLED=$TOTALHOSTPROBLEMSUNHANDLED$' 'TOTALSERVICESOK=$TOTALSERVICESOK$' 'TOTALSERVICESWARNING=$TOTALSERVICESWARNING$' 'TOTALSERVICESCRITICAL=$TOTALSERVICESCRITICAL$' 'TOTALSERVICESUNKNOWN=$TOTALSERVICESUNKNOWN$' 'TOTALSERVICESWARNINGUNHANDLED=$TOTALSERVICESWARNINGUNHANDLED$' 'TOTALSERVICESCRITICALUNHANDLED=$TOTALSERVICESCRITICALUNHANDLED$' 'TOTALSERVICESUNKNOWNUNHANDLED=$TOTALSERVICESUNKNOWNUNHANDLED$' 'TOTALSERVICEPROBLEMS=$TOTALSERVICEPROBLEMS$' 'TOTALSERVICEPROBLEMSUNHANDLED=$TOTALSERVICEPROBLEMSUNHANDLED$' 'NOTIFICATIONTYPE=$NOTIFICATIONTYPE$' 'NOTIFICATIONRECIPIENTS=$NOTIFICATIONRECIPIENTS$' 'NOTIFICATIONISESCALATED=$NOTIFICATIONISESCALATED$' 'NOTIFICATIONAUTHOR=$NOTIFICATIONAUTHOR$' 'NOTIFICATIONAUTHORNAME=$NOTIFICATIONAUTHORNAME$' 'NOTIFICATIONAUTHORALIAS=$NOTIFICATIONAUTHORALIAS$' 'NOTIFICATIONCOMMENT=$NOTIFICATIONCOMMENT$' 'HOSTNOTIFICATIONNUMBER=$HOSTNOTIFICATIONNUMBER$' 'HOSTNOTIFICATIONID=$HOSTNOTIFICATIONID$' 'SERVICENOTIFICATIONNUMBER=$SERVICENOTIFICATIONNUMBER$' 'SERVICENOTIFICATIONID=$SERVICENOTIFICATIONID$' 'LONGDATETIME=$LONGDATETIME$' 'SHORTDATETIME=$SHORTDATETIME$' 'DATE=$DATE$' 'TIME=$TIME$' 'TIMET=$TIMET$' 'MAINCONFIGFILE=$MAINCONFIGFILE$' 'STATUSDATAFILE=$STATUSDATAFILE$' 'COMMENTDATAFILE=$COMMENTDATAFILE$' 'DOWNTIMEDATAFILE=$DOWNTIMEDATAFILE$' 'RETENTIONDATAFILE=$RETENTIONDATAFILE$' 'OBJECTCACHEFILE=$OBJECTCACHEFILE$' 'TEMPFILE=$TEMPFILE$' 'TEMPPATH=$TEMPPATH$' 'LOGFILE=$LOGFILE$' 'RESOURCEFILE=$RESOURCEFILE$' 'COMMANDFILE=$COMMANDFILE$' 'HOSTPERFDATAFILE=$HOSTPERFDATAFILE$' 'SERVICEPERFDATAFILE=$SERVICEPERFDATAFILE$' 'PROCESSSTARTTIME=$PROCESSSTARTTIME$' 'EVENTSTARTTIME=$EVENTSTARTTIME$' 'ADMINEMAIL=$ADMINEMAIL$' 'ADMINPAGER=$ADMINPAGER$' 'ARG1=$ARG1$' 'ARG2=$ARG2$' 'ARG3=$ARG3$' 'ARG4=$ARG4$' 'ARG5=$ARG5$' 'ARG6=$ARG6$' 'ARG7=$ARG7$' 'ARG8=$ARG8$' 'ARG9=$ARG9$' 'ARG10=$ARG10$' 'ARG11=$ARG11$' 'ARG12=$ARG12$' 'ARG13=$ARG13$' 'ARG14=$ARG14$' 'ARG15=$ARG15$' 'ARG16=$ARG16$' 'ARG17=$ARG17$' 'ARG18=$ARG18$' 'ARG19=$ARG19$' 'ARG20=$ARG20$' 'ARG21=$ARG21$' 'ARG22=$ARG22$' 'ARG23=$ARG23$' 'ARG24=$ARG24$' 'ARG25=$ARG25$' 'ARG26=$ARG26$' 'ARG27=$ARG27$' 'ARG28=$ARG28$' 'ARG29=$ARG29$' 'ARG30=$ARG30$' 'ARG31=$ARG31$' 'ARG32=$ARG32$' 'USER1=$USER1$' 'USER2=$USER2$' 'USER3=$USER3$' 'USER4=$USER4$' 'USER5=$USER5$' 'USER6=$USER6$' 'USER7=$USER7$' 'USER8=$USER8$' 'USER9=$USER9$' 'USER10=$USER10$' 'USER11=$USER11$' 'USER12=$USER12$' 'USER13=$USER13$' 'USER14=$USER14$' 'USER15=$USER15$' 'USER16=$USER16$' 'USER17=$USER17$' 'USER18=$USER18$' 'USER19=$USER19$' 'USER20=$USER20$' 'USER21=$USER21$' 'USER22=$USER22$' 'USER23=$USER23$' 'USER24=$USER24$' 'USER25=$USER25$' 'USER26=$USER26$' 'USER27=$USER27$' 'USER28=$USER28$' 'USER29=$USER29$' 'USER30=$USER30$' 'USER31=$USER31$' 'USER32=$USER32$'
    }
define command{
    command_name                   process-service-perfdata
    command_line                   /usr/bin/mon test _process-perfdata
    }
define contact{
    name                           default-contact
    host_notifications_enabled     1
    service_notifications_enabled  1
    host_notification_period       24x7
    service_notification_period    24x7
    host_notification_options      d,r
    service_notification_options   c,w,r
    host_notification_commands     host-notify
    service_notification_commands  service-notify
    can_submit_commands            1
    retain_status_information      1
    retain_nonstatus_information   1
    contactgroups                  support-group
    register                       0
    }
define host{
    name                           default-host-template
    check_command                  check-host-alive
    max_check_attempts             3
    check_interval                 1
    retry_interval                 0
    active_checks_enabled          1
    passive_checks_enabled         1
    check_period                   24x7
    event_handler_enabled          1
    flap_detection_enabled         1
    process_perf_data              1
    retain_status_information      1
    retain_nonstatus_information   1
    notification_interval          0
    notification_period            24x7
    notification_options           d,u,r,f,s
    notifications_enabled          1
    retry_interval                 0
    contact_groups                 support-group
    check_command                  mon_check_random
    register                       0
}
define service{
    name                           default-service
    is_volatile                    0
    max_check_attempts             3
    check_interval                 2
    retry_interval                 1
    active_checks_enabled          1
    passive_checks_enabled         1
    check_period                   24x7
    event_handler_enabled          1
    flap_detection_enabled         1
    process_perf_data              1
    retain_status_information      1
    retain_nonstatus_information   1
    notification_interval          0
    notification_period            24x7
    notification_options           c,w,u,r,f,s
    notifications_enabled          1
    contact_groups                 support-group
    check_command                  mon_check_random
    register                       0
    }
define contactgroup{
    contactgroup_name              support-group
    alias                          Support Contact Group
    }
define contact{
    use                            default-contact
    contact_name                   monitor
    alias                          Monitor Admin
    email                          none@example.com
    }
define contact{
    use                            default-contact
    contact_name                   ae
    alias                          High Lord Hacker
    email                          none@example.com
    }
define hostgroup{
    hostgroup_name                 host1_hosts
    alias                          The first host in each group
    }
define hostgroup{
    hostgroup_name                 host2_hosts
    alias                          The second host in each group
    }
define hostgroup{
    hostgroup_name                 host3_hosts
    alias                          The third host in each group
    }
define hostgroup{
    hostgroup_name                 host4_hosts
    alias                          The fourth host in each group
    }
define hostgroup{
    hostgroup_name                 host5_hosts
    alias                          The fifth host in each group
    }
define hostgroup{
    hostgroup_name                 host6_hosts
    alias                          The sixth host in each group
    }
define hostgroup{
    hostgroup_name                 host7_hosts
    alias                          The seventh host in each group
    }
define servicegroup{
    servicegroup_name            service1_services
    alias                        The first service on each host
}
define servicegroup{
    servicegroup_name            service2_services
    alias                        The second service on each host
}
define servicegroup{
    servicegroup_name            service3_services
    alias                        The third service on each host
}
define servicegroup{
    servicegroup_name            service4_services
    alias                        The fourth service on each host
}
define servicegroup{
    servicegroup_name            service5_services
    alias                        The fifth service on each host
}
define servicegroup{
    servicegroup_name            service6_services
    alias                        The sixth service on each host
}
define servicegroup{
    servicegroup_name            service7_services
    alias                        The seventh service on each host
}
"""
