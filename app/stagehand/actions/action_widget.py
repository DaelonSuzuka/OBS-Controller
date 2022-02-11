from qtstrap import *
from qtstrap.extras.code_editor import CodeEditor
from stagehand.sandbox import Sandbox
import qtawesome as qta
from .action_editor import ActionEditorDialog
from .action_trigger import ActionTrigger
from .action_filter import FilterStack, ActionFilter
import abc
import json


class ActionItem:
    @classmethod
    def get_subclasses(cls):
        return {c.name: c for c in cls.__subclasses__()}

    @classmethod
    def get_item(cls, name):
        return cls.get_subclasses()[name]

    @abc.abstractmethod
    def __init__(self, changed) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def set_data(self, data: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def get_data(self) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    def reset(self):
        pass


class CodeLine(CodeEditor):
    def __init__(self, changed):
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setFixedHeight(28)
        self.textChanged.connect(changed)

        words = [
            //
        ]

        self.completer = QCompleter(words, self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)

        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event: PySide2.QtCore.QEvent):
        keys = [Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab]
        if self.completer.popup().isVisible():
            if event.key() in keys:
                event.ignore()
                return
    
        if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
            event.accept()
            return

        super().keyPressEvent(event)

        self.completer.setCompletionPrefix(self.text_under_cursor())
        index = self.completer.completionModel().index(0, 0)
        self.completer.popup().setCurrentIndex(index)

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

    def text(self):
        return self.toPlainText()


class SandboxAction(QWidget, ActionItem):
    name = 'sandbox'

    def __init__(self, changed, owner=None):
        super().__init__()
        
        self.owner = owner
        self.action = CodeLine(changed)
        self.changed = changed

        self.edit_btn = QPushButton('', clicked=self.open_editor, icon=QIcon(qta.icon('fa5.edit')))

        with CHBoxLayout(self, margins=(0,0,0,0)) as layout:
            layout.add(self.action)
            layout.add(self.edit_btn)
    
    def open_editor(self, *_):
        self.data['action'] = self.action.text()
        self.data['name'] = self.owner.name
        self.editor = ActionEditorDialog(self.data, self.owner)
        self.editor.accepted.connect(self.on_accept)
        self.editor.open()

    def on_accept(self):
        text = self.editor.editor.toPlainText()
        self.action.setText(text)
        self.action.setDisabled('\n' in text)
        self.owner.label.setText(self.editor.label.text())
        self.changed()

    def set_data(self, data: dict):
        self.data = data
        if 'action' in data:
            self.action.setText(data['action'])
        self.action.setDisabled('\n' in self.action.text())

    def get_data(self):
        return {
            'action': self.action.text()
        }

    def reset(self):
        self.action.clear()
        self.action.setDisabled(False)

    def run(self):
        # Sandbox().run(self.action.text(), this=self.parent.this)
        Sandbox().run(self.action.text())


class Action(QWidget):
    changed = Signal()

    def __init__(self, changed, action_type='sandbox', action='', owner=None):
        super().__init__()

        self.owner = owner
        self.type = QComboBox()
        self.action = SandboxAction(changed, owner)
        self._changed = changed
        self.data = None
        self.this = None
        
        for action in ActionItem.__subclasses__():
            self.type.addItem(action.name)
        
        self.type.currentIndexChanged.connect(changed)
        self.type.currentIndexChanged.connect(self.type_changed)

        self.action_box = CHBoxLayout(margins=(0,0,0,0))

        with CHBoxLayout(self, margins=(0,0,0,0)) as layout:
            layout.add(self.type)
            layout.add(self.action_box, 1)

    def type_changed(self):
        if self.action:
            self.action.deleteLater()
            self.action = None
        self.action = ActionItem.get_item(self.type.currentText())(self._changed, self.owner)
        if self.data:
            self.action.set_data(self.data)
        self.action_box.add(self.action)

    def set_data(self, data):
        self.data = data
        if 'action_type' not in data:
            data['action_type'] = 'sandbox'

        self.type.setCurrentText(data['action_type'])
        self.type_changed()

    def get_data(self):
        return  {
            'action_type': self.type.currentText(),
            **self.action.get_data(),
        }

    def run(self):
        self.action.run()

    def reset(self):
        self.type.setCurrentText('sandbox')
        self.action.reset()


class ActionWidget(QWidget):
    changed = Signal()

    @staticmethod
    def from_data(data):
        name = data['name']
        label = data['label']
        action = data['action']
        action_type = data['type']

        return ActionWidget()

    def __init__(self, name='', group=None, trigger=False, data=None, changed=None, parent=None):
        super().__init__(parent=parent)

        self.name = name
        label = name
        action_type = 'sandbox'
        action = ''

        if data:
            self.name = data['name']
            label = data['label']
            action = data['action']
            if 'type' in data:
                action_type = data['type']

        self.run_btn = QPushButton('', clicked=self.run, icon=QIcon(qta.icon('fa5.play-circle')))

        self.label = LabelEdit(label, changed=self.on_change)
        self.action = Action(self.on_change, action_type, action, owner=self)
        self.trigger = ActionTrigger(self.on_change, run=self.run, owner=self)
        self.filter = ActionFilter(self.on_change, owner=self)

        if trigger:
            self.trigger.enabled.setChecked(True)
            self.filter.enabled.setChecked(True)

        if group:
            group.register(self)

        if changed:
            self.changed.connect(changed)

        with CHBoxLayout(self, margins=(0,0,0,0)) as layout:
            layout.add(self.label)
            layout.add(VLine())
            layout.add(self.trigger, 1)
            layout.add(self.filter)
            layout.add(self.action, 2)
            layout.add(self.run_btn)

    def get_data(self):
        return {
            'name': self.name,
            'label': self.label.text(),
            **self.action.get_data(),
            **self.trigger.get_data(),
            **self.filter.get_data(),
        }

    def set_data(self, data):
        self.label.setText(data['label'])
        self.action.set_data(data)
        self.trigger.set_data(data)
        self.filter.set_data(data)
        self.on_change()

    def on_change(self):
        self.filter.setVisible(self.filter.enabled.isChecked())
        self.trigger.setVisible(self.trigger.enabled.isChecked())
        self.changed.emit()

    def contextMenuEvent(self, event: PySide2.QtGui.QContextMenuEvent) -> None:
        menu = QMenu()
        menu.addAction(QAction('Run', self, triggered=self.run))
        menu.addAction(QAction('Rename', self, triggered=self.label.start_editing))
        menu.addAction(QAction('Copy', self, triggered=self.copy))
        menu.addAction(QAction('Paste', self, triggered=self.paste))
        menu.addAction(self.trigger.enabled)
        menu.addAction(self.filter.enabled)
        menu.addAction(QAction('Reset', self, triggered=self.reset))
        menu.exec_(event.globalPos())

    def copy(self):
        data = {
            **self.action.get_data(),
            **self.trigger.get_data(),
            **self.filter.get_data(),
        }
        QClipboard().setText(json.dumps(data))

    def paste(self):
        data = json.loads(QClipboard().text())
        self.action.set_data(data)
        self.trigger.set_data(data)
        self.filter.set_data(data)

    def reset(self):
        self.label.setText(self.name)
        self.action.reset()
        self.trigger.reset()
        self.filter.reset()
        self.on_change()

    def run(self):
        if self.filter.check_filters():
            self.action.run()