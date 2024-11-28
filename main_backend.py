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
