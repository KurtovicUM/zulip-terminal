from typing import Any, Tuple

import urwid

from config import get_key
from zulipterminal.ui_tools.boxes import WriteBox
from zulipterminal.ui_tools.buttons import (
    HomeButton,
    PMButton,
    StreamButton,
    UserButton
)
from zulipterminal.ui_tools.views import (
    MiddleColumnView,
    StreamsView,
    UsersView
)


class View(urwid.WidgetWrap):
    """
    A class responsible for providing the application's interface.
    """
    palette = {
        'default': [
                (None,           'light gray',    'black'),
                ('selected',     'light magenta', 'dark blue'),
                ('msg_selected', 'light red',     'black'),
                ('header',       'dark cyan',     'dark blue',  'bold'),
                ('custom',       'white',         'dark blue',  'underline'),
                ('content',      'white',         'black',      'standout'),
                ('name',         'yellow',        'black'),
                ('unread',       'black',         'light gray'),
                ('active',       'white',         'black'),
                ('idle',         'yellow',        'black')
                ],
        'light': [
                (None,           'black',        'white'),
                ('selected',     'white',        'dark blue'),
                ('msg_selected', 'dark blue',    'light gray'),
                ('header',       'white',        'dark blue',  'bold'),
                ('custom',       'white',        'dark blue',  'underline'),
                ('content',      'black',        'light gray', 'standout'),
                ('name',         'dark magenta', 'light gray', 'bold'),
                ],
        'blue': [
                (None,           'black',        'light blue'),
                ('selected',     'white',        'dark blue'),
                ('msg_selected', 'black',        'light gray'),
                ('header',       'black',        'dark blue',  'bold'),
                ('custom',       'white',        'dark blue',  'underline'),
                ('content',      'black',        'light gray', 'standout'),
                ('name',         'dark red',     'light gray', 'bold'),
                ]
                }

    def __init__(self, controller: Any) -> None:
        self.controller = controller
        self.model = controller.model
        self.client = controller.client
        self.users = self.model.users
        self.streams = self.model.streams
        self.write_box = WriteBox(self)
        super(View, self).__init__(self.main_window())

    def menu_view(self) -> Any:
        count = self.model.unread_counts.get('all_msg', 0)
        self.home_button = HomeButton(self.controller, count=count)
        count = self.model.unread_counts.get('all_pms', 0)
        self.pm_button = PMButton(self.controller, count=count)
        menu_btn_list = [
            self.home_button,
            self.pm_button,
            ]
        w = urwid.ListBox(urwid.SimpleFocusListWalker(menu_btn_list))
        return w

    def streams_view(self) -> Any:
        streams_btn_list = list()
        for stream in self.streams:
            unread_count = self.model.unread_counts.get(stream[1], 0)
            streams_btn_list.append(
                    StreamButton(
                        stream,
                        controller=self.controller,
                        view=self,
                        count=unread_count,
                    )
            )
        self.stream_w = StreamsView(streams_btn_list)
        w = urwid.LineBox(self.stream_w, title="Streams")
        return w

    def left_column_view(self) -> Any:
        left_column_structure = [
            (4, self.menu_view()),
            self.streams_view(),
        ]
        w = urwid.Pile(left_column_structure)
        return w

    def message_view(self) -> Any:
        w = MiddleColumnView(self.model, self.write_box)
        w = urwid.LineBox(w)
        return w

    def users_view(self) -> Any:
        users_btn_list = list()
        for user in self.users:
            unread_count = self.model.unread_counts.get(user['user_id'], 0)
            users_btn_list.append(
                    UserButton(
                        user,
                        controller=self.controller,
                        view=self,
                        color=user['status'],
                        count=unread_count
                    )
            )
        self.user_w = UsersView(urwid.SimpleFocusListWalker(users_btn_list))
        return self.user_w

    def right_column_view(self) -> Any:
        w = urwid.Frame(self.users_view())
        w = urwid.LineBox(w, title=u"Users")
        return w

    def main_window(self) -> Any:
        left_column = self.left_column_view()
        center_column = self.message_view()
        right_column = self.right_column_view()
        body = [
            ('weight', 3, left_column),
            ('weight', 10, center_column),
            ('weight', 3, right_column),
        ]
        self.body = urwid.Columns(body, focus_column=1)
        w = urwid.LineBox(self.body, title=u"Zulip")
        return w

    def keypress(self, size: Tuple[int, int], key: str) -> str:
        if self.controller.editor_mode:
            return self.controller.editor.keypress((20,), key)
        else:
            return super(View, self).keypress(size, get_key(key))
