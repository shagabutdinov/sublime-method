import sublime
import sublime_plugin
import Method.ruby
import re

class MethodBase(sublime_plugin.TextCommand):

  def _get_method_info(self, methods, method, expand):
    region = self._get_method_region(methods, method, expand)
    contents = self.view.substr(region)
    offset = [self.view.sel()[0].a - region.a, self.view.sel()[0].b - region.a]
    return contents, offset

  def _convert_after_to_expand(self, after):
    if after:
      return "backward"
    else:
      return "forward"

  def _get_insert_info(self, methods, index, after, offset):
    position = self._get_cursor_position(methods[index], after)
    start = position.a

    # ?? :(
    if after:
      start += 1
    else:
      start -= 2

    cursor = sublime.Region(start + offset[0], start + offset[1])
    line = self.view.line(position)
    insert_position = line.a
    if after:
      insert_position = line.b + 1
    return insert_position, cursor

  def _get_methods(self):
    code = self.view.substr(sublime.Region(0, self.view.size()))
    methods = Method.ruby.extract_methods(code)
    return methods

  def _get_method_region(self, methods, index, expand = None):
    index = self._prepare_index(methods, index)[0]
    method = methods[index]
    result = self.view.full_line(sublime.Region(method["start"], method["end"]))

    if expand == "forward":
      if self.view.substr(sublime.Region(result.b, result.b + 1)) == "\n":
        result = sublime.Region(result.a, result.b + 1)
    elif expand == "backward":
      if self.view.substr(sublime.Region(result.a - 1, result.a)) == "\n":
        result = sublime.Region(result.a - 1, result.b)

    return result

  def _save_regions(self):
    self.view.erase_regions("Method")
    regions = []
    for sel in self.view.sel():
      regions.append(sublime.Region(sel.a, sel.b))
    self.view.add_regions("Method", regions, "method", "")

  def _restore_regions(self):
    self.view.sel().clear()
    regions = []
    for region in self.view.get_regions("Method"):
      regions.append(sublime.Region(region.a, region.b))
    self.view.sel().add_all(regions)

  def _get_cursor_position(self, method_info, after):
    if after:
      position = method_info["end"]
    else:
      position = method_info["start"]

    selection = sublime.Region(position, position)
    return selection

  def _set_cursor_position(self, method_info, after):
    selection = self._get_cursor_position(method_info, after)
    self.view.sel().clear()
    self.view.sel().add(selection)

  def _get_name_position(self, method_info):
    start = method_info["start"]
    text = self.view.substr(sublime.Region(start, self.view.size()))
    name_start = start + text.index(method_info["name"])
    name_end = name_start + len(method_info["name"])
    return name_start, name_end

  def _insert_method_space(self, after):
    self.view.run_command("insert", {"characters": "\n\n"})
    if not after:
      self.view.run_command("move", {"by": "lines", "forward": False})
      self.view.run_command("move", {"by": "lines", "forward": False})

  def _insert_method(self, edit, name, body, cursor, snippet, indent):
    if snippet:
      contents = Method.ruby.get_method_snippet(name, body)
      self.view.run_command("insert_snippet", {"contents": contents})
    else:
      contents, index = Method.ruby.get_method_text(name, body, cursor)
      index = self.view.sel()[0].b + index

      if indent > 0:
        contents = contents.replace("\n", "\n" + " " * indent)

      self.view.insert(edit, self.view.sel()[0].b, contents)
      self.view.sel().clear()
      self.view.sel().add(sublime.Region(index, index))

  def _prepare_index(self, methods, index):
    if index == None:
      return []

    result = []
    if isinstance(index, list):
      for index_item in index:
        result += self._prepare_index(methods, index_item)
      return result

    current = self._get_current_index(methods)

    match = None
    if isinstance(index, str):
      match = re.match(r"^(\+|\-|)(\d+)$", index)

    if current != None and match != None:
      if match.group(1) == '+':
        index = current + int(match.group(2))
        if index > len(methods) - 1:
          index = len(methods) - 1
      elif match.group(1) == '-':
        index = current - int(match.group(2))
        if index < 0:
          index = 0
      else:
        index = int(match.group(2))

      result = [index]

    elif isinstance(index, str) and index[0] == "/":
      regexp = index[1:-1]
      index = None
      for method_index, method in enumerate(methods):
        if re.search(regexp, method["name"]):
          result.append(method_index)

    elif isinstance(index, str) and index[0] == ":":
      name = index[1:]
      index = None
      for method_index, method in enumerate(methods):
        if name == method["name"]:
          index = method_index
          indexes.append(index)
          break

    elif index == "current":
      result = [current]

    elif index == "private":
      index = None
      for method_index, method in enumerate(methods):
        if "private" in method and method["private"]:
          result.append(method_index)

    elif index == "last_private":
      index = None
      for method_index, method in enumerate(methods):
        if "private" in method and method["private"]:
          result = [method_index]

    elif index == "protected":
      index = None
      for method_index, method in enumerate(methods):
        if "protected" in method and method["protected"]:
          result.append(method_index)

    elif index == "last_protected":
      index = None
      for method_index, method in enumerate(methods):
        if "protected" in method and method["protected"]:
          result = [method_index]

    elif index == "last":
      result = [len(methods) - 1]

    elif isinstance(index, int):
      result = [index]

    return result

  def _get_current_index(self, methods):
    cursor = self.view.sel()[0].b
    index = None

    max_cursor = 0
    for method_index, method in enumerate(methods):
      if cursor <= method["end"] and cursor >= max_cursor:
        max_cursor = method["end"]
        index = method_index

    if index == None:
      index = len(methods) - 1

    return index

  def _get_info(self, name, body, cursor, snippet, delete):
    selection = self.view.substr(self.view.sel()[0]).strip()
    if name == '$selection':
      name = selection

    if name == None:
      name = ""

    if name == '$auto':
      if "\n" not in selection:
        name = selection
      else:
        name = ""

    if body == '$selection':
      body = selection

    if body == '$auto':
      if "\n" in selection:
        body = self._unindent(selection)
      else:
        body = ""

    if body == None:
      body = ""

    if cursor == '$auto':
      if "\n" in selection:
        cursor = "name"
      else:
        cursor = "body"

    if snippet == "$auto":
      snippet = selection == ""

    if delete == "$auto":
      delete = "\n" in selection

    return name, body, cursor, snippet, delete

  def _unindent(self, text):
    lines = text.split("\n")
    match = re.match(r"([\t ]+)[^\s]", lines[len(lines) - 1])
    if match == None:
      return text

    text = re.sub(r"(^|\n)" + match.group(1), "\\1", text)

    return text

class SelectMethods(MethodBase):
  def run(self, edit, methods = "current", excepts = None, body = False):
    current_methods = self._get_methods()
    methods_indexes = self._prepare_index(current_methods, methods)
    excepts_indexes = self._prepare_index(current_methods, excepts)

    print(methods_indexes)
    print(excepts_indexes)

    self.view.sel().clear()
    for index in methods_indexes:
      if index in excepts_indexes:
        continue

      start = current_methods[index]["start"]
      end = current_methods[index]["end"]

      if body:
        start = self.view.line(start).b + 1
        end = self.view.line(end).a - 1

      region = self.view.line(sublime.Region(start, end))
      self.view.sel().add(region)

class GoToMethod(MethodBase):
  def run(self, edit, method = "current", position = None):
    methods = self._get_methods()
    method = self._prepare_index(methods, method)[0]
    info = methods[method]

    cursor = info["start"]
    region = sublime.Region(cursor, self.view.size())
    cursor += self.view.substr(region).index(info["name"]) + len(info["name"])
    if position == "swap":
      if self.view.sel()[0].b == cursor:
        cursor = info["end"]
    elif position != None:
      cursor = info[position]

    self.view.sel().clear()
    self.view.sel().add(sublime.Region(cursor, cursor))
    self.view.show_at_center(sublime.Region(cursor, cursor))

class CloneMethod(MethodBase):
  def run(self, edit, method = "current", index = 0, after = False):
    methods = self._get_methods()
    method = self._prepare_index(methods, method)[0]
    index = self._prepare_index(methods, index)[0]

    if method == index and after == False:
      return

    expand = self._convert_after_to_expand(after)
    method_contents, offset = self._get_method_info(methods, method, expand)
    insert_position, cursor = self._get_insert_info(methods, index, after, offset)

    self.view.insert(edit, insert_position, method_contents)
    self.view.sel().clear()
    self.view.sel().add(cursor)

    methods = self._get_methods()
    method = self._prepare_index(methods, "current")[0]
    method_info = methods[method]

    _, sel_end = self._get_name_position(method_info)
    self.view.sel().clear()
    cursor = sublime.Region(sel_end, sel_end)
    self.view.sel().add(cursor)

    self.view.show_at_center(cursor)

class MoveMethod(MethodBase):
  def run(self, edit, method = "current", index = 0, after = False):
    methods = self._get_methods()
    method = self._prepare_index(methods, method)[0]
    index = self._prepare_index(methods, index)[0]

    if method == index and after == False:
      return

    expand = self._convert_after_to_expand(after)
    method_contents, offset = self._get_method_info(methods, method, expand)
    insert_position, cursor = self._get_insert_info(methods, index, after, offset)

    self.view.insert(edit, insert_position, method_contents)
    self.view.sel().clear()
    self.view.sel().add(cursor)
    self.view.show_at_center(cursor)

    new_methods = self._get_methods()
    if index < method:
      method += 1

    erase = self._get_method_region(new_methods, method, "forward")
    self.view.erase(edit, erase)

class DeleteMethod(MethodBase):
  def run(self, edit, method = "current"):
    methods = self._get_methods()
    region = self._get_method_region(methods, method, "forward")
    self.view.erase(edit, region)


class InsertMethodNameToMark(MethodBase):
  def run(self, edit, method = "current"):
    methods = self._get_methods()
    method_index = self._prepare_index(methods, method)[0]

    self.view.run_command("next_bookmark", {"name": "mark"})
    self.view.run_command("clear_bookmarks", {"name": "mark"})

    name = methods[method_index]["name"] + "()"
    cursor = self.view.sel()[0].b
    self.view.insert(edit, cursor, name)
    self.view.sel().clear()
    cursor += len(name) - 1
    self.view.sel().add(sublime.Region(cursor, cursor))

class CreateMethodSpace(MethodBase):
  def run(self, edit, index = 0, after = False):
    methods = self._get_methods()
    index = self._prepare_index(methods, index)[0]
    self._set_cursor_position(methods[index], after)
    self._insert_method_space(after)

class CreateMethod(MethodBase):
  def run(self, edit,
    index = 0,
    name = "$auto",
    body = "$auto",
    after = False,
    restore = False,
    snippet = "$auto",
    cursor = "$auto",
    delete = "$auto",
    mark = True,
  ):

    if restore:
      self._save_regions()

    name, body, cursor, snippet, delete = self._get_info(name, body, cursor,
      snippet, delete)

    if mark and not restore:
      self.view.run_command("set_mark")

    if delete:
      self.view.erase(edit, self.view.sel()[0])

    methods = self._get_methods()
    index = self._prepare_index(methods, index)[0]
    method_info = methods[index]
    indent = self._get_method_indent(method_info)

    self._set_cursor_position(method_info, after)
    self._insert_method_space(after)

    self._insert_method(edit, name, body, cursor, snippet, indent)

    if restore:
      self._restore_regions()

    if mark and restore:
      self.view.run_command("set_mark")

  def _get_method_indent(self, method):
    line = self.view.full_line(sublime.Region(method["start"], method["end"]))
    text = self.view.substr(line)
    match = re.match(r"^([ \t]*)[^\s]+", text)
    if match == None:
      return 0

    return len(match.group(1))