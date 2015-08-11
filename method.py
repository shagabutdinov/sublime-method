import sublime
import sublime_plugin
import re

from xml.dom import minidom

try:
  from Expression import expression
except ImportError:
  sublime.error_message("Dependency import failed; please read readme for " +
   "Method plugin for installation instructions; to disable this " +
   "message remove this plugin. Missing Sublime Text plugin: Expression.")

indented_languages = ['python', 'coffee', 'saas']

def extract_method(view, point = None):
  if point == None:
    point = view.sel()[0].begin()

  result = None
  for index, method in enumerate(extract_methods(view)):
    if point > method['start']:
      result = method

  return result

def extract_methods(view):
  methods = []
  text = view.substr(sublime.Region(0, view.size()))
  lines = text.split("\n")

  for index, word in enumerate(view.find_by_selector('entity.name.function')):
    start, body_start, privacy = _get_method_start(view, lines, word)
    end, body_end = _get_method_end(view, lines, start, body_start)

    methods.append({
      'index': index,
      'name': view.substr(word),
      'start': start,
      'end': end,
      'body_start': body_start,
      'body_end': body_end,
      'privacy': privacy,
    })

  return methods

def get_regions(view, method):
  start_line = view.line(method['start'])
  comment_point = start_line.a - 2
  if 'comment' in view.scope_name(comment_point):
    comment_start_point = view.extract_scope(comment_point).a
    start_line.a = view.line(comment_start_point).a

  region = sublime.Region(start_line.a, method['end'])
  delete = sublime.Region(region.a, region.b + 1)
  while True:
    if delete.a <= 0:
      break

    previous = view.line(delete.a - 1)
    if view.substr(previous).strip() == '':
      delete.a = previous.a
    else:
      break

  view_size = view.size()
  while True:
    if delete.b >= view_size:
      delete.b = view_size
      break

    next = view.line(delete.b)
    if view.substr(next).strip() == '':
      delete.b = next.b + 1
    else:
      break

  # delete.b += 1
  lines = ''

  # if index != 0 and index != len(methods) - 1:
  lines += "\n"

  return region, delete, lines

def _get_method_start(view, lines, name_range):
  start_line, _ = view.rowcol(name_range.a)
  start_col = re.search(r'^(\s*)', lines[start_line]).end(1)

  start = view.text_point(start_line, start_col)
  body_start = name_range.b
  if '(' in lines[start_line]:
    body_start = _skip_parenthesis_or_return_args(view, body_start)

  # check { or : right after body_start
  body_start_match = re.search(r'^\s*[{:]', view.substr(
    sublime.Region(body_start, body_start + 64)))

  if body_start_match != None:
    body_start += body_start_match.end(0)

  # strip whitespaces
  body_start += re.search(r'^\s*', view.substr(sublime.Region(body_start,
    body_start + 64))).end(0)

  return start, body_start, _get_method_privacy(lines, start_line)

def _skip_parenthesis_or_return_args(view, point):
  new_point = point
  while True:
    new_point = _skip_parenthesis(view, point)
    if new_point == point:
      break

    point = new_point

  if 'source.go' in view.scope_name(point):
    match = expression.find_match(view, point, r'{',
      {'range': [point, point + 128]})
    if match != None:
      new_point += match.end(0)

  return new_point

def _skip_parenthesis(view, point):
  if '(' not in view.substr(sublime.Region(point, view.line(point).b)):
    return point

  match = expression.find_match(view, point, r'\)',
    {'range': [point, point + 512], 'nesting': 'end'})

  if match == None:
    return point

  return match.end(0) + point

def _get_method_end(view, lines, start, body_start):
  empty = re.search(r'^\s*(\}|end)', view.substr(sublime.Region(body_start,
    body_start + 64)))

  if empty:
    return body_start + empty.end(0), body_start + empty.start(0)

  start_line, _ = view.rowcol(body_start)
  end_line = _method_method_end_line(view, lines, start_line)
  end = view.text_point(end_line, len(lines[end_line]))

  if _is_indented(view, start):
    body_end = end
  else:
    point = view.text_point(end_line, 0)
    end_line_range = view.line(point)
    body_end = end_line_range.a + re.search(r'^\s*', lines[end_line]).end(0)

  # stip body end
  body_end -= len(re.search(r'(\s*)$', view.substr(sublime.Region(body_end - 64,
    body_end))).group(0))

  return end, body_end

def _method_method_end_line(view, lines, start_line):
  previous_line_index, end_line = None, None
  source_indentation = len(re.match(r'^(\s*)', lines[start_line]).group(0))

  for line_index in range(start_line, len(lines)):
    line = lines[line_index]
    if line.strip() == '':
      continue

    current_indentation = len(re.match(r'^(\s*)', line).group(0))

    scope_name = view.scope_name(view.text_point(line_index, 0))
    if 'string' in scope_name or 'comment' in scope_name:
      continue

    end_found = (current_indentation < source_indentation and
      not line.strip().startswith('rescue')) # ruby rescue hack

    if end_found:
      end_line_token = line.strip()
      if end_line_token == 'end' or end_line_token[0] == '}':
        end_line = line_index
      else:
        end_line = previous_line_index
      break

    previous_line_index = line_index

  if end_line == None:
    end_line = len(lines) - 1

  return end_line

def _is_indented(view, point):
  scope = view.scope_name(point)
  for language in indented_languages:
    if language in scope:
      return True

  return False

def _get_method_privacy(lines, line):
  if 'public' in lines[line]:
    return 'public'

  if 'protected' in lines[line]:
    return 'protected'

  if 'private' in lines[line]:
    return 'private'

  privacies = ['public', 'protected', 'private']
  for index in reversed(range(0, line)):
    stripped = lines[index].strip()
    if stripped in privacies:
      return stripped

  return 'public'

def get_method_insert_snippet(language, null = False, filename = None):
  if filename == None:
    if null:
      filename = language + '-method-call-null.sublime-snippet'
    else:
      filename = language + '-method-call.sublime-snippet'

  return _get_snippet_body(filename)

def get_method_snippet(language, filename = None):
  if filename == None:
    filename = language + '-method.sublime-snippet'

  return _get_snippet_body(filename)

def _get_snippet_body(filename):
  snippets = sublime.find_resources(filename)
  if len(snippets) == 0:
    raise Exception('Snippet "' + filename + '" not found')

  snippet = sublime.load_resource(snippets[0])
  if snippet.strip() == '':
    return None

  xml = minidom.parseString(snippet).firstChild
  if xml == None:
    return None

  snippet = {}
  for node in xml.childNodes:
    if node.nodeType == node.ELEMENT_NODE:
      value_node = node.firstChild
      if value_node == None:
        continue

      if node.tagName == 'content':
        return value_node.data.strip()

  raise Exception('Snippet "' + name + '" is empty')
