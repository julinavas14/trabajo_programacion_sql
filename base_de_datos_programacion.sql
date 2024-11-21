-- Base de datos para trabajo Programación

create database pro_sql;

use pro_sql;

create or replace table empleados(
	ID int auto_increment primary key,
	nombre varchar (20),
	DNI varchar (9),
	Email varchar (50),
	Titulación varchar (30),
	anos_experiencia int check (anos_experiencia > 0),
	Tipo_via enum('Calle', 'Plaza', 'Avenida'),
	Nombre_via varchar (20),
	Codigo_Postal varchar(5),
	Localidad varchar (50),
	Provincia varchar (50)
);