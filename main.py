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
from reg import regUi_MainWindow
from pass_reg import passUi_MainWindow
from update import Updatei_MainWindow
from delete import delUi_MainWindow
from insert import insUi_MainWindow
import psycopg2
import subprocess

class LoginWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.login)

    def connect_bd(self, username, password):
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=username,
                password=password,
                host='localhost'
            )

            return conn
        except psycopg2.Error:
            QMessageBox.warning(self, 'Error', 'Не удалось подключится к БД')
            return None

    def aut_user(self, conn, username):
        if conn is None:
            return None

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

    def login(self):
        username = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()

        conn = self.connect_bd(username, password)
        role = self.aut_user(conn, username)
        if conn is not None:
            if role == 'consultant':
                self.act_win = cWindow(username, conn, self)
                self.act_win.show()
                self.hide()
            elif role == 'manager':
                self.act_win = mWindow(username, conn, self)
                self.act_win.show()
                self.hide()
            elif role == 'sysadmin':
                self.act_win = sWindow(username, conn, self)
                self.act_win.show()
                self.hide()
            else:
                QMessageBox.warning(self, 'Error', 'Invalid role')
        else:
            QMessageBox.warning(self, 'Error', 'Неверный логин или пароль')

class cWindow(QMainWindow):
    def __init__(self, username, conn, parent=None):
        super().__init__(parent)
        self.cui = cUi_MainWindow()
        self.cui.setupUi(self)
        self.conn = conn

        self.cui.label_2.setText(username)
        self.cui.pushButton.clicked.connect(self.prob)
        self.cui.pushButton_2.clicked.connect(self.butt)
        self.cui.pushButton_5.clicked.connect(self.top)

        self.cui.pushButton.setEnabled(False)
        self.cui.comboBox_3.setEnabled(False)
        self.cui.pushButton_3.setEnabled(False)

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
        self.cui.pushButton_3.setEnabled(True)

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
        self.cui.comboBox_3.clear()
        self.cui.comboBox_3.addItems(self.count)
        self.cui.pushButton_3.clicked.connect(self.reg)

    def pas(self):
        self.cui.pushButton.setEnabled(False)
        self.cui.comboBox_3.setEnabled(False)
        self.cui.pushButton_3.setEnabled(False)

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

        self.cui.tableWidget.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.cui.tableWidget.setItem(i, j, item)

        self.header_labes = [self.cui.tableWidget.horizontalHeaderItem(i).text() for i in
                             range(self.cui.tableWidget.columnCount())]
        self.cui.comboBox.addItems(self.header_labes)
        self.cui.comboBox_2.addItems(self.header_labes)

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
        self.act_win = probWindow(self.txt, self.conn, self)
        self.act_win.show()

    def reg(self):
        self.txt = self.cui.comboBox_3.currentText()
        self.act_win = regWindow(self.conn, self)
        self.act_win.show()

    def top(self):
        self.cui.comboBox.clear()
        self.cui.comboBox_2.clear()
        self.cui.tableWidget.clear()

        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM top_flight;')
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        self.cui.tableWidget.setRowCount(len(rows))
        self.cui.tableWidget.setColumnCount(len(column_names))

        self.cui.tableWidget.setHorizontalHeaderLabels(column_names)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.cui.tableWidget.setItem(i, j, item)

    def closeEvent(self, event):
        try:
            self.parent().show()
            event.accept()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

class probWindow(QMainWindow):
    def __init__(self, txt, conn, parent=None):
        super().__init__(parent)
        self.pui = prob_MainWindow()
        self.pui.setupUi(self)

        self.txt = txt
        self.conn = conn

        cursor = self.conn.cursor()
        cursor.execute(f"WITH booked_tickets AS (\
        SELECT ti.name_of_types, COUNT(bt.id_by_a_ticket) AS booked_seats \
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

class regWindow(QMainWindow):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.rui = regUi_MainWindow()
        self.rui.setupUi(self)

        self.conn = conn

        self.rui.pushButton.clicked.connect(self.registed_pass)
        self.rui.pushButton_2.clicked.connect(self.pass_reg)
        self.rui.pushButton_3.clicked.connect(self.upt)

        cursor = self.conn.cursor()
        cursor.execute(f'\
                                   SELECT rt.id_flight\
                                    FROM flight rt')
        flight = cursor.fetchall()
        cursor.close()
        self.rui.comboBox_2.addItems([str(row[0]) for row in flight])
        self.rui.comboBox_2.currentIndexChanged.connect(self.update_combobox_3)

        cursor = self.conn.cursor()
        cursor.execute(f'\
                           SELECT pa.id_passengers, pgp_sym_decrypt(passport_serial::bytea, phone_number::text),  pgp_sym_decrypt(passport_number::bytea, phone_number::text)\
                            FROM passengers pa')
        passn = cursor.fetchall()
        cursor.close()

        self.rui.comboBox.addItems([str(pas[0]) + ')' + ' ' + pas[1] + ' ' + pas[2] for pas in passn])
    def update_combobox_3(self):
        selected_flight_record_id = self.rui.comboBox_2.currentText()

        cursor = self.conn.cursor()
        cursor.execute(f'\
                   SELECT DISTINCT top.name_of_types\
                   FROM flight_records fr\
                   JOIN flight f ON fr.id_flight = f.id_flight\
                   JOIN airplane_seats aps ON f.id_airplane = aps.id_airplane\
                   JOIN types_of_places top ON aps.id_types_of_places = top.id_types_of_places\
                   WHERE fr.id_flight = %s;', (selected_flight_record_id,))
        rows = cursor.fetchall()
        cursor.close()

        self.rui.comboBox_3.clear()
        self.rui.comboBox_3.addItems([row[0] for row in rows])

    def pass_id(self):
        id_pas = self.rui.comboBox.currentText()
        return id_pas

    def id_class(self):
        name_type = self.rui.comboBox_3.currentText()

        cursor = self.conn.cursor()
        cursor.execute(f'\
                           SELECT  top.id_types_of_places\
                           FROM types_of_places top\
                           WHERE top.name_of_types = %s;', (name_type,))
        name = cursor.fetchall()
        cursor.close()
        return [row[0] for row in name]

    def registed_pass(self):
        id_reice = int(self.rui.comboBox_2.currentText())
        pass_id = self.pass_id()
        pass_res = int(pass_id.partition(')')[0])
        id_class = int(self.id_class()[0])

        cursor = self.conn.cursor()
        cursor.execute(f'CALL buy_ticket({pass_res}, {id_reice}, {id_class} , 0, 0)')
        price = cursor.fetchall()
        cursor.close()

        total_price = 0

        for item in price:
            total_price += item[1]

        self.rui.label_4.setText(f'Итоговая цена: {total_price}')

    def pass_reg(self):
        self.act_win = passregWindow(self.conn, self)
        self.act_win.show()

    def upt(self):
        self.close()
        self.act_win = regWindow(self.conn, self)
        self.show()

class passregWindow(QMainWindow):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.prui = passUi_MainWindow()
        self.prui.setupUi(self)

        self.conn = conn

        self.prui.pushButton.clicked.connect(self.into)

    def into(self):
        lastname = self.prui.lineEdit.text()
        firstname = self.prui.lineEdit_2.text()
        parag = self.prui.lineEdit_3.text()
        serial = self.prui.lineEdit_4.text()
        p_number = self.prui.lineEdit_5.text()
        phone = self.prui.lineEdit_6.text()

        cursor = self.conn.cursor()
        cursor.execute(f"\
                    INSERT INTO passengers (lastname, firstname, patronymic, passport_serial, passport_number, phone_number)\
                    VALUES ('{lastname}', '{firstname}', '{parag}', {serial}, {p_number}, {phone}) ")
        self.conn.commit()
        cursor.close()
        self.close()

class mWindow(QMainWindow):
    def __init__(self, username, conn, parent=None):
        super().__init__(parent)
        self.mui = mUi_MainWindow()
        self.mui.setupUi(self)
        self.conn = conn

        self.mui.label_2.setText(username)

        self.mui.pushButton_3.clicked.connect(self.ticket_moth)
        self.mui.pushButton_9.clicked.connect(self.activ_passengers)
        self.mui.pushButton.clicked.connect(self.sech_time)
        self.mui.pushButton_6.clicked.connect(self.insert_t)
        self.mui.pushButton_5.clicked.connect(self.update_t)
        self.mui.pushButton_4.clicked.connect(self.delete_t)

        self.populate_combo_box_with_tables()
        self.mui.comboBox_3.currentIndexChanged.connect(self.on_table_selected)
        self.mui.comboBox_4.currentIndexChanged.connect(self.on_table_selected_2)

    def populate_combo_box_with_tables(self):
        tables = (['benefits'], ['stocks'])

        self.mui.comboBox_3.clear()
        self.mui.comboBox_4.clear()

        for table in tables:
            self.mui.comboBox_3.addItem(table[0])
            self.mui.comboBox_4.addItem(table[0])

    def on_table_selected(self, index):
        self.table_name = self.mui.comboBox_3.itemText(index)
        self.load_table_data(self.table_name)

    def load_table_data(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name};')
        rows = cursor.fetchall()
        self.column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        self.mui.tableWidget.setRowCount(len(rows))
        self.mui.tableWidget.setColumnCount(len(self.column_names))

        self.count = []
        self.count_1 = []

        self.mui.tableWidget.setHorizontalHeaderLabels(self.column_names)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.mui.tableWidget.setItem(i, j, item)
                if j == 0:
                    self.count_1.append(str(value))

    def on_table_selected_2(self, index):
        table_name = self.mui.comboBox_4.itemText(index)
        self.load_table_data_2(table_name)

    def load_table_data_2(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name};')
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        self.mui.tableWidget_2.setRowCount(len(rows))
        self.mui.tableWidget_2.setColumnCount(len(column_names))

        self.mui.tableWidget_2.setHorizontalHeaderLabels(column_names)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.mui.tableWidget_2.setItem(i, j, item)

    def ticket_moth(self):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM ticket_month;')
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        self.mui.tableWidget.setRowCount(len(rows))
        self.mui.tableWidget.setColumnCount(len(column_names))

        self.mui.tableWidget.setHorizontalHeaderLabels(column_names)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.mui.tableWidget.setItem(i, j, item)

    def activ_passengers(self):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM year_passeng ;')
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        self.mui.tableWidget.setRowCount(len(rows))
        self.mui.tableWidget.setColumnCount(len(column_names))

        self.mui.tableWidget.setHorizontalHeaderLabels(column_names)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.mui.tableWidget.setItem(i, j, item)

    def sech_time(self):
        cursor = self.conn.cursor()
        time1 = self.mui.dateEdit.date().toString("yyyy-MM-dd")
        time2 = self.mui.dateEdit_2.date().toString("yyyy-MM-dd")

        cursor.execute(f"SELECT total_revenue('{time1}', '{time2}');")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        self.mui.tableWidget.setRowCount(len(rows))
        self.mui.tableWidget.setColumnCount(len(column_names))

        self.mui.tableWidget.setHorizontalHeaderLabels(column_names)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.mui.tableWidget.setItem(i, j, item)

    def update_t(self):
        self.tablename = self.table_name
        self.act_win = updateWindow(self.tablename, self.conn, self.column_names, self.count_1, self)
        self.act_win.show()

    def delete_t(self):
        self.tablename = self.table_name
        self.act_win = deleteWindow(self.tablename, self.conn, self.column_names, self.count_1, self)
        self.act_win.show()

    def insert_t(self):
        self.tablename = self.table_name
        self.act_win = insertWindow(self.tablename, self.conn, self.column_names, self.count_1, self)
        self.act_win.show()

    def closeEvent(self, event):
        try:
            self.parent().show()
            event.accept()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

class sWindow(QMainWindow):
    def __init__(self, username, conn, parent=None):
        super().__init__(parent)
        self.sui = sUi_MainWindow()
        self.sui.setupUi(self)
        self.conn = conn

        self.sui.label_2.setText(username)
        self.sui.pushButton_2.clicked.connect(self.cons)

        self.populate_combo_box_with_tables()
        self.sui.comboBox_3.currentIndexChanged.connect(self.on_table_selected)
        self.sui.comboBox_4.currentIndexChanged.connect(self.on_table_selected_2)

        self.sui.pushButton_3.clicked.connect(self.ticket_moth)
        self.sui.pushButton_7.clicked.connect(self.size_data)
        self.sui.pushButton_9.clicked.connect(self.activ_passengers)
        self.sui.pushButton.clicked.connect(self.sech_time)
        self.sui.pushButton_5.clicked.connect(self.update_t)
        self.sui.pushButton_4.clicked.connect(self.delete_t)
        self.sui.pushButton_6.clicked.connect(self.insert_t)

        self.sui.comboBox_5.setEnabled(False)
        self.sui.pushButton_8.setEnabled(False)

    def populate_combo_box_with_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = cursor.fetchall()
        cursor.close()

        self.sui.comboBox_3.clear()
        self.sui.comboBox_4.clear()
        for table in tables:
            self.sui.comboBox_3.addItem(table[0])
            self.sui.comboBox_4.addItem(table[0])

    def on_table_selected(self, index):
        self.table_name = self.sui.comboBox_3.itemText(index)
        self.load_table_data(self.table_name)

    def load_table_data(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name};')
        rows = cursor.fetchall()
        self.column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        self.sui.tableWidget.setRowCount(len(rows))
        self.sui.tableWidget.setColumnCount(len(self.column_names))

        self.count = []
        self.count_1 = []

        self.sui.tableWidget.setHorizontalHeaderLabels(self.column_names)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.sui.tableWidget.setItem(i, j, item)

                if j == 0 and table_name == 'flight_records':
                    self.count.append(str(value))
                elif j == 0:
                    self.count_1.append(str(value))


        if table_name == 'flight_records':
            self.sui.comboBox_5.setEnabled(True)
            self.sui.pushButton_8.setEnabled(True)

            self.sui.pushButton_8.clicked.connect(self.prob)
            self.sui.comboBox_5.addItems(self.count)

        else:
            self.sui.comboBox_5.setEnabled(False)
            self.sui.pushButton_8.setEnabled(False)

    def on_table_selected_2(self, index):
        table_name = self.sui.comboBox_4.itemText(index)
        self.load_table_data_2(table_name)

    def load_table_data_2(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name};')
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        self.sui.tableWidget_2.setRowCount(len(rows))
        self.sui.tableWidget_2.setColumnCount(len(column_names))

        self.sui.tableWidget_2.setHorizontalHeaderLabels(column_names)

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.sui.tableWidget_2.setItem(i, j, item)

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

    def size_data(self):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM size_disk;')
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

    def activ_passengers(self):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM year_passeng ;')
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

    def sech_time(self):
        cursor = self.conn.cursor()
        time1 = self.sui.dateEdit.date().toString("yyyy-MM-dd")
        time2 = self.sui.dateEdit_2.date().toString("yyyy-MM-dd")

        cursor.execute(f"SELECT total_revenue('{time1}', '{time2}');")
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

    def prob(self):
        self.txt = self.sui.comboBox_5.currentText()
        self.act_win = probWindow(self.txt, self.conn, self)
        self.act_win.show()

    def update_t(self):
        self.tablename = self.table_name
        self.act_win = updateWindow(self.tablename, self.conn, self.column_names, self.count_1, self)
        self.act_win.show()

    def delete_t(self):
        self.tablename = self.table_name
        self.act_win = deleteWindow(self.tablename, self.conn, self.column_names, self.count_1, self)
        self.act_win.show()

    def insert_t(self):
        self.tablename = self.table_name
        self.act_win = insertWindow(self.tablename, self.conn, self.column_names, self.count_1, self)
        self.act_win.show()

    def closeEvent(self, event):
        try:
            self.parent().show()
            event.accept()
        except Exception as e:
            QMessageBox.critical(None, 'Error', str(e))

class updateWindow(QMainWindow):
    def __init__(self, tablename, conn, column_names, count_1, parent=None):
        super().__init__(parent)
        self.upui = Updatei_MainWindow()
        self.upui.setupUi(self)
        self.conn = conn

        self.table_name = tablename
        self.column = column_names
        self.count = count_1

        self.upui.comboBox.clear()
        self.upui.comboBox_2.clear()

        self.upui.comboBox.addItems(self.column)
        self.upui.comboBox_2.addItems(self.count)
        self.upui.pushButton.clicked.connect(self.upload)

    def upload(self):
        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE {self.table_name} SET {self.upui.comboBox.currentText()} = '{self.upui.lineEdit.text()}' WHERE {self.column[0]} = '{self.upui.comboBox_2.currentText()}';")
        self.conn.commit()
        cursor.close()
        self.close()

class deleteWindow(QMainWindow):
    def __init__(self, tablename, conn, column_names, count_1, parent=None):
        super().__init__(parent)
        self.delui = delUi_MainWindow()
        self.delui.setupUi(self)
        self.conn = conn

        self.table_name = tablename
        self.column = column_names
        self.count = count_1

        self.delui.comboBox.clear()

        self.delui.comboBox.addItems(self.count)
        self.delui.pushButton.clicked.connect(self.dele)

    def dele(self):
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.column[0]} = {self.delui.comboBox.currentText()}")
        self.conn.commit()
        cursor.close()
        self.close()

class insertWindow(QMainWindow):
    def __init__(self, tablename, conn, column_names, count_1, parent=None):
        super().__init__(parent)
        self.inui = insUi_MainWindow()
        self.inui.setupUi(self)
        self.conn = conn

        self.table_name = tablename
        self.column = column_names
        self.count = count_1

        self.inui.pushButton.clicked.connect(self.inst)

        self.inui.tableWidget.setRowCount(1)
        self.inui.tableWidget.setColumnCount(len(column_names[1::]))
        self.inui.tableWidget.setHorizontalHeaderLabels(column_names[1::])

        for j in range(len(column_names[1::])):
            item = QTableWidgetItem('')
            self.inui.tableWidget.setItem(0, j, item)

    def inst(self):
        column_names = self.get_column_names()
        first_row_data = self.get_first_row_data()

        cursor = self.conn.cursor()
        placeholders = ', '.join(['%s'] * len(first_row_data))
        columns = ', '.join(column_names)
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, first_row_data)
        self.conn.commit()
        cursor.close()
        self.close()

    def get_column_names(self):
        column_count = self.inui.tableWidget.columnCount()
        column_names = []
        for col in range(column_count):
            column_name = self.inui.tableWidget.horizontalHeaderItem(col).text()
            column_names.append(column_name)
        return column_names

    def get_first_row_data(self):
        column_count = self.inui.tableWidget.columnCount()
        first_row_data = []
        for col in range(column_count):
            item = self.inui.tableWidget.item(0, col)
            if item is not None:
                first_row_data.append(item.text())
            else:
                first_row_data.append('')
        return first_row_data

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
