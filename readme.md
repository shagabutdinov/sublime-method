# Sublime Method plugin

The glorious plugin that allows (almost) language independent methods
manipulation in file.

### Demo

![Demo](https://github.com/shagabutdinov/sublime-method/raw/master/demo/demo.gif "Demo")


### Installation

This plugin is part of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
plugin set. You can install sublime-enhanced and this plugin will be installed
automatically.

If you would like to install this package separately check "Installing packages
separately" section of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
package.


### WARNING

This plugin does not works with multicursors. The reason is that I'm too lazy
and the plugin is too complext to refactor it and add multicursors support.

At least one method should be defined in current file before you can start using
this plugin. At least one private or protected method should be defined if
you want to work with private/protected methods.

It relies heavely on source code indentation. If your file is poorly indented
then this plugin will not work properly.

E.g.:

  ```
  # good
  def a()
    test()
  end

  # bad
  def a()
  test()
  end
  ```

There is default support for languages: ruby, python, php, js, coffee. If you
want to provide other language supporting, you should create three files in
"User" plugins directory:

- [language]-method.sublime-snippet
- [language]-method-call.sublime-snippet
- [language]-method-call-null.sublime-snippet

Where [language] is your language as it defined in sublime (to find out right
name use "ctrl+u, ctrl+\" hotkey).

See "snippets" directory for examples. You can also make pull request to make
your language support available for everybody.

### Features

1. Create (extract) method - creates new method. It tries to detect method name,
args, body and return value based on current cursor position. There is also
bindings to show where to create method (in beginning of method list, in
"private" section and etc.)

2. Move method - moves current method under cursor to new position (begin of
methods list, to private)

3. Goto method - allows bind shortcuts to goto first/last method, first/last
private method, next/previous method and method by name (e.g. "__init__")

4. Create method space - creates space for method so your preferred snippet can
be executed here. Especeally good for defining tests.

5. Delete method - deletes current method. Especeally good when working with
tests.

6. Clone method - clones current method. Especeally good when working with
tests.

7. Insert method name to mark - inserts current method name, arguments and
result to mark.

8. Select methods - select specified methods name or methods body.

9. Comment/uncomment all except current - usefull when you want to run only
current test; hotkey is faster than specifying "--name test_my_feature" in
command line.

### Usage

Only few usecases displayed here. Please see "Commands" section to receive
complete command list.

##### Create method (by name)

  ```
  # before
  def a(a)
    b(a)| # <- cursor is here
  end

  # after
  def a(a)
    b(a)
  end

  def b|(a) # <- cursor is here

  end
  ```

##### Create method (by body)

  ```
  # before
  def a(a)
    {a = b(a)
    a = c(a)}| # <- selection is here
    d(a)
  end

  # after
  def a(a)

  end

  def |(a) # <- cursor is here
    a = b(a)
    a = c(a)
    return a
  end
  ```

##### Move method down
  ```
  # before
  def first()
    | # <- cursor is here
  end

  def second()

  end

  # after
  def second()

  end

  def first()
    | # <- cursor is here
  end
  ```

### Commands

| Description                  | Keyboard shortcut | Command palette                      |
|------------------------------|-------------------|--------------------------------------|
| Create method before current | ctrl+m, ctrl+,    | Method: Create method before current |
| Create method after current  | ctrl+m, ctrl+.    | Method: Create method after current  |
| Create method after current  | ctrl+alt+shift+n  | Method: Create method after current  |
| Create method after first    | ctrl+m, ctrl+0    | Method: Create method after first    |
| Create protected method      | ctrl+m, ctrl+o    | Method: Create protected method      |
| Create private method        | ctrl+m, ctrl+i    | Method: Create private method        |
| Create method after last     | ctrl+m, ctrl+l    | Method: Create method after last     |
| Move method after first      | ctrl+m, 0         | Method: Move method after first      |
| Move method to protected     | ctrl+m, o         | Method: Move method to protected     |
| Move method to private       | ctrl+m, i         | Method: Move method to private       |
| Move method to last          | ctrl+m, l         | Method: Move method to last          |
| Move method up               | alt+-             | Method: Move method up               |
| Move method down             | alt+=             | Method: Move method down             |
| Go to next method            | alt+n             | Method: Go to next method            |
| Go to previous method        | alt+shift+n       | Method: Go to previous method        |
| Swap method start/end        | alt+ctrl+n        | Method: Swap method start/end        |
| Go to last method            | ctrl+m, ctrl+/    | Method: Go to last method            |
| Go to first method           | ctrl+m, ctrl+f    | Method: Go to first method           |
| Create method space          | ctrl+m, ctrl+n    | Method: Create method space          |
| Delete method                | ctrl+m, ctrl+d    | Method: Delete method                |
| Clone method                 | ctrl+m, ctrl+c    | Method: Clone method                 |
| Insert method name to mark   | ctrl+m, ctrl+m    | Method: Insert method name to mark   |
| Select current method        | ctrl+m, ctrl+s    | Method: Select current method        |
| Select current method body   | ctrl+m, s         | Method: Select current method body   |
| Comment all except current   | ctrl+m, ctrl+q    | Method: Comment all except current   |
| Uncomment all                | ctrl+m, q         | Method: Uncomment all                |


### Dependencies

- https://github.com/shagabutdinov/sublime-statement
- https://github.com/shagabutdinov/sublime-expression
- https://github.com/shagabutdinov/sublime-local-variable