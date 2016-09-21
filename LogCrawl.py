import sublime, sublime_plugin, re

class LogCrawl(sublime_plugin.TextCommand):
  def run(self, edit):
    s = sublime.load_settings('SAS-Log-Crawler.sublime-settings')
    err_regx = s.get('err-regx', "(^(error|warning:)|uninitialized|[^l]remerge|Invalid data for)(?! (the .{4,15} product with which|your system is scheduled|will be expiring soon, and|this upcoming expiration.|information on your warning period.|missing val|MERGE statement has more than one data set with repeats of BY values|The COMPARE Procedure|No unequal values)")
    s.set('err-regx', err_regx)
    sublime.save_settings('SAS-Log-Crawler.sublime-settings')
    # err_regx = re.compile(err_regx, re.MULTILINE)
    # Get end of last current selection.
    curr_pos = 0
    for region in self.view.sel():
        curr_pos = region.end()

    # Find the next error
    next_error = self.view.find(err_regx, curr_pos, sublime.IGNORECASE)
    if next_error:
      # Clear out any previous selections.
      self.view.sel().clear()
      self.view.sel().add(next_error)
      self.view.show(next_error)
      sublime.status_message("Found error at " + str(next_error))
    else:
      sublime.status_message("No errors found!")