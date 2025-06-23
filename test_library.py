
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

from PyQt6.QtWidgets import (QApplication, QHeaderView, QDialogButtonBox, QDialog,
                             QMessageBox, QHBoxLayout, QLineEdit, QLabel, QWidget,
                             QMainWindow, QTableWidgetItem, QPushButton, QListWidget,
                             QTableWidget, QVBoxLayout)
import sys

engine = db.create_engine('sqlite:///library.db')
Session = sessionmaker(autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = 'library'

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String)
    publisher = Column(String)
    name = Column(String)
    year = Column(Integer)


Base.metadata.create_all(bind=engine)


class InputWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить книгу")

        layout = QVBoxLayout()

        self.fields = []
        labels = ["Автор", "Название", "Издательство", "Год"]

        for text in labels:
            row = QHBoxLayout()
            label = QLabel(text)
            input_field = QLineEdit()
            self.fields.append(input_field)

            row.addWidget(label)
            row.addWidget(input_field)
            layout.addLayout(row)

        # Кнопки OK / Cancel
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_data(self):
        return [field.text() for field in self.fields]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.session = Session()

        self.setWindowTitle("My App")

        self.build()
        self.load_books()

    # def index_changed(self, i):
    #     print(i.text())

    # def text_changed(self, s):
    #     print(s)

    def build(self):

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Автор", "Название", "Год", "Издательство"])
        layout.addWidget(self.table)

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 80)

        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 80)

        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)

        container = QWidget()
        container.setLayout(layout)
        form_layout = QHBoxLayout()

        self.inputs = [QLineEdit() for _ in range(4)]
        labels = ["Автор", "Название", "Издательство", "Год"]

        for label_text, input_field in zip(labels, self.inputs):
            form_layout.addWidget(QLabel(label_text))
            form_layout.addWidget(input_field)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")

        self.add_btn.clicked.connect(self.open_add_dialog)
        self.edit_btn.clicked.connect(self.edit_book)
        self.delete_btn.clicked.connect(self.delete_book)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)

        self.table.cellClicked.connect(self.set_inputs)

        layout.addLayout(button_layout)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def set_inputs(self, row, column):

        self.inputs[0].setText(self.table.item(row, 1).text())
        self.inputs[1].setText(self.table.item(row, 2).text())
        self.inputs[2].setText(self.table.item(row, 4).text())
        self.inputs[3].setText(self.table.item(row, 3).text())

    def load_books(self):
        _books = self.session.query(Book).all()

        self.table.setRowCount(0)
        for i in _books:
            position = self.table.rowCount()
            self.table.insertRow(position)
            self.table.setItem(position, 0, QTableWidgetItem(str(i.id)))
            self.table.setItem(position, 1, QTableWidgetItem(str(i.author)))
            self.table.setItem(position, 2, QTableWidgetItem(str(i.name)))
            self.table.setItem(position, 3, QTableWidgetItem(str(i.year)))
            self.table.setItem(position, 4, QTableWidgetItem(str(i.publisher)))

    def open_add_dialog(self):

        dialog = InputWindow()
        if dialog.exec():
            try:
                author, name, publisher, year = dialog.get_data()
                new_book = Book(author=author, name=name,
                                publisher=publisher, year=int(year))
                self.session.add(new_book)
                self.session.commit()
                self.clear_inputs()

                row = self.table.rowCount()
                self.table.insertRow(row)

                self.table.setItem(row, 0, QTableWidgetItem(str(new_book.id)))
                self.table.setItem(
                    row, 1, QTableWidgetItem(str(new_book.author)))
                self.table.setItem(
                    row, 2, QTableWidgetItem(str(new_book.name)))
                self.table.setItem(
                    row, 3, QTableWidgetItem(str(new_book.year)))
                self.table.setItem(
                    row, 4, QTableWidgetItem(str(new_book.publisher)))
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", ('Проверьте ввод'))

    def edit_book(self):
        if not self.table.selectionModel().hasSelection():
            QMessageBox.warning(
                self, "Нет выбора", "Пожалуйста, выберите строку для редактирования.")
            return

        selected = self.table.currentRow()
        if selected >= 0:
            book_id = int(self.table.item(selected, 0).text())
            book = self.session.query(Book).get(book_id)
            if book:
                try:
                    book.author, book.name, book.publisher, book.year = [
                        field.text() if i < 3 else int(self.inputs[i].text())
                        for i, field in enumerate(self.inputs)
                    ]
                    self.session.commit()

                    self.table.setItem(
                        selected, 1, QTableWidgetItem(self.inputs[0].text()))
                    self.table.setItem(
                        selected, 2, QTableWidgetItem(self.inputs[1].text()))
                    self.table.setItem(
                        selected, 3, QTableWidgetItem(self.inputs[3].text()))
                    self.table.setItem(
                        selected, 4, QTableWidgetItem(self.inputs[2].text()))
                    self.clear_inputs()
                    # self.load_books()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", str(e))

    def delete_book(self):
        if not self.table.selectionModel().hasSelection():
            QMessageBox.warning(self, "Нет выбора",
                                "Пожалуйста, выберите строку для удаления.")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить выбранную строку?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        selected = self.table.selectionModel().selectedRows()[0].row()

        if reply == QMessageBox.StandardButton.Yes:
            book_id = int(self.table.item(selected, 0).text())
            book = self.session.query(Book).get(book_id)
            if book:
                self.session.delete(book)
                self.session.commit()
                self.table.removeRow(selected)

    def clear_inputs(self):
        for input_field in self.inputs:
            input_field.clear()


app = QApplication(sys.argv)


window = MainWindow()
window.resize(800, 600)
window.show()

sys.exit(app.exec())
