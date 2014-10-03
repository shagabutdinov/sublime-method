# some python code

class MethodBase(sublime_plugin.TextCommand):

  def _process(self, result):
    # do stuff here...
    return result # method was moved

  def _prepare_index(self, methods, index):
    if index == None:
      return []

    result = []
    if isinstance(index, list):
      for index_item in index:
        result += self._prepare_index(methods, index_item)
      return result

    # done
    result = self._call(methods, index, result)

    # new method will be added
    result = self._process(result)

    return result

  def _call(self, methods, index, result):
    if current != None and match != None:
      if match.group(1) == '+':
        index = current + int(match.group(2))
        if index > len(methods) - 1:
          index = len(methods) - 1

      result = [index]

    return result