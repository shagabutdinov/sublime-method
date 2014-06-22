import re

def extract_methods(code):
  result = []
  for match in re.finditer(r"([\t ]*)(def) ([\w\.\?\!]+)", code):
    method_start = match.start(2)

    indent = match.group(1)
    method_end_match = re.search("\n" + indent + r"(end)", code[method_start:])
    if method_end_match == None:
      continue

    code_before = code[:method_start]

    method_end = len(code_before) + method_end_match.end(1)

    is_private_match = re.search(indent + "private", code_before)
    is_private = is_private_match != None

    is_protected_match = re.search(indent + "protected", code_before)
    is_protected = is_protected_match != None

    method = {
      "name": match.group(3),
      "start": method_start,
      "end": method_end,
      "indent": len(indent),
      "protected": is_protected,
      "private": is_private,
    }

    result.append(method)

  return result

def get_method_text(name = '', body = '', cursor = None):
  args = ""
  if not "(" in name:
    args = "()"

  result = "def " + name

  index = 0
  if cursor == "name":
    index = len(result)

  result += args
  if cursor == "args":
    index = len(result) - 1

  body = "  " + body.replace("\n", "\n  ")
  result += "\n" + body
  if cursor == "body":
    index = len(result)

  result += "\nend"

  return result, index

def get_method_snippet(name = '', body = ''):
  args = ""
  if not "(" in name:
    args = "($2)"
  return "def ${1:" + name + "}" + args + "\n  " + body + "$0\nend"