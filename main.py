import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QInputDialog, QTableWidgetItem
from PyQt5.sip import delete
from PyQt5.uic import loadUi
from PyQt5 import QtCore
import datetime
from conexion import crear_conexion

usuarios = {
    "admin": {"password": "1234", "role": "admin"},
    "user": {"password": "5678", "role": "user"},
}

empleados = [
    {"nombre": "Juan Pérez", "puesto": "Desarrollador", "DNI": "111111"},
    {"nombre": "Ana López", "puesto": "Diseñadora", "DNI": "222222"},
]

gastos = []
etapas = []
protos = []
recursos = []

app = None
main_window = None
login_window = None
usuario_actual = None
rol_actual = None
dni_actual = None

def header():
    global main_window
    main_window.btnEmpleados.clicked.connect(abrir_ventana_principal)
    main_window.btnGastos.clicked.connect(abrir_ventana_gastos)
    main_window.btnProto.clicked.connect(abrir_ventana_proto)
    main_window.btnEtapas.clicked.connect(abrir_ventana_etapas)
    main_window.btnRecursos.clicked.connect(abrir_ventana_recursos)

def iniciar_sesion():
    global usuario_actual, rol_actual, main_window, login_window, dni_actual

    email = login_window.inputUsuario.text()
    dni = login_window.inputContrasena.text()

    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()

            sql_query = "SELECT nombre, email, DNI FROM empleados WHERE email = %s AND DNI = %s"
            cursor.execute(sql_query, (email, dni))
            resultado = cursor.fetchone()

            if resultado:
                nombre, email_resultado, dni_resultado = resultado
                usuario_actual = nombre
                dni_actual = dni_resultado
                if email == "aroldanrabanal@safareyes.es" or email == "jnavasmedina@safareyes.es" or email=="admin":
                    rol_actual = "admin"
                else:
                    rol_actual = "user"

                login_window.accept()
                abrir_ventana_principal()
            else:
                login_window.labelError.setText("Usuario o contraseña incorrectos")
        except Exception as e:
            print(f"Error al validar las credenciales: {e}")
            login_window.labelError.setText("Error al conectar con la base de datos")
        finally:
            cursor.close()
            conexion.close()
    else:
        login_window.labelError.setText("No se pudo conectar a la base de datos")

def configurar_ventana_gastos():
    global main_window, rol_actual, gastos

    main_window.labelusu.setText(f"Bienvenido, {usuario_actual} ({rol_actual})")
    gastos = []
    conexion = crear_conexion()

    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute("""SELECT empleados.nombre, prototipos.Nombre, gastos.Descripcion, Fecha, Importe, Tipo, gastos.id
                           FROM gastos
                           INNER JOIN empleados ON gastos.id_emp = empleados.ID
                           INNER JOIN prototipos ON gastos.id_proto = prototipos.id""")
            resultados = cursor.fetchall()
            gastos = [{"empleado": fila[0], "proto": fila[1], "desc": fila[2], "fecha": fila[3], "importe": fila[4], "tipo": fila[5], "id": fila[6]} for fila in resultados]

            main_window.listgastos.clear()
            for gasto in gastos:
                main_window.listgastos.addItem(f"{gasto['empleado']} - {gasto['proto']} - {gasto['desc']} - {gasto['fecha']} - {gasto['importe']}€")

            print("Gastos cargados correctamente desde la BBDD")
        except Exception as e:
            print(f"Error al validar las credenciales: {e}")
        finally:
            cursor.close()
            conexion.close()

def configurar_ventana_principal():
    global main_window, rol_actual, empleados

    main_window.labelusu.setText(f"Bienvenido, {usuario_actual} ({rol_actual})")

    empleados = []
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:

            cursor.execute("SELECT nombre, Titulacion, DNI FROM empleados")
            resultados = cursor.fetchall()

            empleados = [{"nombre": fila[0], "puesto": fila[1], "DNI": fila[2]} for fila in resultados]

            main_window.listEmpleados.clear()
            for empleado in empleados:
                main_window.listEmpleados.addItem(f"{empleado['nombre']} - {empleado['puesto']} - {empleado['DNI']}")

            print("Empleados cargados correctamente desde la base de datos.")
        except Exception as e:
            print(f"Error al cargar los empleados: {e}")
        finally:
            cursor.close()
            conexion.close()

    if rol_actual == "admin":
        main_window.btnAdd.setEnabled(True)
        main_window.btnEdit.setEnabled(True)
        main_window.btnDelete.setEnabled(True)
    else:
        main_window.btnAdd.setEnabled(False)
        main_window.btnDelete.setEnabled(False)


def configurar_ventana_etapas():
    global main_window, rol_actual, etapas

    try:
        main_window.labelusu.setText(f"Bienvenido, {usuario_actual} ({rol_actual})")
        etapas = []
        conexion = crear_conexion()

        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("""
                    SELECT e.id, p.Nombre, e.nombre, e.fecha_inicio, e.fecha_fin, e.estado
                    FROM etapas AS e
                    INNER JOIN prototipos AS p ON id_protot = p.id;
                """)
                resultados = cursor.fetchall()

                etapas = [{"id": fila[0], "nombre_proto": fila[1], "nombre": fila[2], "fecha_ini": fila[3], "fecha_fin": fila[4], "estado": fila[5]} for fila in resultados]

                main_window.listetapas.clear()
                for etapa in etapas:
                    main_window.listetapas.addItem(f"{etapa['nombre']} - {etapa['nombre_proto']} - "
                                                   f"{etapa['fecha_ini']} - {etapa['fecha_fin']} - {etapa['estado']}")

                print("Etapas cargadas correctamente.")
            except Exception as e:
                print(f"Error en la consulta SQL: {e}")
            finally:
                cursor.close()
                conexion.close()
        else:
            print("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"Error inesperado al configurar etapas: {e}")

def configurar_ventana_recursos():
    global main_window, rol_actual, recursos

    main_window.labelusu.setText(f"Bienvenido, {usuario_actual} ({rol_actual})")

    recursos = []
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:

            cursor.execute("SELECT id, nombre, descripcion, tipo FROM recursos")
            resultados = cursor.fetchall()

            recursos = [{"id": fila[0], "nombre": fila[1], "tipo": fila[3], "descripcion": fila[2]} for fila in resultados]

            main_window.listrecursos.clear()
            for recurso in recursos:
                main_window.listrecursos.addItem(f"{recurso['id']} - {recurso['nombre']} - {recurso['tipo']} - descripcion: {recurso['descripcion']}")

            print("Recursos cargados correctamente desde la base de datos.")
        except Exception as e:
            print(f"Error al cargar los prototipos: {e}")
        finally:
            cursor.close()
            conexion.close()

    if rol_actual == "admin":
        main_window.btnAddRecursos.setEnabled(True)
        main_window.btnEditRecursos.setEnabled(True)
        main_window.btnDeleteRecursos.setEnabled(True)
    else:
        main_window.btnAddRecursos.setEnabled(False)
        main_window.btnDeleteRecursos.setEnabled(False)




def configurar_ventana_proto():
    global main_window, rol_actual, protos

    main_window.labelusu.setText(f"Bienvenido, {usuario_actual} ({rol_actual})")

    protos = []
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:

            cursor.execute("SELECT Nombre, Fecha_inicio, Fecha_fin, Presupuesto, Horas_est, id FROM prototipos")
            resultados = cursor.fetchall()

            protos = [{"nombre": fila[0], "fecha_ini": fila[1], "fecha_fin": fila[2], "presu": fila[3], "horas": fila[4], "id": fila[5]} for fila in resultados]

            main_window.listProto.clear()
            for proto in protos:
                main_window.listProto.addItem(f"{proto['nombre']} - {proto['fecha_ini']} - {proto['fecha_fin']} - Presupuesto: {proto['presu']}€ - Horas: {proto['horas']}")

            print("Prototipos cargados correctamente desde la base de datos.")
        except Exception as e:
            print(f"Error al cargar los prototipos: {e}")
        finally:
            cursor.close()
            conexion.close()

    if rol_actual == "admin":
        main_window.btnAddProto.setEnabled(True)
        main_window.btnEditProto.setEnabled(True)
        main_window.btnDeleteProto.setEnabled(True)
    else:
        main_window.btnAddProto.setEnabled(False)
        main_window.btnDeleteProto.setEnabled(False)

def anadir_empleado():
    global main_window

    dialogo = QDialog()
    loadUi("formulario.ui", dialogo)
    dialogo.setWindowTitle("Añadir Empleado")

    dialogo.addenviar.clicked.connect(dialogo.accept)

    if dialogo.exec_() == QDialog.Accepted:
        nombre = dialogo.addnombre.text().strip()
        email = dialogo.addemail.text().strip()
        DNI = dialogo.addDNI.text().strip()
        puesto = dialogo.addtitulacion.text().strip()
        a_exp = dialogo.addanos.text().strip()

        if not nombre or not email or not DNI or not puesto:
            QMessageBox.warning(dialogo, "Error", "Todos los campos son obligatorios.")
            return

        empleados.append({"nombre": nombre, "puesto": puesto, "DNI": DNI})
        main_window.listEmpleados.addItem(f"{nombre} - {puesto} - {DNI}")

        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql_insert = ("INSERT INTO empleados (nombre, DNI, Email, Titulacion, anos_experiencia) "
                              "VALUES (%s, %s, %s, %s, %s)")
                cursor.execute(sql_insert, (nombre, DNI, email, puesto, a_exp))
                conexion.commit()
                print(f"Empleado '{nombre}' añadido correctamente.")
            except Exception as e:
                print(f"Error al insertar el empleado en la base de datos: {e}")
                QMessageBox.critical(dialogo, "Error", "No se pudo añadir el empleado.")
            finally:
                cursor.close()
                conexion.close()

def anadir_recursos():
    global main_window

    dialogo = QDialog()
    try:
        loadUi("formulario_recursos.ui", dialogo)
    except Exception as e:
        print(f"Error al cargar el archivo .ui: {e}")
        return

    dialogo.setWindowTitle("Añadir recursos")
    widgets = ["addnombre", "addtipo", "adddesc", "addenviar"]
    for widget in widgets:
        if not hasattr(dialogo, widget):
            print(f"El formulario no contiene el widget: {widget}")
            return
    dialogo.addenviar.clicked.connect(dialogo.accept)

    if dialogo.exec_() == QDialog.Accepted:
        try:
            # Recoger datos del formulario
            nombre = dialogo.addnombre.text().strip()
            tipo = dialogo.addtipo.text().strip()
            descripcion = dialogo.adddesc.toPlainText().strip()

            if not nombre or not tipo or not descripcion:
                QMessageBox.warning(dialogo, "Error", "Todos los campos son obligatorios.")
                return

            conexion = crear_conexion()
            if conexion:
                try:
                    cursor = conexion.cursor()
                    sql_insert = "INSERT INTO recursos (nombre, tipo, descripcion) VALUES (%s, %s, %s)"
                    cursor.execute(sql_insert, (nombre, tipo, descripcion))
                    conexion.commit()
                    try:
                        recursos.append({"id": cursor.lastrowid,"nombre": nombre, "tipo": tipo, "descripcion": descripcion})
                        main_window.listrecursos.addItem(f"{nombre} - {tipo} - {descripcion}")
                    except AttributeError as e:
                        print(f"Error al actualizar la lista de recursos: {e}")
                        QMessageBox.critical(dialogo, "Error", "No se pudo actualizar la lista local de recursos.")
                        return
                    print(f"Recurso '{nombre}' añadido correctamente.")
                except Exception as e:
                    print(f"Error al insertar en la base de datos: {e}")
                    QMessageBox.critical(dialogo, "Error", f"No se pudo añadir el recurso. Detalles: {e}")
                finally:
                    cursor.close()
                    conexion.close()
            else:
                print("Error: No se pudo conectar a la base de datos.")
                QMessageBox.critical(dialogo, "Error", "No se pudo conectar a la base de datos.")

        except Exception as e:
            print(f"Error inesperado: {e}")
            QMessageBox.critical(dialogo, "Error", f"Ha ocurrido un error inesperado. Detalles: {e}")


def anadir_gastos():
    global main_window, gastos
    gastos = []

    dialogo = QDialog()
    loadUi("formulario_gastos.ui", dialogo)
    dialogo.setWindowTitle("Añadir gastos")

    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id, Nombre FROM prototipos")
            resultados = cursor.fetchall()
            dialogo.addproto.clear()
            dialogo.addproto.addItem("Ninguno", "NULL")
            for id, nombre in resultados:
                dialogo.addproto.addItem(nombre, id)

            cursor.execute("SELECT ID, nombre FROM empleados")
            resultados = cursor.fetchall()
            dialogo.addempleado.clear()
            dialogo.addempleado.addItem("Ninguno", "NULL")
            for id, nombre in resultados:
                dialogo.addempleado.addItem(nombre, id)
        except Exception as e:
            print(f"Error al cargar datos: {e}")
        finally:
            cursor.close()
            conexion.close()

    dialogo.addenviargastos.clicked.connect(dialogo.accept)

    if dialogo.exec_() == QDialog.Accepted:
        try:
            empleados = dialogo.addempleado.currentData()
            prototipos = dialogo.addproto.currentData()
            fecha = dialogo.addfecha.date().toString("yyyy-MM-dd")
            importe = float(dialogo.addimport.text().strip().replace(',', '.'))
            descripcion = dialogo.adddesc.toPlainText().strip()
            tipo = dialogo.addtipo.text().strip()
            if not empleados or not prototipos or not fecha or not importe or not descripcion:
                QMessageBox.warning(dialogo, "Error", "Todos los campos son obligatorios.")
                return


            conexion = crear_conexion()
            if conexion:
                cursor = conexion.cursor()
                try:
                    sql_insert = ("INSERT INTO gastos (id_emp, id_proto, fecha, importe, descripcion, tipo) "
                                  "VALUES (%s, %s, %s, %s, %s, %s)")
                    cursor.execute(sql_insert, (empleados, prototipos, fecha, importe, descripcion, tipo))
                    conexion.commit()
                    gastos.append({"empleado": empleados, "proto": prototipos, "desc": descripcion, "fecha": fecha, "importe": importe, "tipo": tipo, "id": cursor.lastrowid})
                    main_window.listgastos.addItem(f"{empleados} - {prototipos} - {descripcion} - {fecha} - {importe}€")

                    print(f"Gasto de '{empleados}' añadido correctamente.")
                except Exception as e:
                    print(f"Error al insertar en la base de datos: {e}")
                    QMessageBox.critical(dialogo, "Error", "No se pudo añadir el gasto.")
                finally:
                    cursor.close()
                    conexion.close()
        except Exception as e:
            print(f"Error al procesar el formulario: {e}")


def anadir_proto():
    global main_window, protos

    dialogo = QDialog()
    try:
        loadUi("formulario_proto.ui", dialogo)
    except Exception as e:
        print(f"Error al cargar el formulario: {e}")
        return

    dialogo.setWindowTitle("Añadir Prototipo")

    print("Verificando widgets del formulario...")
    widgets = ["addnombre", "addini", "addfin", "addpresu", "addhoras", "addrelacionan", "addDesc"]
    for widget in widgets:
        if not hasattr(dialogo, widget):
            print(f"El formulario no contiene el widget: {widget}")
            QMessageBox.critical(dialogo, "Error", f"Falta el widget '{widget}' en el formulario.")
            return

    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id, Nombre FROM prototipos")
            resultados = cursor.fetchall()

            dialogo.addrelacionan.clear()
            dialogo.addrelacionan.addItem("Ninguno", "NULL")

            for id, nombre in resultados:
                dialogo.addrelacionan.addItem(nombre, id)
        except Exception as e:
            print(f"Error al cargar prototipos para relacionar: {e}")
        finally:
            cursor.close()
            conexion.close()

    dialogo.addenviar.clicked.connect(dialogo.accept)

    if dialogo.exec_() == QDialog.Accepted:
        try:
            nombre = dialogo.addnombre.text().strip()
            fecha_inicio = dialogo.addini.text().strip()
            fecha_fin = dialogo.addfin.text().strip()
            presupuesto = dialogo.addpresu.value()
            horas = dialogo.addhoras.value()
            relacion_id = dialogo.addrelacionan.currentData()
            descp = dialogo.addDesc.toPlainText().strip()

            print(f"Datos capturados: {nombre}, {fecha_inicio}, {fecha_fin}, {presupuesto}, {horas}, {relacion_id}, {descp}")

            if relacion_id == "NULL":
                relacion_id = None

            try:
                fecha_inicio = datetime.datetime.strptime(fecha_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
                fecha_fin = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").strftime("%Y-%m-%d")
                print(f"Fechas convertidas: {fecha_inicio}, {fecha_fin}")
            except ValueError as e:
                print(f"Error al convertir las fechas: {e}")
                QMessageBox.warning(dialogo, "Error", "Las fechas deben estar en formato DD/MM/YYYY.")
                return
            if not nombre or not fecha_inicio or not fecha_fin:
                print("Campos obligatorios incompletos.")
                QMessageBox.warning(dialogo, "Error", "Todos los campos son obligatorios.")
                return

            conexion = crear_conexion()
            if conexion:
                cursor = conexion.cursor()
                try:
                    sql_insert = """
                    INSERT INTO prototipos (Nombre, Fecha_inicio, Fecha_fin, Presupuesto, Horas_est, id_proto_rel, Descripcion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert, (nombre, fecha_inicio, fecha_fin, presupuesto, horas, relacion_id, descp))
                    conexion.commit()
                    protos.append({"nombre": nombre, "fecha_ini": fecha_inicio, "fecha_fin": fecha_fin, "presu": presupuesto, "horas": horas, "id": cursor.lastrowid})
                    main_window.listProto.addItem(f"{nombre} - {fecha_inicio} - {fecha_fin} - Presupuesto: {presupuesto}€ - Horas: {horas}")
                    print(f"Prototipo '{nombre}' añadido correctamente.")
                except Exception as e:
                    print(f"Error al insertar el prototipo en la base de datos: {e}")
                    QMessageBox.critical(dialogo, "Error", "No se pudo añadir el prototipo.")
                finally:
                    cursor.close()
                    conexion.close()
        except Exception as e:
            print(f"Error al procesar los datos del formulario: {e}")

def anadir_etapas():
    global main_window

    dialogo = QDialog()
    loadUi("formulario_etapas.ui", dialogo)
    dialogo.setWindowTitle("Añadir Etapas")
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id, Nombre FROM prototipos")
            resultados = cursor.fetchall()

            try:
                dialogo.addproto.clear()
                dialogo.addproto.addItem("Ninguno", "NULL")

                for id, nombre in resultados:
                    dialogo.addproto.addItem(nombre, id)
            except AttributeError as e:
                print(f"Error al configurar 'addproto': {e}")
                return

        except Exception as e:
            print(f"Error al cargar prototipos para relacionar: {e}")
        finally:
            cursor.close()
            conexion.close()

    dialogo.addenviar.clicked.connect(dialogo.accept)

    if dialogo.exec_() == QDialog.Accepted:
        nombre = dialogo.addnombre.text().strip()
        fecha_ini = dialogo.addini.text().strip()
        fecha_fin = dialogo.addfin.text().strip()
        estado = dialogo.addestado.currentText()
        proto = dialogo.addproto.currentData()
        proto_nombre = dialogo.addproto.currentText()

        if proto == "NULL":
            proto = None

        try:
            fecha_ini = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
            fecha_fin = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError as e:
            print(f"Error al convertir fechas: {e}")
            QMessageBox.warning(dialogo, "Error", "Las fechas deben estar en formato DD/MM/YYYY.")
            return
        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql_insert = ("INSERT INTO etapas (nombre, fecha_inicio, fecha_fin, estado, id_protot) "
                              "VALUES (%s, %s, %s, %s, %s)")
                cursor.execute(sql_insert, (nombre, fecha_ini, fecha_fin, estado, proto))
                conexion.commit()
                etapas.append({"id": cursor.lastrowid, "nombre_proto": proto, "nombre": nombre, "fecha_ini": fecha_ini,
                               "fecha_fin": fecha_fin, "estado": estado})
                main_window.listetapas.addItem(f"{nombre} - {proto_nombre} - {fecha_ini} - {fecha_fin} - {estado}")
                print(f"Etapas '{nombre}' añadido correctamente.")
            except Exception as e:
                print(f"Error al insertar el empleado en la base de datos: {e}")
                QMessageBox.critical(dialogo, "Error", "No se pudo añadir el empleado.")
            finally:
                cursor.close()
                conexion.close()

def eliminar_gasto():
    global main_window

    current_item = main_window.listGastos.currentRow()

    if current_item >= 0:
        gasto = gastos[current_item]
        id = gasto["id"]

        respuesta = QMessageBox.question(
            main_window,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar a {id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            gastos.pop(current_item)
            main_window.listGastos.takeItem(current_item)

            conexion = crear_conexion()
            if conexion:
                cursor = conexion.cursor()
                try:
                    sql_delete = "DELETE FROM gastos WHERE id = %s"
                    cursor.execute(sql_delete, (id,))
                    conexion.commit()
                    print(f"Empleado '{id}' eliminado correctamente de la base de datos.")
                except Exception as e:
                    print(f"Error al eliminar el empleado de la base de datos: {e}")
                cursor.close()
                conexion.close()

def eliminar_etapas():
    global main_window

    current_item = main_window.listetapas.currentRow()

    if current_item >= 0:
        etapa = etapas[current_item]
        id = etapa["id"]

        respuesta = QMessageBox.question(
            main_window,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar a {id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            etapas.pop(current_item)
            main_window.listetapas.takeItem(current_item)

            conexion = crear_conexion()
            if conexion:
                cursor = conexion.cursor()
                try:
                    sql_delete = "DELETE FROM etapas WHERE id = %s"
                    cursor.execute(sql_delete, (id,))
                    conexion.commit()
                    print(f"Etapa '{id}' eliminada correctamente de la base de datos.")
                except Exception as e:
                    print(f"Error al eliminar el empleado de la base de datos: {e}")
                cursor.close()
                conexion.close()

def eliminar_recurso():
    global main_window

    current_item = main_window.listrecursos.currentRow()
    if current_item < 0:
        QMessageBox.warning(main_window, "Error", "No se ha seleccionado ningún recurso.")
        return

    recurso = recursos[current_item]
    id = recurso.get("id")
    nombre = recurso.get("nombre", "Recurso desconocido")

    respuesta = QMessageBox.question(
        main_window,
        "Confirmar eliminación",
        f"¿Estás seguro de que deseas eliminar el recurso '{nombre}' con ID {id}?",
        QMessageBox.Yes | QMessageBox.No
    )

    if respuesta == QMessageBox.Yes:
        try:
            recursos.pop(current_item)
            main_window.listrecursos.takeItem(current_item)
        except Exception as e:
            print(f"Error al eliminar el recurso localmente: {e}")
            QMessageBox.critical(main_window, "Error", "No se pudo actualizar la lista local.")
            return

        conexion = None
        try:
            conexion = crear_conexion()
            if not conexion:
                raise Exception("No se pudo conectar a la base de datos.")
            cursor = conexion.cursor()
            sql_delete = "DELETE FROM recursos WHERE id = %s"
            cursor.execute(sql_delete, (id,))
            conexion.commit()
            print(f"Recurso '{id}' eliminado correctamente de la base de datos.")
        except Exception as e:
            print(f"Error al eliminar el recurso de la base de datos: {e}")
            QMessageBox.critical(main_window, "Error", f"No se pudo eliminar el recurso. Detalles: {e}")
        finally:
            if conexion:
                conexion.close()



def eliminar_proto():
    global main_window

    current_item = main_window.listProto.currentRow()

    if current_item >= 0:
        proto = protos[current_item]
        nombre_proto = proto["nombre"]
        id = proto["id"]

        respuesta = QMessageBox.question(
            main_window,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar a {nombre_proto}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            protos.pop(current_item)
            main_window.listProto.takeItem(current_item)

            conexion = crear_conexion()
            if conexion:
                cursor = conexion.cursor()
                try:
                    sql_delete = "DELETE FROM prototipos WHERE id = %s"
                    cursor.execute(sql_delete, (id,))
                    conexion.commit()
                    print(f"Empleado '{nombre_proto}' eliminado correctamente de la base de datos.")
                except Exception as e:
                    print(f"Error al eliminar el empleado de la base de datos: {e}")
                cursor.close()
                conexion.close()


def eliminar_empleado():
    global main_window

    current_item = main_window.listEmpleados.currentRow()

    if current_item >= 0:
        empleado = empleados[current_item]
        nombre_empleado = empleado["nombre"]
        dni = empleado["DNI"]

        respuesta = QMessageBox.question(
            main_window,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar a {nombre_empleado}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            empleados.pop(current_item)
            main_window.listEmpleados.takeItem(current_item)

            conexion = crear_conexion()
            if conexion:
                cursor = conexion.cursor()
                try:
                    sql_delete = "DELETE FROM empleados WHERE DNI = %s"
                    cursor.execute(sql_delete, (dni,))
                    conexion.commit()
                    print(f"Empleado '{nombre_empleado}' eliminado correctamente de la base de datos.")
                except Exception as e:
                    print(f"Error al eliminar el empleado de la base de datos: {e}")
                cursor.close()
                conexion.close()


def editar_empleado():
    global main_window, usuario_actual, dni_actual

    current_item = main_window.listEmpleados.currentRow()
    if current_item >= 0:
        empleado = empleados[current_item]
        dni_empleado = empleado["DNI"]

        if rol_actual == "user" and dni_actual != dni_empleado:
            QMessageBox.warning(main_window, "Permiso denegado", "Solo puedes editar tu propio perfil.")
            return

        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql_select = "SELECT nombre, DNI, Email, Titulacion, anos_experiencia FROM empleados WHERE DNI = %s"
                cursor.execute(sql_select, (dni_empleado,))
                resultado = cursor.fetchone()

                if not resultado:
                    QMessageBox.warning(main_window, "Error", "No se encontraron datos del empleado en la base de datos.")
                    return

                nombre, dni, email, titulacion, anos_experiencia = resultado

                dialogo = QDialog()
                loadUi("formulario.ui", dialogo)
                dialogo.setWindowTitle("Editar Empleado")

                dialogo.addnombre.setText(nombre)
                dialogo.addemail.setText(email)
                dialogo.addDNI.setText(dni)
                dialogo.addtitulacion.setText(titulacion)
                dialogo.addanos.setValue(int(anos_experiencia))
                dialogo.addenviar.clicked.connect(dialogo.accept)

                if dialogo.exec_() == QDialog.Accepted:
                    nuevo_nombre = dialogo.addnombre.text().strip()
                    nuevo_email = dialogo.addemail.text().strip()
                    nuevo_DNI = dialogo.addDNI.text().strip()
                    nueva_titulacion = dialogo.addtitulacion.text().strip()
                    nuevos_anos_experiencia = dialogo.addanos.text().strip()

                    if not nuevo_nombre or not nuevo_email or not nuevo_DNI or not nueva_titulacion or not nuevos_anos_experiencia:
                        QMessageBox.warning(dialogo, "Error", "Todos los campos son obligatorios.")
                        return

                    empleados[current_item] = {"nombre": nuevo_nombre, "puesto": nueva_titulacion, "DNI": nuevo_DNI}
                    main_window.listEmpleados.item(current_item).setText(f"{nuevo_nombre} - {nueva_titulacion} - {nuevo_DNI}")

                    sql_update = "UPDATE empleados SET nombre = %s, Email = %s, DNI = %s, Titulacion = %s, anos_experiencia = %s WHERE DNI = %s"
                    cursor.execute(sql_update, (nuevo_nombre, nuevo_email, nuevo_DNI, nueva_titulacion, nuevos_anos_experiencia, dni_empleado))
                    conexion.commit()
                    print(f"Empleado con DNI {dni_empleado} actualizado correctamente.")
            except Exception as e:
                print(f"Error al actualizar los datos del empleado: {e}")
                QMessageBox.critical(main_window, "Error", "No se pudo editar el empleado.")
            finally:
                cursor.close()
                conexion.close()

def editar_recursos():
    global main_window

    current_item = main_window.listrecursos.currentRow()
    if current_item >= 0:
        recurso = recursos[current_item]
        id = recurso["id"]

        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql_select = "SELECT id, nombre, tipo, descripcion FROM recursos WHERE id = %s"
                cursor.execute(sql_select, (id,))
                resultado = cursor.fetchone()

                if not resultado:
                    QMessageBox.warning(main_window, "Error", "No se encontraron datos del recurso en la base de datos.")
                    return

                id, nombre, tipo, descripcion = resultado

                dialogo = QDialog()
                loadUi("formulario_recursos.ui", dialogo)
                dialogo.setWindowTitle("Editar recurso")

                dialogo.addnombre.setText(nombre)
                dialogo.addtipo.setText(tipo)
                dialogo.adddesc.setText(descripcion)
                dialogo.addenviar.clicked.connect(dialogo.accept)

                if dialogo.exec_() == QDialog.Accepted:
                    nuevo_nombre = dialogo.addnombre.text().strip()
                    nuevo_tipo = dialogo.addtipo.text().strip()
                    nuevo_desc = dialogo.adddesc.toPlainText().strip()

                    if not nuevo_nombre or not nuevo_tipo or not nuevo_desc:
                        QMessageBox.warning(dialogo, "Error", "Todos los campos son obligatorios.")
                        return

                    recursos[current_item] = {"id": id, "nombre": nuevo_nombre, "tipo": nuevo_tipo, "descripcion": nuevo_desc}
                    main_window.listrecursos.item(current_item).setText(f"{nuevo_nombre} - {nuevo_tipo} - {nuevo_desc}")

                    sql_update = "UPDATE recursos SET nombre = %s, tipo = %s, descripcion = %s WHERE id = %s"
                    cursor.execute(sql_update, (nuevo_nombre, nuevo_tipo, nuevo_desc, id))
                    conexion.commit()
                    print(f"Recurso con nombre {nuevo_nombre} actualizado correctamente.")
            except Exception as e:
                print(f"Error al actualizar los datos del recurso: {e}")
                QMessageBox.critical(main_window, "Error", "No se pudo editar el recurso.")
            finally:
                cursor.close()
                conexion.close()

def editar_proto():
    global main_window, protos

    current_item = main_window.listProto.currentRow()
    if current_item < 0 or current_item >= len(protos):
        QMessageBox.warning(main_window, "Error", "No se seleccionó un prototipo válido.")
        return

    proto = protos[current_item]
    proto_id = proto["id"]

    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            sql_select = """
                SELECT Nombre, Fecha_inicio, Fecha_fin, Presupuesto, Horas_est, id_proto_rel, Descripcion
                FROM prototipos
                WHERE id = %s
            """
            cursor.execute(sql_select, (proto_id,))
            resultado = cursor.fetchone()

            if not resultado:
                QMessageBox.warning(main_window, "Error", "No se encontraron datos del prototipo en la base de datos.")
                return

            nombre, fecha_inicio, fecha_fin, presupuesto, horas, id_proto_rel, descripcion = resultado

            fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%d")
            fecha_fin_str = fecha_fin.strftime("%Y-%m-%d")

            dialogo = QDialog()
            loadUi("formulario_proto.ui", dialogo)
            dialogo.setWindowTitle("Editar Prototipo")

            dialogo.addnombre.setText(nombre)
            dialogo.addini.setDate(QtCore.QDate.fromString(fecha_inicio_str, "yyyy-MM-dd"))
            dialogo.addfin.setDate(QtCore.QDate.fromString(fecha_fin_str, "yyyy-MM-dd"))
            dialogo.addpresu.setValue(presupuesto)
            dialogo.addhoras.setValue(horas)
            dialogo.addDesc.setPlainText(descripcion)

            cursor.execute("SELECT id, Nombre FROM prototipos")
            resultados = cursor.fetchall()

            dialogo.addrelacionan.clear()
            dialogo.addrelacionan.addItem("Ninguno", None)
            for id, nombre_rel in resultados:
                dialogo.addrelacionan.addItem(nombre_rel, id)

            for i in range(dialogo.addrelacionan.count()):
                if dialogo.addrelacionan.itemData(i) == id_proto_rel:
                    dialogo.addrelacionan.setCurrentIndex(i)
                    break

            dialogo.addenviar.clicked.connect(dialogo.accept)

            if dialogo.exec_() == QDialog.Accepted:
                nuevo_nombre = dialogo.addnombre.text().strip()
                nueva_fecha_inicio = dialogo.addini.date().toString("yyyy-MM-dd")
                nueva_fecha_fin = dialogo.addfin.date().toString("yyyy-MM-dd")
                nuevo_presupuesto = dialogo.addpresu.value()
                nuevas_horas = dialogo.addhoras.value()
                nueva_relacion_id = dialogo.addrelacionan.currentData()
                nueva_descripcion = dialogo.addDesc.toPlainText().strip()

                if not nuevo_nombre or not nueva_fecha_inicio or not nueva_fecha_fin:
                    QMessageBox.warning(dialogo, "Error", "Todos los campos son obligatorios.")
                    return

                sql_update = """
                    UPDATE prototipos
                    SET Nombre = %s, Fecha_inicio = %s, Fecha_fin = %s, Presupuesto = %s,
                        Horas_est = %s, id_proto_rel = %s, Descripcion = %s
                    WHERE id = %s
                    """
                cursor.execute(sql_update, (nuevo_nombre, nueva_fecha_inicio, nueva_fecha_fin, nuevo_presupuesto,
                                            nuevas_horas, nueva_relacion_id, nueva_descripcion, proto_id))
                conexion.commit()

                protos[current_item] = {
                    "nombre": nuevo_nombre,
                    "fecha_ini": nueva_fecha_inicio,
                    "fecha_fin": nueva_fecha_fin,
                    "presu": nuevo_presupuesto,
                    "horas": nuevas_horas,
                    "id": proto_id,
                }
                main_window.listProto.item(current_item).setText(
                    f"{nuevo_nombre} - {nueva_fecha_inicio} - {nueva_fecha_fin} - Presupuesto: {nuevo_presupuesto}€ - Horas: {nuevas_horas}"
                )

                print(f"Prototipo '{nuevo_nombre}' actualizado correctamente.")
        except Exception as e:
            print(f"Error al actualizar el prototipo: {e}")
            QMessageBox.critical(main_window, "Error", "No se pudo actualizar el prototipo.")
        finally:
            cursor.close()
            conexion.close()

def anadir_telf():
    global main_window, dni_actual

    current_item = main_window.listEmpleados.currentRow()
    if current_item >= 0:
        empleado = empleados[current_item]
        dni = empleado["DNI"]
        if rol_actual == "user" and dni_actual != dni:
            QMessageBox.warning(main_window, "Permiso denegado", "Solo puedes añadir teléfonos a tu propio perfil.")
            return
        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql_select_id = "SELECT ID FROM empleados WHERE DNI = %s"
                cursor.execute(sql_select_id, (dni,))
                resultado = cursor.fetchone()

                if not resultado:
                    QMessageBox.warning(main_window, "Error", "No se encontró el empleado en la base de datos.")
                    return

                id_empleado = resultado[0]

                telefono, ok = QInputDialog.getText(main_window, "Añadir Teléfono", "Introduce el teléfono (9 dígitos):")
                if not ok or not telefono.isdigit() or len(telefono) != 9:
                    QMessageBox.warning(main_window, "Error", "Teléfono inválido. Debe ser un número de 9 dígitos.")
                    return

                sql_insert_telf = "INSERT INTO telf_empleados (id_empleado, telf) VALUES (%s, %s)"
                cursor.execute(sql_insert_telf, (id_empleado, telefono))
                conexion.commit()
                print(f"Teléfono {telefono} añadido correctamente para el empleado con ID {id_empleado}.")
                QMessageBox.information(main_window, "Éxito", f"Teléfono {telefono} añadido correctamente.")
            except Exception as e:
                print(f"Error al añadir el teléfono: {e}")
                QMessageBox.critical(main_window, "Error", "No se pudo añadir el teléfono.")
            finally:
                cursor.close()
                conexion.close()
        else:
            QMessageBox.critical(main_window, "Error", "No se pudo conectar a la base de datos.")

def inspeccionar_empleado():
    global main_window

    current_item = main_window.listEmpleados.currentRow()
    if current_item >= 0:
        empleado = empleados[current_item]
        dni = empleado["DNI"]

        if rol_actual == "user" and dni_actual != dni:
            QMessageBox.warning(main_window, "Permiso denegado", "Solo puedes inspeccionar tu propio perfil.")
            return

        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql_select = "SELECT nombre, DNI, Email, Titulacion, anos_experiencia, provincia FROM empleados WHERE DNI = %s"
                cursor.execute(sql_select, (dni,))
                resultado = cursor.fetchone()

                if not resultado:
                    QMessageBox.warning(main_window, "Error", "No se encontraron datos del empleado en la base de datos.")
                    return

                nombre, dni, email, titulacion, a_exp, provincia = resultado

                sql_select_telf = "SELECT telf FROM telf_empleados WHERE id_empleado = (SELECT ID FROM empleados WHERE DNI = %s)"
                cursor.execute(sql_select_telf, (dni,))
                telefonos = cursor.fetchall()

                dialogo = QDialog()
                loadUi("inspeccionar.ui", dialogo)
                dialogo.setWindowTitle("Inspeccionar Empleado")
                dialogo.labelusu2.setText(f"Usuario seleccionado - {nombre}")
                dialogo.LNombre.setText(f"Nombre: {nombre}")
                dialogo.LDNI.setText(f"DNI: {dni}")
                dialogo.LEmail.setText(f"Email: {email}")
                dialogo.LTitu.setText(f"Titulacion: {titulacion}")
                dialogo.LExp.setText(f"Años de experiencia: {a_exp}")
                dialogo.LProvicia.setText(f"Provincia: {provincia}")

                dialogo.listTelefonos.clear()
                for telf in telefonos:
                    dialogo.listTelefonos.addItem(telf[0])

                dialogo.btnEditTelf.clicked.connect(lambda: editar_telefono(dialogo, dni))
                dialogo.btnDeleteTelf.clicked.connect(lambda: eliminar_telefono(dialogo, dni))
                dialogo.exec_()

            except Exception as e:
                print(f"Error al obtener los datos del empleado: {e}")
                QMessageBox.critical(main_window, "Error", "No se pudo obtener los datos del empleado.")
            finally:
                cursor.close()
                conexion.close()
        else:
            QMessageBox.critical(main_window, "Error", "No se pudo conectar a la base de datos.")

def inspeccionar_recursos():
    global main_window

    # Verificar selección en la lista
    current_item = main_window.listrecursos.currentRow()
    if current_item < 0:
        QMessageBox.warning(main_window, "Error", "No se ha seleccionado ningún recurso.")
        return

    if not isinstance(recursos, list) or current_item >= len(recursos):
        QMessageBox.critical(main_window, "Error", "El recurso seleccionado no existe.")
        return

    recurso = recursos[current_item]
    id = recurso.get("id")
    nombre = recurso.get("nombre", "Desconocido")
    tipo = recurso.get("tipo", "Desconocido")

    if rol_actual == "user" and dni_actual != id:
        QMessageBox.warning(main_window, "Permiso denegado", "Solo puedes inspeccionar tu propio perfil.")
        return

    conexion = crear_conexion()
    if not conexion:
        QMessageBox.critical(main_window, "Error", "No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conexion.cursor()
        sql_select = "SELECT nombre, tipo, descripcion FROM recursos WHERE id = %s"
        cursor.execute(sql_select, (id,))
        resultado = cursor.fetchone()

        if not resultado:
            QMessageBox.warning(main_window, "Error", "No se encontraron datos del recurso en la base de datos.")
            return

        nombre, tipo, descripcion = resultado
        dialogo = QDialog()
        try:
            loadUi("inspeccionar_recursos.ui", dialogo)
        except Exception as e:
            print(f"Error al cargar la interfaz: {e}")
            QMessageBox.critical(main_window, "Error", f"No se pudo cargar la interfaz. Detalles: {e}")
            return

        dialogo.setWindowTitle("Inspeccionar recursos")
        dialogo.labelusu2.setText(f"Recurso seleccionado - {nombre}")
        dialogo.LNombre.setText(f"Nombre: {nombre}")
        dialogo.LTipo.setText(f"Tipo: {tipo}")
        dialogo.LDesc.setText(f"{descripcion}")

        dialogo.exec_()

    except Exception as e:
        print(f"Error al obtener los datos del recurso: {e}")
        QMessageBox.critical(main_window, "Error", f"No se pudo obtener los datos del recurso. Detalles: {e}")
    finally:
        cursor.close()
        conexion.close()


def inspeccionar_proto():
    global main_window

    current_item = main_window.listProto.currentRow()
    if current_item >= 0:
        proto = protos[current_item]
        id = proto["id"]

        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql_select = "SELECT Nombre, Fecha_inicio, Fecha_fin, Presupuesto, Horas_est, id_proto_rel, Descripcion FROM prototipos WHERE id = %s"
                cursor.execute(sql_select, (id,))
                resultado = cursor.fetchone()

                if not resultado:
                    QMessageBox.warning(main_window, "Error", "No se encontraron datos del empleado en la base de datos.")
                    return

                nombre, fecha_ini, fecha_fin, presu, horas, relacion, descp = resultado

                if relacion == None:
                    relacion = "No se relaciona"


                dialogo = QDialog()
                loadUi("inspeccionar_proto.ui", dialogo)
                dialogo.setWindowTitle("Inspeccionar Prototipos")
                dialogo.labelusu2.setText(f"Protoripo seleccionado - {nombre}")
                dialogo.LNombre.setText(f"Nombre: {nombre}")
                dialogo.Lini.setText(f"Fecha inicio: {fecha_ini}")
                dialogo.Lfin.setText(f"Fecha fin: {fecha_fin}")
                dialogo.Lpresu.setText(f"Presupuesto: {presu}€")
                dialogo.Lhoras.setText(f"Horas estimadas: {horas}")
                dialogo.Ldesc.setText(f"{descp}")
                dialogo.Lrela.setText(f"Se relaciona: {relacion}")
                dialogo.exec_()

            except Exception as e:
                print(f"Error al obtener los datos del empleado: {e}")
                QMessageBox.critical(main_window, "Error", "No se pudo obtener los datos del empleado.")
            finally:
                cursor.close()
                conexion.close()
        else:
            QMessageBox.critical(main_window, "Error", "No se pudo conectar a la base de datos.")


def editar_telefono(dialogo, dni):
    current_item = dialogo.listTelefonos.currentRow()
    if current_item >= 0:
        telefono_actual = dialogo.listTelefonos.item(current_item).text()

        nuevo_telefono, ok = QInputDialog.getText(dialogo, "Editar Teléfono", "Introduce el nuevo teléfono (9 dígitos):", text=telefono_actual)
        if ok and nuevo_telefono.isdigit() and len(nuevo_telefono) == 9:
            conexion = crear_conexion()
            if conexion:
                cursor = conexion.cursor()
                try:
                    sql_update_telf = "UPDATE telf_empleados SET telf = %s WHERE id_empleado = (SELECT ID FROM empleados WHERE DNI = %s) AND telf = %s"
                    cursor.execute(sql_update_telf, (nuevo_telefono, dni, telefono_actual))
                    conexion.commit()
                    dialogo.listTelefonos.item(current_item).setText(nuevo_telefono)
                    print(f"Teléfono actualizado de {telefono_actual} a {nuevo_telefono}.")
                except Exception as e:
                    print(f"Error al actualizar el teléfono: {e}")
                    QMessageBox.critical(dialogo, "Error", "No se pudo actualizar el teléfono.")
                finally:
                    cursor.close()
                    conexion.close()
        else:
            QMessageBox.warning(dialogo, "Error", "Teléfono inválido. Debe ser un número de 9 dígitos.")
    else:
        QMessageBox.warning(dialogo, "Error", "No se seleccionó ningún teléfono.")


def eliminar_telefono(dialogo, dni):
    current_item = dialogo.listTelefonos.currentRow()
    if current_item >= 0:
        telefono = dialogo.listTelefonos.item(current_item).text()

        respuesta = QMessageBox.question(
            dialogo,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar el teléfono {telefono}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            conexion = crear_conexion()
            if conexion:
                cursor = conexion.cursor()
                try:
                    sql_delete_telf = "DELETE FROM telf_empleados WHERE telf = %s AND id_empleado = (SELECT ID FROM empleados WHERE DNI = %s)"
                    cursor.execute(sql_delete_telf, (telefono, dni))
                    conexion.commit()
                    dialogo.listTelefonos.takeItem(current_item)
                    print(f"Teléfono {telefono} eliminado correctamente.")
                except Exception as e:
                    print(f"Error al eliminar el teléfono: {e}")
                    QMessageBox.critical(dialogo, "Error", "No se pudo eliminar el teléfono.")
                finally:
                    cursor.close()
                    conexion.close()
    else:
        QMessageBox.warning(dialogo, "Error", "No se seleccionó ningún teléfono.")

def abrir_ventana_gastos():
    global main_window

    main_window = QMainWindow()
    loadUi("V_G.ui", main_window)
    main_window.setWindowTitle("Ventana Gastos")

    configurar_ventana_gastos()
    main_window.btnAddGastos.clicked.connect(anadir_gastos)

    header()

    main_window.show()


def abrir_ventana_etapas():
    global main_window

    main_window = QMainWindow()
    loadUi("V_Et.ui", main_window)
    main_window.setWindowTitle("Ventana Etapas")

    configurar_ventana_etapas()

    header()
    main_window.btnAddEtapas.clicked.connect(anadir_etapas)
    main_window.btnDeleteEtapas.clicked.connect(eliminar_etapas)

    main_window.show()


def abrir_ventana_proto():
    global main_window

    main_window = QMainWindow()
    loadUi("V_P.ui", main_window)
    main_window.setWindowTitle("Ventana Prototipos")

    configurar_ventana_proto()

    main_window.btnEditProto.clicked.connect(editar_proto)
    main_window.btninspectProto.clicked.connect(inspeccionar_proto)
    main_window.btnDeleteProto.clicked.connect(eliminar_proto)
    main_window.btnAddProto.clicked.connect(anadir_proto)
    header()

    main_window.show()

def abrir_ventana_recursos():
    global main_window

    main_window = QMainWindow()
    loadUi("V_R.ui", main_window)
    main_window.setWindowTitle("Ventana Recursos")

    configurar_ventana_recursos()

    header()
    main_window.btnAddRecursos.clicked.connect(anadir_recursos)
    main_window.btnDeleteRecursos.clicked.connect(eliminar_recurso)
    main_window.btninspectRecursos.clicked.connect(inspeccionar_recursos)
    main_window.btnEditRecursos.clicked.connect(editar_recursos)


    main_window.show()

def abrir_ventana_principal():
    global main_window

    main_window = QMainWindow()
    loadUi("V_E.ui", main_window)

    configurar_ventana_principal()

    main_window.btnAdd.clicked.connect(anadir_empleado)
    main_window.btnDelete.clicked.connect(eliminar_empleado)
    main_window.btnEdit.clicked.connect(editar_empleado)
    main_window.btntlf.clicked.connect(anadir_telf)
    main_window.btninspect.clicked.connect(inspeccionar_empleado)
    header()

    main_window.show()


def main():
    global app, login_window

    app = QApplication(sys.argv)
    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    login_window = QDialog()
    loadUi("login.ui", login_window)

    login_window.btnLogin.clicked.connect(iniciar_sesion)

    if login_window.exec_() == QDialog.Accepted:
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()