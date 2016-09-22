import sublime
import sublime_plugin
import re


def getSettingsRegex(extension):
    if extension == "log" or extension == "lst":
        s = sublime.load_settings('SAS_Log_Crawler.sublime-settings')

        if extension == "log":
            err_regx = s.get('err-regx', "(^(error|warning:)|missing val|repeats of BY values|uninitialized|[^l]remerge|Invalid data for)(?! (Unable to copy SASUSER registry|the .{4,15} product with which|your system is scheduled|will be expiring soon, and|this upcoming expiration.|information on your warning period.))")
            s.set('err-regx', err_regx)
        elif extension == "lst":
            err_regx = s.get('lst-regx', "(The COMPARE Procedure|No unequal values|not found in)")
            s.set('lst-regx', err_regx)

        sublime.save_settings('SAS_Log_Crawler.sublime-settings')
        return err_regx
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
    def run(self, paths=[]):
        # Get pattern from settings or use default
        err_regx = getSettingsRegex()
        # Go to next error
        goToNextError(self.view, err_regx)


# Still need TODO:
class side_bar_check_folder_logs(sublime_plugin.TextCommand):
    def run(self, paths=[]):
        # Get pattern from settings or use default
        err_regx = getSettingsRegex()
        # Go to next error
        goToNextError(self.view, err_regx)
