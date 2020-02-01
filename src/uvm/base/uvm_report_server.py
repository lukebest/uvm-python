
from cocotb.utils import get_sim_time

from .uvm_object import UVMObject
from .uvm_object_globals import *
from .uvm_globals import *
from .uvm_pool import UVMPool
from .uvm_report_catcher import UVMReportCatcher
from .uvm_global_vars import uvm_default_printer
from .sv import sv



# TODO
def ename(sever):
    if isinstance(sever, str):
        raise Exception("str was given to ename(). Expected int. Got: " + sever)
    if sever == UVM_INFO:
        return "UVM_INFO"
    if sever == UVM_ERROR:
        return "UVM_ERROR"
    if sever == UVM_FATAL:
        return "UVM_FATAL"
    if sever == UVM_WARNING:
        return "UVM_WARNING"
    return "UNKNOWN_SEVERITY: {}".format(sever)

#------------------------------------------------------------------------------
# Title: UVM Report Server
#
# This page covers the classes that define the UVM report server facility.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#
# CLASS: uvm_report_server
#
# uvm_report_server is a global server that processes all of the reports
# generated by a uvm_report_handler.
#
# The ~uvm_report_server~ is an abstract class which declares many of its methods
# as ~pure virtual~.  The UVM uses the <uvm_default_report_server> class
# as its default report server implementation.
#------------------------------------------------------------------------------


class UVMReportServer(UVMObject):

    def __init__(self, name="base"):
        UVMObject.__init__(self, name)
        self.m_quit_count = 0
        self.m_max_quit_count = 0
        self.max_quit_overridable = True
        self.m_severity_count = UVMPool()
        self.m_id_count = UVMPool()

        self.enable_report_id_count_summary = True
        self.record_all_messages = False
        self.show_verbosity = False
        self.show_terminator = False

        self.m_message_db = {}  # uvm_tr_database
        self.m_streams = {}
        self.reset_quit_count()
        self.reset_severity_counts()
        self.set_max_quit_count(0)

    def get_type_name(self):
        return "uvm_report_server"

    @classmethod
    def set_server(cls, server):
        cs = get_cs()
        #server.copy(cs.get_report_server())
        cs.set_report_server(server)

    @classmethod
    def get_server(cls):
        cs = get_cs()
        return cs.get_report_server()

    # Function: print
    #
    # The uvm_report_server implements the <uvm_object::do_print()> such that
    # ~print~ method provides UVM printer formatted output
    # of the current configuration.    A snippet of example output is shown here:
    #

    # Print to show report server state
    def do_print(self, printer):
        l_severity_count_index = 0
        l_id_count_index = ""

        printer.print_int("quit_count", self.m_quit_count, sv.bits(self.m_quit_count), UVM_DEC,
            ".", "int")
        printer.print_int("max_quit_count", self.m_max_quit_count,
            sv.bits(self.m_max_quit_count), UVM_DEC, ".", "int")
        printer.print_int("max_quit_overridable", self.max_quit_overridable,
            sv.bits(self.max_quit_overridable), UVM_BIN, ".", "bit")

        if self.m_severity_count.has_first():
            l_severity_count_index = self.m_severity_count.first()
            printer.print_array_header("severity_count",self.m_severity_count.size(),"severity counts")
            ok = True
            while ok:
                printer.print_int("".formatf("[{}]",
                    ename(l_severity_count_index)),
                    self.m_severity_count[l_severity_count_index], 32, UVM_DEC)
                ok = self.m_severity_count.has_next()
                if ok:
                    l_severity_count_index = self.m_severity_count.next()
            printer.print_array_footer()

        if self.m_id_count.has_first():
            l_id_count_index = self.m_id_count.first()
            printer.print_array_header("id_count",self.m_id_count.size(),"id counts")
            ok = True
            while ok:
                printer.print_int("".format("[{}]",l_id_count_index),
                    self.m_id_count[l_id_count_index], 32, UVM_DEC)
                ok = self.m_id_count.has_next()
                if ok:
                    l_id_count_index = self.m_id_count.next()
            printer.print_array_footer()

        printer.print_int("enable_report_id_count_summary", self.enable_report_id_count_summary,
            sv.bits(self.enable_report_id_count_summary), UVM_BIN, ".", "bit")
        printer.print_int("record_all_messages", self.record_all_messages,
            sv.bits(self.record_all_messages), UVM_BIN, ".", "bit")
        printer.print_int("show_verbosity", self.show_verbosity,
            sv.bits(self.show_verbosity), UVM_BIN, ".", "bit")
        printer.print_int("show_terminator", self.show_terminator,
            sv.bits(self.show_terminator), UVM_BIN, ".", "bit")

    #----------------------------------------------------------------------------
    # Group: Quit Count
    #----------------------------------------------------------------------------

    # Function: get_max_quit_count
    def get_max_quit_count(self):
        return self.m_max_quit_count

    # Function: set_max_quit_count
    #
    # Get or set the maximum number of COUNT actions that can be tolerated
    # before a UVM_EXIT action is taken. The default is 0, which specifies
    # no maximum.

    def set_max_quit_count(self, count, overridable=True):
        if self.max_quit_overridable is False:
            uvm_report_info("NOMAXQUITOVR",
                "".format("The max quit count setting of {} is not overridable to {} due to a previous setting.",
                self.m_max_quit_count, count), UVM_NONE)
            return
        self.max_quit_overridable = overridable
        if count < 0:
            self.m_max_quit_count = 0
        else:
            self.m_max_quit_count = count

    # Function: get_quit_count
    def get_quit_count(self):
        return self.m_quit_count

    # Function: set_quit_count
    def set_quit_count(self, quit_count):
        if quit_count < 0:
            self.m_quit_count = 0
        else:
            self.m_quit_count = quit_count

    # Function: incr_quit_count
    def incr_quit_count(self):
        self.m_quit_count += 1

    # Function: reset_quit_count
    #
    # Set, get, increment, or reset to 0 the quit count, i.e., the number of
    # COUNT actions issued.
    def reset_quit_count(self):
        self.m_quit_count = 0

    # Function: is_quit_count_reached
    #
    # If is_quit_count_reached returns 1, then the quit counter has reached
    # the maximum.
    def is_quit_count_reached(self):
        return self.m_quit_count >= self.m_max_quit_count

    #----------------------------------------------------------------------------
    # Group: Severity Count
    #----------------------------------------------------------------------------

    # Function: get_severity_count
    def get_severity_count(self, severity):
        if self.m_severity_count.exists(severity):
            return self.m_severity_count.get(severity)
        return 0

    # Function: set_severity_count

    def set_severity_count(self, severity, count):
        val = count
        if count < 0:
            val = 0
        self.m_severity_count.add(severity, val)

    # Function: incr_severity_count

    def incr_severity_count(self, severity):
        if self.m_severity_count.exists(severity):
            new_count = self.m_severity_count.get(severity) + 1
            self.m_severity_count.add(severity, new_count)
        else:
            self.m_severity_count.add(severity, 1)

    # Function: reset_severity_counts
    #
    # Set, get, or increment the counter for the given severity, or reset
    # all severity counters to 0.

    def reset_severity_counts(self):
        for s in UVM_SEVERITY_LEVELS:
            self.m_severity_count.add(s, 0)

    #----------------------------------------------------------------------------
    # Group: id Count
    #----------------------------------------------------------------------------

    # Function: get_id_count

    def get_id_count(self, id):
        if self.m_id_count.exists(id):
            return self.m_id_count.get(id)
        return 0

    # Function: set_id_count

    def set_id_count(self, id, count):
        val = count
        if count < 0:
            val = 0
        self.m_id_count.add(id, val)

    # Function: incr_id_count
    #
    # Set, get, or increment the counter for reports with the given id.

    def incr_id_count(self, id):
        if self.m_id_count.exists(id):
            val = self.m_id_count.get(id)
            self.m_id_count.add(id, val + 1)
        else:
            self.m_id_count.add(id, 1)

    #----------------------------------------------------------------------------
    # Group: message recording
    #
    # The ~uvm_default_report_server~ will record messages into the message
    # database, using one transaction per message, and one stream per report
    # object/handler pair.
    #
    #----------------------------------------------------------------------------

    # Function: set_message_database
    # sets the <uvm_tr_database> used for recording messages
    def set_message_database(self, database):
        self.m_message_db = database

    # Function: get_message_database
    # returns the <uvm_tr_database> used for recording messages
    #
    def get_message_database(self):
        return self.m_message_db

    def get_severity_set(self, q):
        while self.m_severity_count.has_next():
            q.append(self.m_severity_count.next())

    def get_id_set(self, q):
        while self.m_id_count.has_next():
            q.append(self.m_id_count.next())

    # Function- f_display
    #
    # This method sends string severity to the command line if file is 0 and to
    # the file(s) specified by file if it is not 0.
    def f_display(self, file, _str):
        if file == 0:
            #import logging
            #logging.info("%s", str)
            print("%s\n", _str)
        else:
            file.write(_str + "\n")

    def process_report_message(self, report_message):
        l_report_handler = report_message.get_report_handler()
        #process p = process::self()
        report_ok = True

        # Set the report server for this message
        report_message.set_report_server(self)

        if report_ok is True:
            report_ok = UVMReportCatcher.process_all_report_catchers(report_message)

        if report_message.get_action() == UVM_NO_ACTION:
            report_ok = False

        if report_ok is True:
            m = ""
            cs = get_cs()
            # give the global server a chance to intercept the calls
            svr = cs.get_report_server()

            # no need to compose when neither UVM_DISPLAY nor UVM_LOG is set
            if report_message.get_action() & (UVM_LOG | UVM_DISPLAY):
                m = svr.compose_report_message(report_message)
            svr.execute_report_message(report_message, m)

    #----------------------------------------------------------------------------
    # Group: Message Processing
    #----------------------------------------------------------------------------

    # Function: execute_report_message
    #
    # Processes the provided message per the actions contained within.
    #
    # Expert users can overload this method to customize action processing.

    def execute_report_message(self, report_message, composed_message):
        #process p = process::self()

        # Update counts
        self.incr_severity_count(report_message.get_severity())
        self.incr_id_count(report_message.get_id())

        if self.record_all_messages is True:
            report_message.set_action(report_message.get_action() | UVM_RM_RECORD)

        # UVM_RM_RECORD action
        if report_message.get_action() & UVM_RM_RECORD:
            stream = None  # uvm_tr_stream stream
            ro = report_message.get_report_object()
            rh = report_message.get_report_handler()

            # Check for pre-existing stream TODO
            #if (m_streams.exists(ro.get_name()) && (m_streams[ro.get_name()].exists(rh.get_name())))
            #stream = m_streams[ro.get_name()][rh.get_name()]

            # If no pre-existing stream (or for some reason pre-existing stream was ~null~)
            if stream is None:
                # Grab the database
                db = self.get_message_database()

                # If database is ~null~, use the default database
                if db is None:
                    cs = get_cs()
                    db = cs.get_default_tr_database()

                if db is not None:
                    # Open the stream.    Name=report object name, scope=report handler name, type=MESSAGES
                    stream = db.open_stream(ro.get_name(), rh.get_name(), "MESSAGES")
                    # Save off the openned stream
                    self.m_streams[ro.get_name()][rh.get_name()] = stream
            if stream is not None:
                recorder = stream.open_recorder(report_message.get_name(), None,report_message.get_type_name())
                if recorder is not None:
                    report_message.record(recorder)
                    recorder.free()

        # DISPLAY action
        if report_message.get_action() & UVM_DISPLAY:
            print(composed_message)

        # LOG action
        # if log is set we need to send to the file but not resend to the
        # display. So, we need to mask off stdout for an mcd or we need
        # to ignore the stdout file handle for a file handle.
        if report_message.get_action() & UVM_LOG:
            if report_message.get_file() == 0 or report_message.get_file() != 0x80000001: #ignore stdout handle
                tmp_file = report_message.get_file()
                #if report_message.get_file() & 0x80000000 == 0: # is an mcd so mask off stdout
                #    tmp_file = report_message.get_file() & 0xfffffffe
                self.f_display(tmp_file, composed_message)

        # Process the UVM_COUNT action
        if report_message.get_action() & UVM_COUNT:
            if self.get_max_quit_count() != 0:
                self.incr_quit_count()
                # If quit count is reached, add the UVM_EXIT action.
                if self.is_quit_count_reached():
                    report_message.set_action(report_message.get_action() | UVM_EXIT)

        # Process the UVM_EXIT action
        if report_message.get_action() & UVM_EXIT:
            cs = get_cs()
            l_root = cs.get_root()
            l_root.die()

        # Process the UVM_STOP action
        if report_message.get_action() & UVM_STOP:
            raise Exception("$stop from uvm_report_server, msg: " +
                    report_message.sprint())

    # Function: compose_report_message
    #
    # Constructs the actual string sent to the file or command line
    # from the severity, component name, report id, and the message itself.
    #
    # Expert users can overload this method to customize report formatting.
    def compose_report_message(self, report_message, report_object_name=""):
        sev_string = ""
        l_severity = UVM_INFO
        l_verbosity = UVM_MEDIUM
        filename_line_string = ""
        time_str = ""
        line_str = ""
        context_str = ""
        verbosity_str = ""
        terminator_str = ""
        msg_body_str = ""
        el_container = None
        prefix = ""
        l_report_handler = None

        l_severity = report_message.get_severity()
        sev_string = ename(l_severity)

        if report_message.get_filename() != "":
            line_str = str(report_message.get_line())
            filename_line_string = report_message.get_filename() + "(" + line_str + ") "

        # Make definable in terms of units.
        #$swrite(time_str, "%0t", $time)
        #time_str = get_sim_time('ns') TODO
        time_str = str(uvm_sim_time('NS')) + 'NS'

        if report_message.get_context() != "":
            context_str = "@@" + report_message.get_context()

        if self.show_verbosity is True:
            verb = report_message.get_verbosity()
            verbosity_str = "(" + verb + ")"

        if self.show_terminator is True:
            terminator_str = " -" + sev_string

        el_container = report_message.get_element_container()
        if el_container.size() == 0:
            msg_body_str = report_message.get_message()
        else:
            prefix = uvm_default_printer.knobs.prefix
            uvm_default_printer.knobs.prefix = " +"
            msg_body_str = report_message.get_message() + "\n" + el_container.sprint()
            uvm_default_printer.knobs.prefix = prefix

        if report_object_name == "":
            l_report_handler = report_message.get_report_handler()
            if l_report_handler is not None:
                report_object_name = l_report_handler.get_full_name()
            else:
                report_object_name = "NO_REPORT_OBJECT"

        result = (sev_string + verbosity_str + " " + filename_line_string
            + "@ " + time_str + ": " + report_object_name + context_str
            + " [" + report_message.get_id() + "] " + msg_body_str + terminator_str)
        return result

    # Function: report_summarize
    #
    # Outputs statistical information on the reports issued by this central report
    # server. This information will be sent to the command line if ~file~ is 0, or
    # to the file descriptor ~file~ if it is not 0.
    #
    # The <run_test> method in uvm_top calls this method.

    def report_summarize(self, file=0):
        rpt = self.get_summary_string()
        uvm_info("UVM/REPORT/SERVER", rpt, UVM_LOW)

    # Function: get_summary_string
    #
    # Returns the statistical information on the reports issued by this central report
    # server as multi-line string.
    def get_summary_string(self):
        id = ""
        q = []

        UVMReportCatcher.summarize()
        q.append("\n--- UVM Report Summary ---\n\n")

        if self.m_max_quit_count != 0:
            if self.m_quit_count >= self.m_max_quit_count:
                q.append("Quit count reached!\n")
            q.append("Quit count : {} of {}\n".format(self.m_quit_count,
                self.m_max_quit_count))

        q.append("** Report counts by severity\n")
        for s in self.m_severity_count.keys():
            q.append("{} : {}\n".format(ename(s), self.m_severity_count.get(s)))

        if self.enable_report_id_count_summary is True:
            q.append("** Report counts by id\n")
            for id in self.m_id_count.keys():
                q.append("[{}] {}\n".format(id, self.m_id_count.get(id)))
        return "".join(q)

def get_cs():
    from .uvm_coreservice import UVMCoreService
    return UVMCoreService.get()


