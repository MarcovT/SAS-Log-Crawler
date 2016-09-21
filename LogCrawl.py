import sublime, sublime_plugin, re

def getSettingsRegex():
  s = sublime.load_settings('SAS_Log_Crawler.sublime-settings')
  err_regx = s.get('err-regx', "(^(error|warning:)|uninitialized|[^l]remerge|Invalid data for)(?! (the .{4,15} product with which|your system is scheduled|will be expiring soon, and|this upcoming expiration.|information on your warning period.)|missing val|MERGE statement has more than one data set with repeats of BY values|The COMPARE Procedure|No unequal values)")
  s.set('err-regx', err_regx)
  sublime.save_settings('SAS_Log_Crawler.sublime-settings')
  return err_regx

def goToNextError():
  # Get end of last cursur position
  curr_pos = 0
  for region in self.view.sel():
    curr_pos = region.end()

  # Find next error/message in log
  next_error = self.view.find(err_regx, curr_pos, sublime.IGNORECASE)
  if next_error:
    # Clear out any previous error/messages in selection
    self.view.sel().clear()
    self.view.sel().add(next_error)
    self.view.show(next_error)
    sublime.status_message("Found issue at " + str(next_error))
  else:
    sublime.status_message("No issues found!")

class log_crawl(sublime_plugin.TextCommand):
  def run(self, edit):
    # Get pattern from settings or use default
    err_regx =  getSettingsRegex()
    # Go to next error
    goToNextError()

class side_bar_check_log(sublime_plugin.TextCommand):
  def run(self, paths = []):
    # Get pattern from settings or use default
    err_regx =  getSettingsRegex()
    # Go to next error
    goToNextError()

class side_bar_check_folder_logs(sublime_plugin.TextCommand):
  def run(self, paths = []):
    # Get pattern from settings or use default
    err_regx =  getSettingsRegex()
    # Go to next error
    goToNextError()