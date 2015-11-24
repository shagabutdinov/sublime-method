import sublime
import sublime_plugin
import re

from Method import method as parser

try:
  from Statement import statement
  from Expression import expression
  from LocalVariable import local_variable
except ImportError as error:
  sublime.error_message("Dependency import failed; please read readme for " +
   "Method plugin for installation instructions; to disable this " +
   "message remove this plugin; message: " + str(error))
  raise error

class MethodBase(sublime_plugin.TextCommand):

  def _get_language(self):
    if len(self.view.sel()) == 0:
      return None

    sel = self.view.sel()[0]

    match = re.search(r'source\.(\w+)', self.view.scope_name(sel.a))
    if match == None:
      return None

    return match.group(1)

  def _get_methods(self):
    methods = parser.extract_methods(self.view)
    return methods

  def _get_method_regions(self, methods, index):
    return parser.get_regions(self.view, methods[index])

  def _get_insert_info(self, region, target, after):
    text = self.view.substr(region)
    shift = [self.view.sel()[0].a - region.a, self.view.sel()[0].b - region.a]

    if after:
      text = "\n\n" + text
      point = target.b
      shift[0] += 2
      shift[1] += 2
    else:
      text += "\n\n"
      point = target.a

    return text, shift, point

  def _save_regions(self):
    self.view.erase_regions('Method')
    regions = []
    for sel in self.view.sel():
      regions.append(sublime.Region(sel.a, sel.b))
    self.view.add_regions('Method', regions, 'method', '')

  def _restore_regions(self):
    self.view.sel().clear()
    regions = []
    for region in self.view.get_regions('Method'):
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
    text = self.view.substr(sublime.Region(start, start + 255))
    name_start = start + text.index(method_info["name"])
    name_end = name_start + len(method_info["name"])
    return name_start, name_end

  def _insert_method_space(self, after):
    self.view.run_command('insert', {'characters': '\n\n'})
    if not after:
      self.view.run_command('move', {'by': 'lines', 'forward': False})
      self.view.run_command('move', {'by': 'lines', 'forward': False})

  def _insert_method(self, edit, indent, snippet):
    selection = self.view.sel()[0]
    line = self.view.line(selection.b)
    indent_value = self._get_indent(indent)

    self.view.replace(edit, sublime.Region(line.a, selection.b), indent_value)
    self.view.run_command('insert_snippet', {'contents': snippet})

  def _get_indent(self, indent):
    if self.view.settings().get('translate_tabs_to_spaces', False):
      tab = ' '
    else:
      tab = "\t"

    return tab * indent

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

    elif isinstance(index, str) and index[0] == '/':
      regexp = index[1 : - 1]
      index = None
      for method_index, method in enumerate(methods):
        if re.search(regexp, method["name"]):
          result.append(method_index)

    elif isinstance(index, str) and index[0] == ':':
      name = index[1 :]
      index = None
      for method_index, method in enumerate(methods):
        if name == method["name"]:
          index = method_index
          indexes.append(index)
          break

    elif index == 'current':
      result = [current]

    elif index == 'private':
      index = None
      for method_index, method in enumerate(methods):
        if method['privacy'] == 'private':
          result.append(method_index)

    elif index == 'last_private':
      index = None
      for method_index, method in reversed(enumerate(methods)):
        if method['privacy'] == 'private':
          result.append(method_index)

    elif index == 'protected':
      index = None
      for method_index, method in enumerate(methods):
        if method['privacy'] == 'protected':
          result.append(method_index)

    elif index == 'last_protected':
      index = None
      for method_index, method in reversed(enumerate(methods)):
        if method['privacy'] == 'protected':
          result.append(method_index)

    elif index == 'last':
      result = [len(methods) - 1]

    elif isinstance(index, int):
      result = [index]

    return result

  def _get_current_index(self, methods):
    cursor = self.view.sel()[0].b
    index = None

    max_cursor = 0
    for method_index, method in enumerate(methods):
      if cursor <= method["end"] and cursor > max_cursor:
        max_cursor = method["end"]
        index = method_index

    if index == None:
      index = len(methods) - 1

    return index

  def _get_definition(self, name, args, body, result, snippet):
    info = self._get_snippet_args(name, args, body, result)
    if info == None:
      return None

    name, args, body, result = info

    snippet = self._get_snippet_content(snippet)
    if snippet == None:
      return None

    snippet = self._set_args_to_snippet(snippet, name, args, body, result)
    return snippet

  def _get_snippet_content(self, snippet):
    language = self._get_language()
    if language == None:
      return None

    return parser.get_method_snippet(language, snippet)

  def _get_snippet_args(self, name, args, body, result):
    definition_info = self._get_definition_info()
    if definition_info == None:
      return

    definition_type, definition_region = definition_info
    if definition_type == 'name':
      if definition_region != None:
        new_name, new_args = self._extract_name(definition_region)
      else:
        new_name, new_args = None, ['']

      new_body, new_result = None, None
    else:
      new_body, new_args, new_result = self._extract_body(definition_region)
      new_name = None

    if name == None:
      name = new_name

    if args == None:
      args = new_args

    if body == None:
      body = new_body

    if result == None:
      result = new_result

    # fucking self
    scope_name = self.view.scope_name(self.view.sel()[0].a)
    if 'self' in args and 'python' in scope_name:
      args.remove('self')

    return name, args, body, result

  def _set_args_to_snippet(self, snippet, name, args, body, result):
    index = 1

    snippet = snippet.replace('$name', (name or '') + '$' + str(index))
    index += 1

    args_value = []
    for arg in args:
      arg = self._escape_snippet_value(arg)
      args_value.append('${' + str(index) + ':' + arg + '}')
      index += 1

    snippet = snippet.replace('$args', ', '.join(args_value))

    if body != None:
      body = self._escape_snippet_value(body)
      if result != None and len(result) != 0:
        result_args = []
        for result_arg in result:
          result_arg = self._escape_snippet_value(result_arg)
          result_args.append('${' + str(index) + ':' + result_arg + '}')
          index += 1

        body += '$' + str(index) + "\n\nreturn " + ', '.join(result_args)
        index += 1

      body_indent = re.search(r'\n(\s*)\$body', snippet)
      if body_indent != None:
        body = re.sub('(\n)', '\\1' + body_indent.group(1), body)
        snippet = snippet.replace('$body', (body or '') + '$' + str(index))
        index += 1

    return snippet

  def _escape_snippet_value(self, value):
    return(
      value.
        replace('\\', '\\\\').
        replace('$', '\\$').
        replace('{', '\\{').
        replace('}', '\\}')
    )

  def _extract_name(self, region):
    token_value = self.view.substr(sublime.Region(*region))
    parethesis = re.search(r'\(', token_value)
    if parethesis == None:
      name, args = token_value, []
    else:
      name = token_value[: parethesis.start(0)]
      args_point = region[0] + parethesis.end(0)
      args_tokens = statement.get_tokens(self.view, args_point) or []
      args = []
      for arg in args_tokens:
        args.append(self.view.substr(sublime.Region(*arg)))

    name_match = re.search(r'[\w\?\!]+$', name)
    if name_match != None:
      name = name_match.group(0)

    return name, args

  def _extract_body(self, region):
    variables = local_variable.find_variables(self.view, region[0], False)

    assignments = []
    for assignment in local_variable.find_all_assignments(self.view, region[0]):
      assignments.append(assignment['variable'])

    inner, following = [], []
    for variable in variables:
      if region[0] <= variable[0] and variable[1] <= region[1]:
        value = self.view.substr(sublime.Region(*variable))
        inner.append(value)
      elif region[1] <= variable[0]:
        value = self.view.substr(sublime.Region(*variable))
        following.append(value)

    preceding_assignments, inner_assignments = [], []
    for assignment in assignments:
      if assignment[1] <= region[0]:
        value = self.view.substr(sublime.Region(*assignment))
        if value not in preceding_assignments:
          preceding_assignments.append(value)
      elif region[0] <= assignment[0] and assignment[1] <= region[1]:
        value = self.view.substr(sublime.Region(*assignment))
        if value not in inner_assignments:
          inner_assignments.append(value)

    body = self._extract_indented_body(region)
    args = self._get_list_intersection(preceding_assignments, inner)
    result = self._get_list_intersection(inner_assignments, following)

    return body, args, result

  def _get_list_intersection(self, list1, list2):
    result = []
    for item in list1:
      if item in list2:
        result.append(item)
    return result

  def _get_definition_info(self):
    selection = self.view.sel()[0]
    if selection.empty():
      token_info = statement.get_token(self.view, selection.b)
      token = None
      if token_info != None:
        _, token = token_info

      if token == None or '(' not in self.view.substr(sublime.Region(*token)):
        token = statement.get_parent_token(self.view, selection.b, r'\(')

      if token == None:
        return 'name', None

      return 'name', token
    else:
      statement_1 = statement.get_statement(self.view, selection.begin())
      statement_2 = statement.get_statement(self.view, selection.end())

      if statement_1 == None or statement_2 == None:
        return None
      if statement_1 != statement_2 or expression.find_match(self.view,
        statement_1[0], r'\{', {'range': statement_1, 'string': False}) != None:
        return 'body', [statement_1[0], statement_2[1]]
      else:
        return 'name', statement_1

  def _extract_method_definition(self, cursor):
    _, token = statement.get_token(self.view, self.view.sel()[0].b)
    if token == None:
      return None

    if self.view.substr(sublime.Region(token[1] - 1, token[1])) != ')':
      token = statement.get_parent_token(self.view, cursor, r'\(')
      if token == None:
        return None

    return self.view.substr(sublime.Region(*token))

  def _prepare_name(self, selection):
    return re.sub(r'^(self|\$?this)(\.|->)', '', selection)

  # this method copied from SnippetCaller _get_indented_region
  def _extract_indented_body(self, region):
    sel = sublime.Region(*region)

    region = sublime.Region(self.view.line(sel.begin()).a, sel.end())
    text = re.sub(r'^([\n\s]*)\n', '', self.view.substr(region))
    original_text = re.sub(r'^([\n\s]*)\n', '', self.view.substr(sel))

    ignore_first_line = False
    if text.strip() != original_text.strip():
      text = original_text
      ignore_first_line = True

    lines = text.split("\n")
    min = None
    source_indentation = ''
    for index, line in enumerate(lines):
      if ignore_first_line and index == 0:
        continue

      match = re.search(r'^(\s*)\S', line)

      if match == None:
        continue

      if min == None or min > len(match.group(1)):
        min = len(match.group(1))
        source_indentation = match.group(1)

    result = re.sub(r'(^|\n)' + source_indentation, '\\1', text)
    result = result.rstrip()

    return result

class SelectMethods(MethodBase):
  def run(self, edit, methods = 'current', excepts = None, body = False):
    current_methods = self._get_methods()

    methods_indexes = self._prepare_index(current_methods, methods)
    excepts_indexes = self._prepare_index(current_methods, excepts)

    self.view.sel().clear()
    for index in methods_indexes:
      if index in excepts_indexes:
        continue

      method = current_methods[index]

      if body:
        start, end = method['body_start'], method['body_end']

      else:
        start, end = method["start"], method["end"]

      region = sublime.Region(start, end)
      if not body:
        region = self.view.line(region)

      self.view.sel().add(region)

class GotoMethod(MethodBase):
  def run(self, edit, method = 'current', position = None):
    methods = self._get_methods()
    method = self._prepare_index(methods, method)[0]
    info = methods[method]

    cursor = info["start"]
    region = sublime.Region(cursor, self.view.size())
    cursor += self.view.substr(region).index(info["name"]) + len(info["name"])
    if position == 'swap':
      if self.view.sel()[0].b == cursor:
        cursor = info["end"]
    elif position != None:
      cursor = info[position]

    self.view.sel().clear()
    self.view.sel().add(sublime.Region(cursor, cursor))
    self.view.show(sublime.Region(cursor, cursor))

class CloneMethod(MethodBase):
  def run(self, edit, method = 'current', index = 0, after = False):
    methods = self._get_methods()
    method = self._prepare_index(methods, method)[0]
    index = self._prepare_index(methods, index)[0]

    is_clone_invalid = (
      (index < 0 or index > len(methods) - 1)
    )

    if is_clone_invalid:
      return

    region, _, _ = self._get_method_regions(methods, method)
    target, _, _ = self._get_method_regions(methods, index)

    text, shift, point = self._get_insert_info(region, target, after)

    self.view.insert(edit, point, text)
    self.view.sel().clear()
    self.view.sel().add(sublime.Region(point + shift[0], point + shift[1]))

class MoveMethod(MethodBase):
  def run(self, edit, method = 'current', index = 0, after = False):
    methods = self._get_methods()
    method = self._prepare_index(methods, method)[0]
    index = self._prepare_index(methods, index)[0]

    is_move_invalid = (
      (method == index and after == True) or
      (index < 0 or index > len(methods) - 1)
    )

    if is_move_invalid:
      return

    old, old_delete, lines = self._get_method_regions(methods, method)
    text = self.view.substr(old)
    shift = [self.view.sel()[0].a - old.a, self.view.sel()[0].b - old.a]

    self.view.replace(edit, old_delete, lines)
    methods = self._get_methods()

    if method < index:
      index -= 1

    new, _, _ = self._get_method_regions(methods, index)

    if after:
      text = "\n\n" + text
      point = new.b
      shift[0] += 2
      shift[1] += 2
    else:
      text += "\n\n"
      point = new.a

    self.view.insert(edit, point, text)
    self.view.sel().clear()
    self.view.sel().add(sublime.Region(point + shift[0], point + shift[1]))

class DeleteMethod(MethodBase):
  def run(self, edit, method = 'current'):
    methods = self._get_methods()
    method = self._prepare_index(methods, method)[0]
    _, region, lines = self._get_method_regions(methods, method)
    self.view.replace(edit, region, lines)

class InsertMethodNameToMark(MethodBase):
  def run(self, edit, method = 'current', snippets = []):
    methods = self._get_methods()
    method_index = self._prepare_index(methods, method)[0]

    snippet = self._get_snippet(snippets, methods[method_index])

    self.view.run_command('goto_named_mark', {'name': 'method'})
    self.view.run_command('insert_snippet', {'contents': snippet})

  def _get_snippet(self, snippets, method):
    result_args, is_regular_snippet = self._get_result_args(method)
    snippet = self._get_snippet_value(snippets, is_regular_snippet)

    snippet_index = 1
    snippet_index, result_args_str = self._prepare_result_args(snippet_index,
      result_args, is_regular_snippet)

    args_prepared = self._get_args(method, snippet_index)

    snippet = (snippet.
      replace('${result}', result_args_str).
      replace('$name', method['name']).
      replace('$args', ', '.join(args_prepared)))

    return snippet

  def _get_args(self, method, snippet_index):
    match_options = {
      'range': [method['start'], method['end']],
      'nesting': True,
    }

    args_point = expression.find_match(self.view, method['start'], r'(?:\()',
      match_options)

    args = []
    if args_point != None:
      tokens_point = method['start'] + args_point.end(0)
      tokens = statement.get_tokens(self.view, tokens_point)
      for token in tokens:
        args.append(self.view.substr(sublime.Region(*token)))

    # fucking self
    if 'python' in self.view.scope_name(method['start']) and 'self' in args:
      args.remove('self')

    args_prepared = []
    for arg in args:
      snippet_index += 1
      args_prepared.append('${' + str(snippet_index) + ':' +
        re.search(r'^\S*', arg).group(0) + '}')

    return args_prepared

  def _prepare_result_args(self, snippet_index, result_args, is_regular):
    result_args_prepared = []
    if result_args != None:
      for arg in result_args:
        arg_value = self.view.substr(sublime.Region(*arg))
        snippet_index += 1
        result_args_prepared.append('${' + str(snippet_index) + ':' +
          self._escape_snippet_value(arg_value) + '}')

    result_args_str = ', '.join(result_args_prepared)
    if len(result_args_str) > 0 and is_regular:
      result_args_str += ' = '

    return snippet_index, result_args_str

  def _get_snippet_value(self, snippets, is_regular_snippet):
    if len(snippets) != 0:
      if is_regular_snippet:
        snippet_file = snippets[0]
      else:
        snippet_file = snippets[1]

      snippet = parser.get_method_insert_snippet(self._get_language(), None,
        snippet_file)
    else:
      snippet = parser.get_method_insert_snippet(self._get_language(),
        not is_regular_snippet)

    return snippet

  def _get_result_args(self, method):
    returns = expression.find_matches(self.view, method['body_start'],
      r'(?:\n|^).*?return', {'range': [method['body_start'],
      method['body_end']], 'nesting': True})

    null, result_args = None, None
    nulls = ['None', 'null', 'nil', 'undefined']
    for return_match in returns:
      tokens = statement.get_tokens(self.view, method['body_start'] +
        return_match.end(0))

      first_token = self.view.substr(sublime.Region(*tokens[0]))
      if len(tokens) == 1 and first_token in nulls:
        null = tokens[0]
      else:
        result_args = tokens

    is_regular_snippet = (
      null == None or
      result_args == None or
      len(result_args) <= 1
    )

    return result_args, is_regular_snippet

class CreateMethodSpace(MethodBase):
  def run(self, edit, index = 0, after = False):
    methods = self._get_methods()
    index = self._prepare_index(methods, index)[0]
    self._set_cursor_position(methods[index], after)
    self._insert_method_space(after)

class CreateMethod(MethodBase):
  def run(self, edit,
    index = 0,
    after = False,
    restore = False,
    name = None,
    args = None,
    body = None,
    result = None,
    snippet = None,
    cursor = '$auto',
    delete = '$auto',
    mark = True,
  ):
    if restore:
      self._save_regions()

    methods = self._get_methods()
    index = self._prepare_index(methods, index)[0]
    method_info = methods[index]
    indent = self._get_method_indent(method_info)

    snippet = self._get_definition(name, args, body, result, snippet)
    if snippet == None:
      raise Exception('Snippet for method not found')

    if mark and not restore:
      self.view.run_command('set_named_mark', {'name': 'method', 'icon': ''})

    if delete:
      self.view.erase_regions('method_delete')
      self.view.add_regions('method_delete', [self.view.sel()[0]])

    self._set_cursor_position(method_info, after)

    self._insert_method_space(after)
    self._insert_method(edit, indent, snippet)

    if restore:
      self._restore_regions()

    if mark and restore:
      self.view.run_command('set_named_mark', {'name': 'method', 'icon': ''})

    deleted = self.view.get_regions('method_delete')
    if len(deleted) > 0:
      indent_match = re.search(r'(^|\n)([^\S\n]*)\S', self.view.substr(deleted[0]))
      if indent_match == None:
        indent = ''
      else:
        indent = indent_match.group(2)

      self.view.replace(edit, deleted[0], '')
      self.view.insert(edit, deleted[0].begin(), indent)

  def _get_method_indent(self, method):
    line = self.view.full_line(sublime.Region(method["start"], method["end"]))
    text = self.view.substr(line)
    match = re.match(r"^([ \t]*)[^\s]+", text)
    if match == None:
      return 0

    return len(match.group(1))
