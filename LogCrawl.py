import sublime
import sublime_plugin
import re
import os
import threading

default_pattern = "missing val|repeats of BY values|uninitialized|[^l]remerge|Invalid data for"

ignore_pattern = "Unable to copy SASUSER registry|the BASE SAS Software product with which|your system is scheduled|will be expiring soon, and|this upcoming expiration.|information on your warning period.|Unable to open SASUSER.PROFILE|All profile changes will be lost|Copyright (c)|This session is executing|The Base Product product"

default_lst_pattern = "The COMPARE Procedure|No unequal values|not found in"


def getSettingsRegex(extension):
    if extension == "log" or extension == "lst":
        s = sublime.load_settings('SAS_Log_Crawler.sublime-settings')

        if extension == "log":
            def_regx = s.get('err-regx', default_pattern)
            ign_regx = s.get('ign-regx', ignore_pattern)
            regex = "(^(error|warning:)|" + default_pattern + ")(?! (" + ignore_pattern + "))"
        elif extension == "lst":
            def_regx = s.get('lst-regx', default_pattern)
            s.set('lst-regx', def_regx)
            regex = "(" + default_pattern + ")"

        return regex
    else:
        return False


def goToNextError(theView, err_regx):
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


def getExtension(theView):
    path = theView.file_name().split("\\")[-1:]
    # print(path)
    ext = path[0].split(".")[-1:]
    # print(ext[0])
    return ext[0]


def getPath(paths=[]):
    return paths[0]


class log_crawl(sublime_plugin.TextCommand):
    def run(self, edit):
        ext = getExtension(self.view)
        # print(ext)
        # Get pattern from settings or use default
        err_regx = getSettingsRegex(ext)
        # Go to next error
        goToNextError(self.view, err_regx)


# Still need TODO:
class side_bar_check_log(sublime_plugin.TextCommand):
    def run(self, view, files=[]):
        file = getPath(files)
        print("File is " + str(file))
        if file:
            # Open the file that was selected with the cursur
            window = self.view.window()
            view = window.open_file(os.path.realpath(file))

            while view.is_loading():
                time.sleep(0.3)

            ext = getExtension(self.view)
            # print(ext)
            # Get pattern from settings or use default
            err_regx = getSettingsRegex(ext)
            # Go to next error
            goToNextError(self.view, err_regx)
        else:
            sublime.status_message("No file selected.")


# Still need TODO:
class side_bar_check_folder_logs(sublime_plugin.TextCommand):
    def run(self, view, files=[]):
        # Get pattern from settings or use default
        err_regx = getSettingsRegex()
        # Go to next error
        goToNextError(self.view, err_regx)
