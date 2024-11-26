import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QInputDialog
from PyQt5.sip import delete
from PyQt5.uic import loadUi
from conexion import crear_conexion
import qdarkstyle

usuarios = {
    "admin": {"password": "1234", "role": "admin"},
    "user": {"password": "5678", "role": "user"},
}

empleados = [
    {"nombre": "Juan Pérez", "puesto": "Desarrollador"},
    {"nombre": "Ana López", "puesto": "Diseñadora"},
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

                if email == "aroldanrabanal@safareyes.es" or email == "jnavasmedina@safareyes.es":
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

    main_window.labelUsuario.setText(f"Bienvenido, {usuario_actual} ({rol_actual})")

    empleados = []
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:

            cursor.execute("SELECT nombre, Titulacion FROM empleados")
            resultados = cursor.fetchall()

            empleados = [{"nombre": fila[0], "puesto": fila[1]} for fila in resultados]

            main_window.listEmpleados.clear()
            for empleado in empleados:
                main_window.listEmpleados.addItem(f"{empleado['nombre']} - {empleado['puesto']}")

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
    conexion = crear_conexion()


    nombre, ok = QInputDialog.getText(main_window, "Añadir empleado", "Nombre:")
    if ok:
        puesto, ok = QInputDialog.getText(main_window, "Añadir empleado", "Puesto:")
        if ok:
            empleados.append({"nombre": nombre, "puesto": puesto})
            main_window.listEmpleados.addItem(f"{nombre} - {puesto}")
            if conexion:
                cursor = conexion.cursor()

                sql_insert = "INSERT INTO empleados(nombre, Titulacion) VALUES (%s, %s)"
                try:
                    cursor.execute(sql_insert, (nombre, puesto))
                except Exception as e:
                    print(f"Error al insertar la fila: {e}")

                conexion.commit()
                print("Datos insertados correctamente.")
                cursor.close()
                conexion.close()


def eliminar_empleado():
    global main_window

    current_item = main_window.listEmpleados.currentRow()

    if current_item >= 0:
        empleado = empleados[current_item]
        nombre_empleado = empleado["nombre"]

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
                    sql_delete = "DELETE FROM empleados WHERE nombre = %s"
                    cursor.execute(sql_delete, (nombre_empleado,))
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

        nuevo_nombre, ok = QInputDialog.getText(
            main_window, "Editar empleado", "Nombre:", text=empleado["nombre"]
        )
        if ok:
            nuevo_puesto, ok = QInputDialog.getText(
                main_window, "Editar empleado", "Puesto:", text=empleado["puesto"]
            )
            if ok:
                empleados[current_item] = {"nombre": nuevo_nombre, "puesto": nuevo_puesto}
                main_window.listEmpleados.item(current_item).setText(
                    f"{nuevo_nombre} - {nuevo_puesto}"
                )

                conexion = crear_conexion()
                if conexion:
                    cursor = conexion.cursor()
                    try:
                        sql_update = "UPDATE empleados SET nombre = %s, Titulación = %s WHERE nombre = %s"
                        cursor.execute(sql_update, (nuevo_nombre, nuevo_puesto, nombre_anterior))
                        conexion.commit()
                        print(f"Empleado '{nombre_anterior}' actualizado a '{nuevo_nombre}' correctamente.")
                    except Exception as e:
                        print(f"Error al actualizar el empleado en la base de datos: {e}")
                    finally:
                        cursor.close()
                        conexion.close()

def abrir_ventana_principal():
    global main_window

    main_window = QMainWindow()
    loadUi("main.ui", main_window)

    configurar_ventana_principal()

    main_window.btnAdd.clicked.connect(anadir_empleado)
    main_window.btnDelete.clicked.connect(eliminar_empleado)
    main_window.btnEdit.clicked.connect(editar_empleado)

    main_window.show()


def main():
    global app, login_window

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    login_window = QDialog()
    loadUi("untitled.ui", login_window)

    login_window.btnLogin.clicked.connect(iniciar_sesion)

    if login_window.exec_() == QDialog.Accepted:
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()