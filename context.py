import sublime
import sublime_plugin

from Context.base import Base
from . import method

class InMethodDefinition(Base):

  def on_query_context(self, view, *args):
    return self._check_sel('in_method_definition', self._check_point, view,
      *args)

  def _check_point(self, view, sel):
    info = method.extract_method(view, sel.a)
    if info == None:
      return False

    start = info['start']
    value = view.substr(sublime.Region(start, info['body_start'])).strip()
    return start < sel.a and sel.b < start + len(value)

class InMethod(Base):
  def on_query_context(self, view, *args):
    return self._check_sel('in_method', self._check_point, view, *args)

  def _check_point(self, view, sel):
    info = method.extract_method(view, sel.a)
    if info == None:
      return False

    return info['start'] < sel.a and sel.b < info['end']

class MethodName(Base):
  def on_query_context(self, view, *args):
    return self._check_sel('method_name', self._get_method_name, view, *args)

  def _get_method_name(self, view, sel):
    info = method.extract_method(view, sel.a)
    if info == None:
      return None

    return info['name']