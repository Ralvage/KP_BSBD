import sys
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from login import Ui_MainWindow
from cons_int import cUi_MainWindow
from man_int import mUi_MainWindow
from sys_int import sUi_MainWindow
from prob import prob_MainWindow
import psycopg2
import subprocess

def connect_bd (username, password):
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=username,
            password=password,
            host='localhost'
        )

        return conn
    except psycopg2.Error:
        print(f"Error database connection")

def aut_user (conn, username):
    values = ('consultant',
              'manager',
              'sysadmin')

    cursor = conn.cursor()
    for value in values:
        cursor.execute(
            f"SELECT rolname FROM pg_roles WHERE pg_has_role(rolname, '{value}', 'member') and rolname = '{username}';")
        result = cursor.fetchone()
        if result is not None:
            role = value
            break
    cursor.close()
    return role

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.login)


    def login(self):
        username = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()

        conn = connect_bd(username, password)
        role = aut_user(conn, username)
        if role == 'consultant':
            self.act_win = cWindow(username, conn)
            self.act_win.show()
            self.close()
        elif role == 'manager':
            self.act_win = mWindow(username, conn)
            self.act_win.show()
            self.close()
        elif role == 'sysadmin':
            self.act_win = sWindow(username, conn)
            self.act_win.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid role')

class cWindow(QMainWindow):
    def __init__(self, username, conn):
        super().__init__()
        self.cui = cUi_MainWindow()
        self.cui.setupUi(self)
        self.conn = conn

        self.cui.label_2.setText(username)
        self.cui.pushButton.clicked.connect(self.prob)
        self.cui.pushButton_2.clicked.connect(self.butt)

    def butt(self):
        if self.cui.pushButton_2.text() == 'Рейсы':
            self.cui.pushButton_2.setText('Пассажиры')
            self.reis()
        elif self.cui.pushButton_2.text() == 'Пассажиры':
            self.cui.pushButton_2.setText('Рейсы')
            self.pas()
        else:
            print('Error')

    def reis(self):
        self.cui.pushButton.setEnabled(True)
        self.cui.comboBox_3.setEnabled(True)

        self.cui.comboBox.clear()
        self.cui.comboBox_2.clear()

        self.cui.pushButton_4.disconnect()
        self.cui.pushButton_4.clicked.connect(self.seach)

        self.cui.tableWidget.setColumnCount(11)
        self.cui.tableWidget.setHorizontalHeaderLabels(
            ['Номер рейса', 'Город отправки', 'Аэропорт отправки', 'Город прибытия', 'Аэропорт прибытия',
             'Дата отправки', 'Время отправки', 'Дата прибытия', 'Время прибытия', 'Статус', 'Номер записи'])
        self.header1 = (
            ['f.id_flight', 'dc.name_of_city', 'dap.name_of_airport', 'ac.name_of_city', 'aap.name_of_airport',
             'fr.departure_date', 'fr.departure_time', 'fr.departure_time', 'fr.arrival_date', 's.name_of_states', 'fr.id_flight_records'])

        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM flight_select')
        rows = cursor.fetchall()
        cursor.close()

        self.count = []

        self.cui.tableWidget.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.cui.tableWidget.setItem(i, j, item)
                if j == len(row)-1:
                    self.count.append(str(value))

        self.header_labes = [self.cui.tableWidget.horizontalHeaderItem(i).text() for i in
                             range(self.cui.tableWidget.columnCount())]
        self.cui.comboBox.addItems(self.header_labes)
        self.cui.comboBox_2.addItems(self.header_labes)
        self.cui.comboBox_3.addItems(self.count)

    def pas(self):
        self.cui.pushButton.setEnabled(False)
        self.cui.comboBox_3.setEnabled(False)

        self.cui.comboBox.clear()
        self.cui.comboBox_2.clear()

        self.cui.pushButton_4.disconnect()
        self.cui.pushButton_4.clicked.connect(self.seach1)

        self.cui.tableWidget.setColumnCount(6)
        self.cui.tableWidget.setHorizontalHeaderLabels(
            ['Фамилия', 'Имя', 'Отчество', 'Серия паспорта', 'Номер паспорта', 'Номер телефона'])
        self.header1 = (
            ['passengers.lastname', 'passengers.firstname', 'passengers.patronymic', 'passengers.passport_serial', 'passengers,passport_number', 'passengers.phone_number'])

        cursor = self.conn.cursor()
        cursor.execute(f'SELECT lastname, firstname, patronymic, pgp_sym_decrypt(passport_serial::bytea, phone_number::text), pgp_sym_decrypt(passport_number::bytea, phone_number::text), phone_number FROM passengers')
        rows = cursor.fetchall()
        cursor.close()

        self.count = []

        self.cui.tableWidget.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.cui.tableWidget.setItem(i, j, item)
                if j == len(row) - 1:
                    self.count.append(str(value))

        self.header_labes = [self.cui.tableWidget.horizontalHeaderItem(i).text() for i in
                             range(self.cui.tableWidget.columnCount())]
        self.cui.comboBox.addItems(self.header_labes)
        self.cui.comboBox_2.addItems(self.header_labes)
        self.cui.comboBox_3.addItems(self.count)

    def map_value(self, header):

        if header in self.header_labes:
            index = self.header_labes.index(header)
            return self.header1[index]
        else:
            raise ValueError()

    def map_value1(self, header):

        if header in self.header_labes:
            index = self.header_labes.index(header)
            return self.header1[index]
        else:
            raise ValueError()

    def seach(self):
        t = self.cui.comboBox.currentText()
        temp2 = self.cui.lineEdit.text()
        temp = self.map_value(t)

        t1 = self.cui.comboBox_2.currentText()
        temp2_1 = self.cui.lineEdit_2.text()
        temp_1 = self.map_value(t1)

        if temp2_1 == '':
            temp_1 = '1'
            temp2_1 = '1'

        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT f.id_flight, dc.name_of_city, dap.name_of_airport, ac.name_of_city, aap.name_of_airport, fr.departure_date, fr.departure_time, fr.arrival_date, fr.arrival_time, s.name_of_states, fr.id_flight_records FROM flight f JOIN route r ON f.id_route = r.id_route JOIN airport dap ON r.where_from_id_airport = dap.id_airport JOIN city dc ON dap.id_city = dc.id_city JOIN airport aap ON r.where_id_airport = aap.id_airport JOIN city ac ON aap.id_city = ac.id_city JOIN flight_records fr ON f.id_flight = fr.id_flight JOIN states s ON fr.id_states = s.id_states WHERE {temp} = '{temp2}' and {temp_1} = '{temp2_1}'")
        rows = cursor.fetchall()
        cursor.close()

        self.cui.tableWidget.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.cui.tableWidget.setItem(i, j, item)

    def seach1(self):
        t = self.cui.comboBox.currentText()
        temp2 = self.cui.lineEdit.text()
        temp = self.map_value1(t)

        t1 = self.cui.comboBox_2.currentText()
        temp2_1 = self.cui.lineEdit_2.text()
        temp_1 = self.map_value1(t1)

        if temp2_1 == '':
            temp_1 = '1'
            temp2_1 = '1'

        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT lastname, firstname, patronymic, pgp_sym_decrypt(passport_serial::bytea, phone_number::text), pgp_sym_decrypt(passport_number::bytea, phone_number::text), phone_number FROM passengers WHERE {temp} = '{temp2}' and {temp_1} = '{temp2_1}'")
        rows = cursor.fetchall()
        cursor.close()

        self.cui.tableWidget.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.cui.tableWidget.setItem(i, j, item)

    def prob(self):
        self.txt = self.cui.comboBox_3.currentText()
        self.act_win = probWindow(self.txt, self.conn)
        self.act_win.show()

class probWindow(QMainWindow):
    def __init__(self, txt, conn):
        super().__init__()
        self.pui = prob_MainWindow()
        self.pui.setupUi(self)

        self.txt = txt
        self.conn = conn

        cursor = self.conn.cursor()
        cursor.execute(f"WITH booked_tickets AS (\
        SELECT ti.name_of_types, COUNT(bt.id_buyng_ticket) AS booked_seats \
        FROM ticket ti \
        JOIN flight_promotions fp ON ti.id_flight_promotions = fp.id_flight_promotions \
        JOIN flight_records fr ON fp.id_flight_records = fr.id_flight_records \
        JOIN flight f ON fr.id_flight = f.id_flight \
        JOIN by_a_ticket bt ON ti.id_ticket = bt.id_ticket \
        WHERE fr.id_flight_records = {txt} \
        GROUP BY ti.name_of_types \
        ) \
        SELECT f.id_flight, dc.name_of_city, dap.name_of_airport, ac.name_of_city, aap.name_of_airport, fr.departure_date, fr.departure_time, fr.arrival_date, fr.arrival_time, m.name_of_model, \
        SUM(CASE WHEN ti.name_of_types = 'Экономкласс' THEN ass.number_of_seats END) AS economy_seats, \
        SUM(CASE WHEN ti.name_of_types = 'Экономкласс' THEN ass.number_of_seats - COALESCE(bt.booked_seats, 0) END) AS economy_available_seats, \
        SUM(CASE WHEN ti.name_of_types = 'Бизнес-класс' THEN ass.number_of_seats END) AS business_seats, \
        SUM(CASE WHEN ti.name_of_types = 'Бизнес-класс' THEN ass.number_of_seats - COALESCE(bt.booked_seats, 0) END) AS business_available_seats, \
        SUM(CASE WHEN ti.name_of_types = 'Первый класс' THEN ass.number_of_seats END) AS first_class_seats, \
        SUM(CASE WHEN ti.name_of_types = 'Первый класс' THEN ass.number_of_seats - COALESCE(bt.booked_seats, 0) END) AS first_class_available_seats \
        FROM flight f \
        JOIN flight_records fr ON f.id_flight = fr.id_flight \
        JOIN airplane a ON f.id_airplane = a.id_airplane \
        JOIN model m ON a.id_model = m.id_model \
        JOIN airplane_seats ass ON a.id_airplane = ass.id_airplane \
        JOIN route rt ON f.id_route = rt.id_route \
        JOIN airport dap ON rt.where_from_id_airport = dap.id_airport \
        JOIN city dc ON dap.id_city = dc.id_city \
        JOIN airport aap ON rt.where_id_airport = aap.id_airport \
        JOIN city ac ON aap.id_city = ac.id_city \
        LEFT JOIN types_of_places ti ON ass.id_types_of_places = ti.id_types_of_places \
        LEFT JOIN booked_tickets bt ON ti.name_of_types = bt.name_of_types \
        WHERE fr.id_flight_records = {txt} \
        GROUP BY f.id_flight, dc.name_of_city, dap.name_of_airport, ac.name_of_city, aap.name_of_airport, fr.departure_date, fr.departure_time, fr.arrival_date, fr.arrival_time, m.name_of_model;")
        rows = cursor.fetchone()
        cursor.close()
        print(rows)

        self.pui.label.setText(f"Номер рейса: {rows[0]}")
        self.pui.label_2.setText(f"Дата отправки: {rows[5]}")
        self.pui.label_3.setText(f"Дата отправки: {rows[6]}")
        self.pui.label_4.setText(f"Дата прибытия: {rows[7]}")
        self.pui.label_5.setText(f"Дата прибытия: {rows[8]}")
        self.pui.label_6.setText(f"Модель самолета: {rows[9]}")
        self.pui.label_7.setText(f"Количество мест эконом класса: {rows[10]}")
        self.pui.label_8.setText(f"Количество свободных мест эконом класса: {rows[11]}")
        self.pui.label_9.setText(f"Количество свободных мест бизнес класса: {rows[12]}")
        self.pui.label_10.setText(f"Количество мест бизнес класса: {rows[13]}")
        self.pui.label_11.setText(f"Количество мест первого класса: {rows[14]}")
        self.pui.label_12.setText(f"Количество свободных мест первого класса: {rows[15]}")
        self.pui.label_13.setText(f"Аэропорт отправки: {rows[2]}")
        self.pui.label_14.setText(f"Город отправки: {rows[1]}")
        self.pui.label_15.setText(f"Аэропорт прибытия: {rows[4]}")
        self.pui.label_16.setText(f"Город прибытия: {rows[3]}")

class mWindow(QMainWindow):
    def __init__(self, username, conn):
        super().__init__()
        self.mui = mUi_MainWindow()
        self.mui.setupUi(self)
        self.conn = conn

        self.mui.label_2.setText(username)

        self.mui.tableWidget.setColumnCount(11)

class sWindow(QMainWindow):
    def __init__(self, username, conn):
        super().__init__()
        self.sui = sUi_MainWindow()
        self.sui.setupUi(self)
        self.conn = conn

        self.sui.label_2.setText(username)
        self.sui.pushButton_2.clicked.connect(self.cons)

        self.populate_combo_box_with_tables()
        self.sui.comboBox_3.currentIndexChanged.connect(self.on_table_selected)
        self.sui.pushButton_3.clicked.connect(self.ticket_moth)

    def populate_combo_box_with_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = cursor.fetchall()
        cursor.close()

        self.sui.comboBox_3.clear()
        for table in tables:
            self.sui.comboBox_3.addItem(table[0])

    def on_table_selected(self, index):
        table_name = self.sui.comboBox_3.itemText(index)
        self.load_table_data(table_name)

    def load_table_data(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name};')
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        self.sui.tableWidget.setRowCount(len(rows))
        self.sui.tableWidget.setColumnCount(len(column_names))

        self.sui.tableWidget.setHorizontalHeaderLabels(column_names)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.sui.tableWidget.setItem(i, j, item)

    def ticket_moth(self):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM ticket_month;')
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        self.sui.tableWidget.setRowCount(len(rows))
        self.sui.tableWidget.setColumnCount(len(column_names))

        self.sui.tableWidget.setHorizontalHeaderLabels(column_names)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.sui.tableWidget.setItem(i, j, item)

    def cons(self):
        subprocess.Popen(('start', 'D:\\PostgreSQL\\16\\scripts\\runpsql.bat'), shell=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
