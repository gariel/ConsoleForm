# ConsoleForm

An old project that draws windows by a definition.
The original project was to draw in other frameworks too, like Qt

### Python 3
For python 3 use the `python3` branch, it will be merged soon.

### Sample:
```python
layout = [
    {'id': 99, 'name': 'mp1', 'type': 'hbox', 'width': 20, 'height': 20},
    {'id': 10, 'name': 'm1', 'type': 'vbox', 'parent': 99},
    {'id': 20, 'name': 'm2', 'type': 'vbox', 'parent': 99},
    {'id': 13, 'name': 'l1', 'type': 'label', 'value': 'User:', 'parent': 10},
    {'id': 15, 'name': 'l2', 'type': 'label', 'value': 'Pass:', 'parent': 10},
    {'id': 1, 'name': 'user', 'type': 'entry', 'parent': 20, 'description': 13},
    {'id': 2, 'name': 'password', 'type': 'password', 'parent': 20, 'description': 15},
    {'id': 5, 'name': 'cancel', 'type': 'button', 'value': 'Cancel', 'parent': 10, 'signals': {'clicked': 'destroy'}},
    {'id': 3, 'name': 'ok', 'type': 'button', 'value': 'Login', 'parent': 20, 'signals': {'clicked': 'on_bt_ok_clicked'}},
]
class Login(Window):
    def __init__(self, l):
        Window.__init__(self, l)
        self.title = "Login Window"
        self.default = 3

    def on_bt_ok_clicked(self):
        MsgBox('Wrong user or password.', "Error").show()

w = Login(layout)
w.show()
```
```

                    ,--------------------------------------,
                    |             Login Window             |
                    |--------------------------------------|
                    |   User:   1[gabriel                ] |
                    |   Pass:   2[***********************] |
                    |  5(Cancel)         3(Login)          |
                    '--------------------------------------'

```
```

                    ,----,---------------------------,-----,
                    |    |           Error           |     |
                    |----|---------------------------|-----|
                    |   U|  Wrong user or password.  |   ] |
                    |   P|            1(OK)          |***] |
                    |  5('---------------------------'     |
                    '--------------------------------------'

```
