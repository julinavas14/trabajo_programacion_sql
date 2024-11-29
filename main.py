import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QInputDialog
from PyQt5.sip import delete
from PyQt5.uic import loadUi
from conexion import crear_conexion

usuarios = {
    "admin": {"password": "1234", "role": "admin"},
    "user": {"password": "5678", "role": "user"},
}

empleados = [
    {"nombre": "Juan Pérez", "puesto": "Desarrollador", "DNI": "111111"},
    {"nombre": "Ana López", "puesto": "Diseñadora", "DNI": "222222"},
]

app = None
main_window = None
login_window = None
usuario_actual = None
rol_actual = None


def iniciar_sesion():
    global usuario_actual, rol_actual, main_window, login_window

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
        main_window.btnEdit.setEnabled(False)
        main_window.btnDelete.setEnabled(False)
        main_window.listEmpleados.hide()


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
    global main_window

    current_item = main_window.listEmpleados.currentRow()
    if current_item >= 0:
        empleado = empleados[current_item]
        nombre_anterior = empleado["nombre"]
        dni = empleado["DNI"].strip()

        #print(f"DNI seleccionado: {dni}")
        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                sql_select = "SELECT nombre, DNI, Email, Titulacion, anos_experiencia FROM empleados WHERE DNI = %s"
                cursor.execute(sql_select, (dni,))
                resultado = cursor.fetchone()

                if not resultado:
                    QMessageBox.warning(main_window, "Error", "No se encontraron datos del empleado en la base de datos.")
                    return

                nombre, DNI, email, titulacion, anos_experiencia = resultado

                dialogo = QDialog()
                loadUi("formulario.ui", dialogo)
                dialogo.setWindowTitle("Editar Empleado")

                dialogo.addnombre.setText(nombre)
                dialogo.addemail.setText(email)
                dialogo.addDNI.setText(DNI)
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
                    cursor.execute(sql_update, (nuevo_nombre, nuevo_email, nuevo_DNI, nueva_titulacion, nuevos_anos_experiencia, dni))
                    conexion.commit()
                    print(f"Empleado '{nombre_anterior}' actualizado a '{nuevo_nombre}' correctamente.")
            except Exception as e:
                print(f"Error al obtener o actualizar los datos del empleado: {e}")
                QMessageBox.critical(main_window, "Error", "No se pudo editar el empleado.")
            finally:
                cursor.close()
                conexion.close()

def anadir_telf():
    global main_window

    current_item = main_window.listEmpleados.currentRow()
    if current_item >= 0:
        empleado = empleados[current_item]
        dni = empleado["DNI"]

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