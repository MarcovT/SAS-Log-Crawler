import sublime
import sublime_plugin
import re
import os
import threading

# List for storing all file names with issues
found_files = []
# Dict for storing associations with satisfied lines and files
found_lines = {}

default_pattern = "will be overwritten by data set|Missing values were generated|repeats of BY values|uninitialized|[^l]remerge|Invalid data for"

ignore_pattern = "Unable to copy SASUSER registry|the BASE SAS Software product with which|your system is scheduled|will be expiring soon, and|this upcoming expiration.|information on your warning period.|Unable to open SASUSER.PROFILE|All profile changes will be lost|Copyright (c)|This session is executing|The Base Product product"

default_lst_pattern = "The COMPARE Procedure|No unequal values|not found in"


def get_settings_regex(extension):
    if extension == ".log" or extension == ".lst":
        s = sublime.load_settings('SAS_Log_Crawler.sublime-settings')

        if extension == ".log":
            def_regx = s.get('err-regx', default_pattern)
            ign_regx = s.get('ign-regx', ignore_pattern)
            regex = "(^(error|warning:)|" + def_regx + ")(?! (" + ign_regx + "))"
        elif extension == "lst":
            def_regx = s.get('lst-regx', default_pattern)
            s.set('lst-regx', def_regx)
            regex = "(" + def_regx + ")"

        return regex
    else:
        return False


def go_to_next_error_view(theView, err_regx):
    if err_regx:
        # Get end of last cursur position
        curr_pos = 0
        for region in theView.sel():
            curr_pos = region.end()

        # Find next error/message in log
        next_error = theView.find(err_regx, curr_pos, sublime.IGNORECASE)
        if next_error:
            # Clear out any previous error/messages in selection
            theView.sel().clear()
            theView.sel().add(next_error)
            theView.show(next_error)
            sublime.status_message("Found issue at " + str(next_error))
        else:
            sublime.status_message("No issues found!")
    else:
        sublime.status_message("This is not a .log or .lst file")


def get_extension(filename):
    if filename is not None:
        path = os.path.splitext(filename)[1]
    else:
        path = None
    return path


def check_if_can_call(view):
    # Set small asyncronous timeout while view is loading
    if view.is_loading():
        sublime.set_timeout_async(check_if_can_call, 0.1)
    else:
        # When view is done loading call the log check function to jump to first issue if any is found
        check_log_view(view)
    # Call recursively until view is done loading
    check_if_can_call(view)


def check_log_view(view):
    ext = get_extension(view.file_name())
    # print(ext)
    # Get pattern from settings or use default
    err_regx = get_settings_regex(ext)
    # Go to next error
    go_to_next_error_view(view, err_regx)


def find_issue_in_line(line, regex):
    # Find next error/message in log
    is_issue = re.search(r'%s' % regex, line, re.IGNORECASE)
    if is_issue:
        # If issue is found then add it to the array of issues for the file
        return True
    else:
        return False


def create_report(found_files=[], found_lines={}, path=""):
    print("Creating Report ...")
    sublime.status_message("Creating Report ...")
    # Now we build the bulky string before we create a new view and add the region
    report = "LOG REPORT \n" + "Folder: " + path + "\n"
    if len(found_lines) > 0:
        # Now we show issues for each file that is of importance
        for file in found_files:
            report += "\nISSUES FOR FILE: " + str(file) + "\n"
            for line in found_lines[file]:
                report += line + "\n"
    else:
        report += "\nResult: NO ISSUES FOUND!"

    # Now let's display the report in a view
    newView = sublime.active_window().new_file()
    newView.set_name("LOG REPORT.log")
    newView.run_command("insert", {"characters": report})
    # Trying to add scope to the new file to ensure colour coding
    p1 = 0
    p2 = newView.size()
    newView.set_syntax_file("SASLog.tmLanguage")
    print("Report Created ...")
    sublime.status_message("Report Created ...")


def checkSingleFile(file, path=""):
    # Store file extension
    extension = get_extension(file)
    if extension == ".log":
        # Open the file in current iteration
        with open(path + "/" + file) as fp:
            print("Checking File " + str(file))
            sublime.status_message("Checking File " + str(file))
            # We need to keep track of the lines that are issues in this file
            issueLines = []
            # Check every line in the opened file
            for line in fp:
                regex = get_settings_regex(extension)
                # Check if line satisfies the regex pattern stored in settings
                issueLine = find_issue_in_line(line, regex)
                # If an issue is found then store the line in an array
                if issueLine:
                    if file not in found_files:
                        found_files.append(file)
                    # Add the line and associate it with its parent file
                    issueLines.append(line)
                else:
                    continue
        if len(issueLines) > 0:
            found_lines[file] = issueLines
    else:
        return False


class singleLogThread (threading.Thread):
    def __init__(self, view, args, logObj):
        threading.Thread.__init__(self)
        self.view = view
        self.args = args
        self.logObj = logObj

    def run(self):
        # Get dirs and files from args
        dirs = self.args["dirs"]
        files = self.args["files"]
        # Stores the folder path of the files
        if len(dirs) > 0:
            path = dirs[0]
        else:
            path = os.path.dirname(files[0])
        # Get dirs and files from args
        file = files[0]
        checkSingleFile(file)
        # Create Final Report
        create_report(found_files, found_lines, path)


class folderLogThread (threading.Thread):
    def __init__(self, view, args):
        threading.Thread.__init__(self)
        self.view = view
        self.args = args

    def run(self):
        # Get dirs and files from args
        dirs = self.args["dirs"]
        files = self.args["files"]
        # Stores the folder path of the files
        if len(dirs) > 0:
            path = dirs[0]
        else:
            path = os.path.dirname(files[0])

        # Loop through files to check each file's lines
        for file in os.listdir(path):
            checkSingleFile(file, path)
        # Create Final Report
        create_report(found_files, found_lines, path)


class log_crawl(sublime_plugin.TextCommand):
    def run(self, edit):
        file = paths[0]
        if file:
            # Open the file that was selected with the cursur
            window = self.view.window()
            view = window.open_file(os.path.realpath(file))
            check_if_can_call(view)
        else:
            sublime.status_message("No file selected.")


class side_bar_check_log(sublime_plugin.TextCommand):

    def run(self, view, **args):
        thread1 = singleLogThread(self.view, args, self)
        thread1.start()


class side_bar_check_folder_logs(sublime_plugin.TextCommand):

    def run(self, view, **args):
        thread2 = folderLogThread(view, args)
        thread2.start()
        print("Started Checking Folder Logs ...")
        sublime.status_message("Started Checking Folder Logs ...")
