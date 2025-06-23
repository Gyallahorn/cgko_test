import sqlite3
import sqlalchemy as db 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import  Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMessageBox,QHBoxLayout,QLineEdit,QLabel, QWidget, QMainWindow,QTableWidgetItem, QPushButton, QListWidget, QTableWidget , QVBoxLayout
import sys 

engine =  db.create_engine('sqlite:///library.db')
Session = sessionmaker(autoflush=False, bind=engine)



class Base(DeclarativeBase): pass
class Book(Base):
    __tablename__  = 'library'

    id = Column(Integer, primary_key = True, index = True)
    author = Column(String)
    publisher = Column(String)
    name = Column(String)
    year = Column(Integer)

Base.metadata.create_all(bind=engine)



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
        widget = QWidget()
        layout = QVBoxLayout()


        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Автор","Название", "Год", "Издательство"])
        layout.addWidget(self.table)
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

        self.add_btn.clicked.connect(self.add_book)
        self.edit_btn.clicked.connect(self.edit_book)
        self.delete_btn.clicked.connect(self.delete_book)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        
        self.table.cellClicked.connect(self.set_inputs)
        

        layout.addLayout(button_layout)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
    def set_inputs(self, row, column):
        

        self.inputs[0].setText (self.table.item(row, 1).text())
        self.inputs[1].setText (self.table.item(row, 2).text())
        self.inputs[2].setText (self.table.item(row, 4).text())  
        self.inputs[3].setText (self.table.item(row, 3).text())  
          
          
        
        
    def load_books(self):
        _books = self.session.query(Book).all()    
        for i in _books:
            position = self.table.rowCount()
            self.table.insertRow(position)
            self.table.setItem( position, 0, QTableWidgetItem(str(i.id)))
            self.table.setItem( position, 1, QTableWidgetItem(str(i.author)))
            self.table.setItem( position, 2, QTableWidgetItem(str(i.name)))
            self.table.setItem( position, 3, QTableWidgetItem(str(i.year)))
            self.table.setItem( position, 4, QTableWidgetItem(str(i.publisher)))
            
    def add_book(self):
        try:
            author, name, publisher, year = [field.text() for field in self.inputs]
            new_book = Book(author=author, name=name, publisher=publisher, year=int(year))
            self.session.add(new_book)
            self.session.commit()
            self.clear_inputs()
            
            row = self.table.rowCount() 
            self.table.insertRow(row) 
            
            self.table.setItem( row , 0, QTableWidgetItem(str(new_book.id)))
            self.table.setItem( row , 1, QTableWidgetItem(str(new_book.name)))
            self.table.setItem(row , 2, QTableWidgetItem(str(new_book.author)))
            self.table.setItem( row, 3, QTableWidgetItem(str(new_book.year)))
            self.table.setItem( row , 4, QTableWidgetItem(str(new_book.publisher)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def edit_book(self):
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
                
                    self.table.setItem(selected, 1 ,QTableWidgetItem(self.inputs[0].text()) )
                    self.table.setItem(selected, 2 ,QTableWidgetItem(self.inputs[1].text()) )
                    self.table.setItem(selected, 3 ,QTableWidgetItem(self.inputs[3].text()) )
                    self.table.setItem(selected, 4 ,QTableWidgetItem(self.inputs[2].text()) )
                    self.clear_inputs()        
                    # self.load_books()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", str(e))

    def delete_book(self):
        selected = self.table.currentRow()
        if selected >= 0:
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
window.show() 


app.exec()