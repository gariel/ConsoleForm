#!/usr/bin/env python3

# Window controls for console

from math import ceil
import sys

#TODO: get this dinamicaly
HDIFF = 6
WDIFF = 12
CONSOLEX = 80
CONSOLEY = 25

class Widget:
	def __init__(self, d):
		self.id = d.get('id')
		self.name = d.get('name')
		self.type = d.get('type')
		self.value = d.get('value', '')
		self.parent = d.get('parent')
		self.width = int(d.get('width', 0) / WDIFF)
		self.height = int(d.get('height', 0) / HDIFF)
		self.description = d.get('description')
		self.signals = dict(d.get('signals', {}))
		self.parentw = None
		self.default()
		self.c = Console()

	def default(self):
		pass

	def call_signal(self, w, name):
		if self.signals.get(name):
			if hasattr(w, self.signals[name]):
				getattr(w, self.signals[name])()

	def get_height(self):
		return self.height or len(self.stl())

	def get_width(self):
		return max([self.width, len(self.value)] + (self.parentw and [self.parentw.width, len(self.parentw.value)] or []))

	def __repr__(self):
		return '\n'.join([str(s) for s in self.stl()])

	def stl(self):
		raise NotImplementedError

	def centralize(self, ret):
		width = self.get_width()
		for r in ret:
			r = r.center(width)

		ret = [r.center(width) for r in ret]
		ret = ([' ' * width] * (int((self.height - len(ret))/2))) + ret
		ret += [' ' * width] * int(self.height - len(ret))
		return ret

	def active(self, w, args):
		pass

class Container(Widget):
	def __init__(self, d):
		Widget.__init__(self, d)
		self.children = []

	def add(self, child):
		self.children.append(child)

	def get_height(self):
		return max([c.get_height() for c in self.children] + [self.height])

	def get_width(self):
		return max([c.get_width() for c in self.children] + [self.width])

class WButton(Widget):
	def stl(self):
		return self.centralize([" %s(%s)" % (self.id, self.width and self.value[:self.width -2 -(len(str(self.id)) + 1)].center(self.width -2 -(len(str(self.id)) + 1)) or self.value)])

	def active(self, w, args):
		self.call_signal(w, 'clicked')

class WLabel(Widget):
	def stl(self):
		return self.centralize([" %s " % (self.width and self.value[:self.width -2].ljust(self.width -2) or self.value)])

class WEntry(Widget):
	def default(self):
		self.width = max([self.width, 15])

	def stl(self):
		return self.centralize(["%s[%s]" % (self.id, self.value[:self.get_width()].ljust(self.get_width()-(len(str(self.id)) + 2)))])

	def active(self, w, args):
		if len(args) > 1:
			self.value = ' '.join(args[1:])
			return
		#self.c.show_out(["Edit %s (%s): %s" % (self.description and w.tree.get(self.description, '').value.strip().strip(':') or self.name, self.id, self.value)])
		#self.value = self.c.read("%s: " % (self.description and w.tree.get(self.description, '').value.strip().strip(':') or self.name))

class WPassword(WEntry):
	def stl(self):
		return self.centralize(["%s[%s]" % (self.id, ("*" * min(self.get_width(), len(self.value))).ljust(self.get_width()-(len(str(self.id)) + 2)))])

class WVBox(Container):
	def get_height(self):
		return max([sum([c.get_height() for c in self.children]), self.height])

	def stl(self):
		def reduce(f, l):
			if l:
				r = l[0]
				for i in range(1, len(l)):
					r = f(r, l[i])
				return r
			return None

		s = reduce(lambda x, y: x + y, [c.stl() for c in self.children])
		self.width = max([self.width] + [len(d) for d in s])
		s = reduce(lambda x, y: x + y, [c.stl() for c in self.children])
		return self.centralize(s)

class WHBox(Container):
	def get_width(self):
		return max([sum([c.get_width() for c in self.children]), self.width])

	def stl(self):
		l = []
		sp = 0
		for i in self.children:
			r = i.stl()
			for d in range(len(r)):
				if len(l) <= d:
					l.append(" " * sp) # All teoricaly should have the same size
				l[d] = "%s%s" % (l[d].ljust(sp), r[d])
			sp = max([len(k) for k in l] or [0])
		return self.centralize(l)

def make_widget(t):
	t = t.lower()
	types = {
		'vbox': WVBox,
		'hbox': WHBox,
		'entry': WEntry,
		'button': WButton,
		'label': WLabel,
		'password': WPassword
	}
	if t not in types:
		raise NotImplementedError
	return types[t]

class Window:
	def __init__(self, layout):
		self.layout = layout
		self.border = {
			'left': '|',
			'right': '|',
			'top': '-',
			'title': '-',
			'title_left': '|',
			'title_right': '|',
			'botton': '-',
			'corner_11': '.',
			'corner_12': '.',
			'corner_21': '|',
			'corner_22': '|',
			'corner_31': "'",
			'corner_32': "'",
		}
		self.title = ""
		self.width, self.height = 20, 20
		self.tree = {}
		self.root = None
		self.state = None
		self.c = Console()
		self.out = []
		self.modal = False
		self.default = ""

	def show(self):
		self.load()
		self.state = 'visible'
		self.start()

	def destroy(self):
		self.state = 'destroyed'

	def start(self):
		while self.state == 'visible':
			self.update_view()
			self.console()

			v = self.c.read("> ").split(' ')
			av = None
			if v[0] in ('q', 'quit', 'exit'): sys.exit()
			try: av = int(v[0] or self.default)
			except: pass

			if av in self.tree:
				self.tree[av].active(self, v)


	def load(self):
		if not self.tree:
			l = self.layout[:]
			ininfinite = True
			while ininfinite:
				ininfinite = []
				for i in range(len(l)):
					if not l[i].get('parent') in list(self.tree.keys()) + [None]:
						continue
					g = make_widget(l[i].get('type'))(l[i])
					ininfinite.append(i)
					self.tree[g.id] = g
					if not g.parent:
						assert not self.root
						self.root = g
						continue
					self.tree[g.parent].add(g)
					g.parentw = self.tree[g.parent]
					setattr(self, g.name, g)

				ininfinite.sort()
				ininfinite.reverse()
				for i in ininfinite:
					del l[i]

	def update_view(self):
		line = lambda c1, c2, li, wi: (c1, (li * int(ceil((wi - len(c1) - len(c2)) / float(len(li)))))[:(wi - len(c1) - len(c2))], c2)
		h, w = self.height / WDIFF, self.width / HDIFF
		b = self.border

		widgets_lines = self.root.stl()

		# ----------------------------------

		mcl = max([len(b['corner_11']), len(b['corner_21']), len(b['corner_31']), len(b['left']), len(b['title_left'])])
		mcr = max([len(b['corner_12']), len(b['corner_22']), len(b['corner_32']), len(b['right']), len(b['title_right'])])
		w = max([len(wl) + mcl + mcr + 2 for wl in widgets_lines] + [w])

		if self.title: h -= 2
		if h > len(widgets_lines): widgets_lines.extend([""] * (h - len(widgets_lines)))

		self.out = []

		b['corner_11'] = b['corner_11'] or b['top']
		b['corner_12'] = b['corner_12'] or b['top']
		b['corner_21'] = b['corner_21'] or b['title'] or b['top']
		b['corner_22'] = b['corner_22'] or b['title'] or b['top']
		b['corner_31'] = b['corner_31'] or b['botton']
		b['corner_32'] = b['corner_32'] or b['botton']
		b['title_left'] = b['title_left'] or b['left']
		b['title_right'] = b['title_right'] or b['right']
		b['title'] = b['title'] or b['top'] or b['botton'] or ' '

		if b['top']:
			self.out.append("%s%s%s" % line(b['corner_11'], b['corner_12'], b['top'], w))

		if self.title:
			d = len(b['title_left']) + len(b['title_right']) + 2
			self.out.append("%s %s %s" % (b['title_left'], self.title[:w - d].center(w - d), b['title_right']))
			self.out.append("%s%s%s" % line(b['corner_21'], b['corner_22'], b['title'], w))

		for wl in widgets_lines:
			d = len(b['left']) + len(b['right']) + 2
			self.out.append("%s %s %s" % (b['left'], wl[:w - d].ljust(w - d), b['right']))
		self.out.append("%s%s%s" % line(b['corner_31'], b['corner_32'], b['botton'], w))

	def console(self):
		if self.modal:
			last = self.c.last
			s = int(CONSOLEY/2 - len(self.out) / 2)
			for q in range(len(self.out)):
				last[s + q] = last[s + q].center(CONSOLEX)
				a = self.out[q].center(CONSOLEX)
				last[s + q] = "%s%s%s" % (last[s + q][:len(last[s + q]) - len(a.lstrip())], self.out[q], last[s + q][len(a.lstrip())-1:])

			self.out = last

		self.c.show_out(self.out)

class MsgBox(Window):
	def __init__(self, msg, title = "Message"):
		Window.__init__(self, [
			{'id': 99, 'name': 'mp1', 'type': 'vbox'},
			{'id': 10, 'name': 'l1', 'type': 'label', 'value': msg, 'parent': 99},
			{'id': 1, 'name': 'bOk', 'width': 10, 'type': 'button', 'value': 'OK', 'parent': 99, 'signals': {'clicked': 'on_bt_ok_clicked'}}
			])
		self.title = title
		self.modal = True
		self.default = 1

	def on_bt_ok_clicked(self):
		self.destroy()

class Console(object):
	instance = None

	def __new__(self):
		if not Console.instance:
			Console.instance = object.__new__(self)
			self.last = []
		return Console.instance

	def read(self, s):
		return input(s)

	def show_out(self, value):
		for d in range(len(value)):
			value[d] = value[d].center(CONSOLEX)
		d = CONSOLEY - len(value)
		value = [""]*int(d/2) + value
		value = value + [""] * (CONSOLEY - len(value))
		self.last = value
		print('\n'.join(value))

if __name__ == "__main__":
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
