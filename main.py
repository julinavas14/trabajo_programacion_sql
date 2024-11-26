import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QInputDialog
from PyQt5.uic import loadUi
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

    usuario = login_window.inputUsuario.text()
    contrasena = login_window.inputContrasena.text()

    if usuario in usuarios and usuarios[usuario]["password"] == contrasena:
        usuario_actual = usuario
        rol_actual = usuarios[usuario]["role"]

        login_window.accept()
        abrir_ventana_principal()
    else:
        login_window.labelError.setText("Usuario o contraseña incorrectos")


def configurar_ventana_principal():
    global main_window, rol_actual

    main_window.labelUsuario.setText(f"Bienvenido, {usuario_actual} ({rol_actual})")

    if rol_actual == "admin":
        main_window.btnAdd.setEnabled(True)
        main_window.btnEdit.setEnabled(True)
        main_window.btnDelete.setEnabled(True)
        main_window.listEmpleados.addItems(
            [f"{emp['nombre']} - {emp['puesto']}" for emp in empleados]
        )
    else:
        main_window.btnAdd.setEnabled(False)
        main_window.btnEdit.setEnabled(False)
        main_window.btnDelete.setEnabled(False)
        main_window.listEmpleados.hide()


def anadir_empleado():
    global main_window

    nombre, ok = QInputDialog.getText(main_window, "Añadir empleado", "Nombre:")
    if ok:
        puesto, ok = QInputDialog.getText(main_window, "Añadir empleado", "Puesto:")
        if ok:
            empleados.append({"nombre": nombre, "puesto": puesto})
            main_window.listEmpleados.addItem(f"{nombre} - {puesto}")


def eliminar_empleado():
    global main_window

    current_item = main_window.listEmpleados.currentRow()
    if current_item >= 0:
        empleados.pop(current_item)
        main_window.listEmpleados.takeItem(current_item)


def editar_empleado():
    global main_window

    current_item = main_window.listEmpleados.currentRow()
    if current_item >= 0:
        empleado = empleados[current_item]
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


def abrir_ventana_principal():
    global main_window

    main_window = QMainWindow()
    loadUi("main.ui", main_window)

    configurar_ventana_principal()

    main_window.btnAdd.clicked.connect(anadir_empleado)
    main_window.btnDelete.clicked.connect(eliminar_empleado)
    main_window.btnEdit.clicked.connect(editar_empleado)

    main_window.show()


# Función principal para iniciar la aplicación
def main():
    global app, login_window

    app = QApplication(sys.argv)

    login_window = QDialog()
    loadUi("untitled.ui", login_window)

    login_window.btnLogin.clicked.connect(iniciar_sesion)

    if login_window.exec_() == QDialog.Accepted:
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()