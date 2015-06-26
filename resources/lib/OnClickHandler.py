# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details


class OnClickHandler():
    def __init__(self):
        self.clicks = {}
        self.context_menus = {}

    def click(self, button_ids):
        def decorator(f):
            if isinstance(button_ids, list):
                for button_id in button_ids:
                    self.clicks[button_id] = f
            else:
                self.clicks[button_ids] = f
            return f

        return decorator

    def context(self, button_ids):
        def decorator(f):
            if isinstance(button_ids, list):
                for button_id in button_ids:
                    self.context_menus[button_id] = f
            else:
                self.context_menus[button_ids] = f
            return f

        return decorator

    def serve(self, control_id, wnd):
        view_function = self.clicks.get(control_id)
        if view_function:
            wnd.control = wnd.getControl(control_id)
            wnd.control_id = control_id
            return view_function(wnd)
        # else:
        #     raise ValueError('OnClick for "{}"" has not been registered'.format(control_id))

    def serve_context(self, control_id, wnd):
        view_function = self.context_menus.get(control_id)
        if view_function:
            wnd.control = wnd.getControl(control_id)
            wnd.control_id = control_id
            return view_function(wnd)
        # else:
        #     raise ValueError('Context Menu for "{}"" has not been registered'.format(control_id))
