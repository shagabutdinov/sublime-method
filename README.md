Sublime method manipulation plugin
==================================

Allows to manipulate methods in file. If you like this plugin please star this
repo.

Warning
-------

Plugin is beta. Documentation is incomplete. You can help improve the plugin by
sending a pull request.

Features
--------

- Extract method refactoring

- Create new method

- Create space for new method

- Delete method

- Clone method

- Go to method

- Select method

- Comment/uncomment all tests except current


Setup
-----

Available commands:


  - select_methods(edit, methods = "current", excepts = None, body = False):

  - go_to_method(edit, method = "current", position = None):

  - clone_method(edit, method = "current", index = 0, after = False):

  - move_method(edit, method = "current", index = 0, after = False):

  - delete_method(edit, method = "current"):

  - insert_method_name_to_mark(edit, method = "current"):

  - create_method_space(edit, index = 0, after = False):

  - create_method(edit, index = 0, name = "$auto", body = "$auto",
      after = False, restore = False, snippet = "$auto",
      cursor = "$auto", delete = "$auto", mark = True)

    $auto - let plugin decide what to put in variable

Supported values for methods, method, excepts and index variables:

  - /regexp/ - method name regexp

  - :name - method name

  - current - current method

  - first - first method

  - last - last method

  - private - first private method

  - protected - first protected method

  - last_private - last private method

  - last_protected - last protected method

  - [] - look for first available method in array or for all methods for
    multiple method manipulation

Configuration
-------------

This is my preferred completion configuration. Add it to your ".sublime-keymap" to start using the plugin.

    {"keys": ["ctrl+m", "ctrl+."], "command": "create_method",
      "args": {"index": "current", "after": true}},
    {"keys": ["ctrl+m", "ctrl+,"], "command": "create_method",
      "args": {"index": "current"}},
    {"keys": ["ctrl+m", "ctrl+u"], "command": "create_method",
      "args": {"index": 1}},
    {"keys": ["ctrl+m", "ctrl+i"], "command": "create_method",
      "args": {"index": "protected"}},
    {"keys": ["ctrl+m", "ctrl+o"], "command": "create_method",
      "args": {"index": "private"}},
    {"keys": ["ctrl+m", "ctrl+p"], "command": "create_method",
      "args": {"index": "last", "after": true}},

    {"keys": ["ctrl+m", "ctrl+n"], "command": "create_method_space",
      "args": {"index": "current", "after": true}},
    {"keys": ["ctrl+m", "ctrl+d"], "command": "delete_method",
      "args": {"method": "current"}},
    {"keys": ["ctrl+m", "ctrl+c"], "command": "clone_method",
      "args": {"index": "current", "after": true}},
    {"keys": ["ctrl+m", "ctrl+m"], "command": "insert_method_name_to_mark",
      "args": {}},

    {"keys": ["ctrl+m", "ctrl+s"], "command": "select_methods",
      "args": {"methods": "current"}},
    {"keys": ["ctrl+m", "ctrl+w"], "command": "select_methods",
      "args": {"methods": "current", "body": true}},
    {"keys": ["ctrl+m", "ctrl+a"], "command": "run_macro_file", "args": {"file":
      "res://Packages/Method/leave_only_current_test.sublime-macro"}},
    {"keys": ["ctrl+m", "ctrl+q"], "command": "run_macro_file", "args": {"file":
      "res://Packages/Method/uncomment_bookmarks.sublime-macro"}},

    {"keys": ["alt+n"], "command": "go_to_method",
      "args": {"method": "+1"}},
    {"keys": ["alt+shift+n"], "command": "go_to_method",
      "args": {"method": "-1"}},
    {"keys": ["alt+ctrl+n"], "command": "go_to_method",
      "args": {"method": "current", "position": "swap"}},
    {"keys": ["ctrl+m", "ctrl+/"], "command": "go_to_method",
      "args": {"method": "last"}},

    {"keys": ["ctrl+-"], "command": "move_method",
      "args": {"index": "-1"}},
    {"keys": ["ctrl+="], "command": "move_method",
      "args": {"index": "+1", "after": true}},
    {"keys": ["ctrl+m", "ctrl+y"], "command": "move_method",
      "args": {"index": "-1"}},
    {"keys": ["ctrl+m", "ctrl+h"], "command": "move_method",
      "args": {"index": "+1", "after": true}},
    {"keys": ["ctrl+m", "ctrl+j"], "command": "move_method",
      "args": {"index": 0, "after": true}},
    {"keys": ["ctrl+m", "ctrl+k"], "command": "move_method",
      "args": {"index": "protected"}},
    {"keys": ["ctrl+m", "ctrl+l"], "command": "move_method",
      "args": {"index": "private"}},
    {"keys": ["ctrl+m", "ctrl+;"], "command": "move_method",
      "args": {"index": "last", "after": true}},

TODO
----

- Multilanguage support

- Javascript, php, coffeescript languages