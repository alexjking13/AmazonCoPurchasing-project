#! /usr/bin/python3

import os
import sys
import re
import configparser as cfg
import decimal
import json
import random as rnd
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtCore import QRect, QCoreApplication, QMetaObject
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QAction,
                            QDialog, QMessageBox, QTableWidget,QListWidget,QGridLayout, QTableWidgetItem,
                            QVBoxLayout, QPushButton, QLabel, QRadioButton, QTextEdit,
                            QMenuBar, QMenu, QStatusBar)
from PyQt5.QtGui import QIcon, QPixmap, QTextCharFormat, QFont

project_root = re.sub('(?<=Amazon-CoPurchasing).*', '', os.path.abspath('.'))
config_path = os.path.join(project_root, 'etc', 'config.ini')

# Add reference path to access files in /lib/ (JR)
sys.path.insert(0, os.path.join(project_root, 'lib'))

from acpN4J import N4J
from acpAlgos import CollaborativeFilter

category_path = os.path.join(project_root,'etc','node_property_keys.json')
x=open(category_path)
dict_of_cats = json.load(x)

config = cfg.ConfigParser()
config.read(config_path)

ui_path = os.path.join(project_root, 'ui')
ui_main_window = os.path.join(ui_path, 'Mockup_UI_query_program.ui')
ui_qss  = os.path.join(project_root, 'etc', 'style.qss')

Ui_MainWindow, QtBaseClass = uic.loadUiType(ui_main_window)

class AcpApp(QMainWindow):
  
    def __init__(self):
        super(AcpApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.loadList()
        self.ui.listWidget.itemClicked.connect(self.Clicked1)
        self.ui.listWidget.itemSelectionChanged.connect(self.node_source_changed)
        self.ui.listWidget_2.itemClicked.connect(self.Clicked2)
        self.ui.listWidget_2.itemSelectionChanged.connect(self.property_key_changed)
        self.ui.listWidget_3.itemClicked.connect(self.Clicked3)
        self.ui.listWidget_3.itemSelectionChanged.connect(self.condition_op_changed)
        self.ui.pushButton.clicked.connect(self.Clicked4)
        self.ui.btn_gen_cf_recs.clicked.connect(self.btn_gen_cf_recs_clicked)
        self.ui.btn_reset.clicked.connect(self.reset_ui)
        self.products = dict()
        self.n4 = N4J()

    def loadList(self):
        self.ui.listWidget.clear()
        self.ui.listWidget.addItem('PRODUCT')
        self.ui.listWidget.addItem('CATEGORY')
        self.ui.listWidget.addItem('CUSTOMER')
        self.ui.listWidget.addItem('REVIEW')
        self.ui.listWidget_3.addItem('<')
        self.ui.listWidget_3.addItem('<=')
        self.ui.listWidget_3.addItem('=')
        self.ui.listWidget_3.addItem('>=')
        self.ui.listWidget_3.addItem('>')
    
    def style_query_results_table(self, data_dims, header_vals):
        # Expects to receive a two-value tuple in the form (row_count, column_count) (JR)
        self.ui.tbl_query_results.horizontalHeader().setFixedHeight(50)
        self.ui.tbl_query_results.setColumnCount(data_dims[1])
        self.ui.tbl_query_results.setRowCount(data_dims[0])
        self.ui.tbl_query_results.setHorizontalHeaderLabels(header_vals)
        self.ui.tbl_query_results.setColumnWidth(0, int(round(self.ui.tbl_query_results.width() * 0.25, 0)))
        self.ui.tbl_query_results.setColumnWidth(1, self.ui.tbl_query_results.width() - self.ui.tbl_query_results.columnWidth(0))
        self.ui.tbl_query_results.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.Alignment(QtCore.Qt.TextWordWrap))
    
    def reset_query_results_table(self):
        for i in reversed(range(self.ui.tbl_query_results.rowCount())):
            self.ui.tbl_query_results.removeRow(i)

    def reset_cf_results_table(self):
        for i in reversed(range(self.tbl_cf_recs.rowCount())):
            self.ui.tbl_cf_recs.removeRow(i)

    def reset_ui(self):
        # Empty out downstream elements (JR)
        self.ui.listWidget.clearSelection()
        self.ui.listWidget_2.clear()
        self.ui.textEdit.clear()
        # self.ui.textEdit_2.clear()
        self.ui.lst_cf_recs.clear()
        self.reset_query_results_table()
        self.reset_cf_results_table()
        

        #DEMO CODE NOT NECESSARY FOR NOW
                # try:
                #     results = self.executeQuery(sql_str)
                #     #print(results)
                #     for row in results:
                #         self.ui.listWidget.addItem(row[0])
                #         self.ui.stateList_2.addItem(row[0])
                # except:
                #     print("Query failed!")
                # self.ui.listWidget.setCurrentIndex(0)
                # self.ui.listWidget.clearEditText()
                # self.ui.stateList_2.setCurrentIndex(-1)
                # self.ui.stateList_2.clearEditText()

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1039, 805)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.listWidget = QListWidget(self.centralwidget)
        self.listWidget.setObjectName(u"listWidget")

        self.gridLayout.addWidget(self.listWidget, 1, 0, 1, 1)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 2, 1, 1)

        self.listWidget_2 = QListWidget(self.centralwidget)
        self.listWidget_2.setObjectName(u"listWidget_2")

        self.gridLayout.addWidget(self.listWidget_2, 1, 3, 1, 1)

        self.textEdit = QTextEdit(self.centralwidget)
        self.textEdit.setObjectName(u"textEdit")

        self.gridLayout.addWidget(self.textEdit, 2, 0, 1, 1)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 2, 1, 1, 1)

        self.listWidget_3 = QListWidget(self.centralwidget)
        self.listWidget_3.setObjectName(u"listWidget_3")

        self.gridLayout.addWidget(self.listWidget_3, 2, 3, 1, 1)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMouseTracking(False)

        self.gridLayout.addWidget(self.pushButton, 3, 1, 1, 2)

        # self.textEdit_2 = QTextEdit(self.centralwidget)
        # self.textEdit_2.setObjectName(u"textEdit_2")

        # self.gridLayout.addWidget(self.textEdit_2, 4, 0, 1, 4)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1039, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Enter a query below", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"->", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Add condition", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Go!", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi



    category_item = ''
    value_item = ''
    condition = '' 

    def Clicked1(self,item):
        listofitems=[]
        self.ui.listWidget_2.clear()
        if (item.text() == 'CUSTOMER'):
            listofitems = [z for x,y in dict_of_cats.items() if x == 'CUSTOMER' for z in y]
        if (item.text() == 'CATEGORY'):
            listofitems = [z for x,y in dict_of_cats.items() if x == 'CATEGORY' for z in y] 
        if (item.text() == 'PRODUCT'):
            listofitems = [z for x,y in dict_of_cats.items() if x == 'PRODUCT' for z in y]          
        if (item.text() == 'REVIEW'):
            listofitems = [z for x,y in dict_of_cats.items() if x == 'REVIEW' for z in y]          
        
        for it in listofitems:
            self.ui.listWidget_2.addItem(it)
        global category_item
        category_item = item.text()
        
    def Clicked2(self,item):
        global value_item
        value_item = item.text()

    def Clicked3(self,item):
        global condition
        condition = item.text()

    def Clicked4(self):
        n=N4J()
        # self.ui.textEdit_2.clear()

        global numeric_val
        numeric_val = self.ui.textEdit.toPlainText()
      
        self.products = n.get_rating_greater(rating=numeric_val,operand=condition)
        # self.ui.textEdit_2.append(str(self.products.values))

        self.style_query_results_table(self.products.shape, list(self.products.columns))

        for row_idx in range(self.products.shape[0]):
            for col_idx in range(0, self.products.shape[1]):
                self.ui.tbl_query_results.setItem(row_idx, col_idx, QTableWidgetItem(str(self.products.values[row_idx, col_idx])))

    # def Clicked3(self,item):
	#     QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())

    #def populate_List_2(self,MainWindow):

    def node_source_changed(self):
        # Empty out downstream elements (JR)
        self.ui.listWidget_2.clear()
        self.ui.listWidget_3.clearSelection()
        self.ui.textEdit.clear()
        # self.ui.textEdit_2.clear()
        self.ui.lst_cf_recs.clear()
        self.reset_query_results_table()
        self.reset_cf_results_table()

    def property_key_changed(self):
        # Empty out downstream elements (JR)
        self.ui.listWidget_3.clearSelection()
        self.ui.textEdit.clear()
        # self.ui.textEdit_2.clear()
        self.ui.lst_cf_recs.clear()
        self.reset_query_results_table()
        self.reset_cf_results_table()

    def condition_op_changed(self):
        # Empty out downstream elements (JR)
        self.ui.textEdit.clear()
        # self.ui.textEdit_2.clear()
        self.ui.lst_cf_recs.clear()
        self.reset_query_results_table()
        self.reset_cf_results_table()


    def btn_gen_cf_recs_clicked(self):
        # Generate list of recommendations based on the subset returned to the UI (JR)
        self.ui.lst_cf_recs.clear()

        if len(self.products) == 0:
            self.ui.lst_cf_recs.addItem('No products to derive recommendations from.')
        
        else:
            wtd_mtx = self.n4.get_cf_set_from_asins(list(set(x['asin'] for x in self.products)))
            cid = rnd.sample(list(wtd_mtx.columns.values), 1)[0]

            cf = CollaborativeFilter(wtd_mtx, cid)
            recs = cf.recommend_product(cid, 5)
            rec_titles = self.n4.get_titles_from_asins(recs)

            for row in rec_titles:
                self.ui.lst_cf_recs.addItem(row)
       


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AcpApp()
    window.show()

    with open(ui_qss, 'r') as f:
        style = f.read()
        app.setStyleSheet(style)

    sys.exit(app.exec_())