from conexion import crear_conexion
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
