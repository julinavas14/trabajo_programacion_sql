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

create or replace table telf_empleados(
    id_empleado int,
    telf char(9),
    primary key(id_emlpeado, telf),
    foreign key id_emlpeado
        references empleados(ID)
        on delete cascade on update cascade
);

create or replace table gastos(
	id int auto_increment primary key,
	descp varchar(255),
	fecha date,
	importe decimal(10, 2),
	tipo varchar(50),
	id_empleado int,
	constraint fk_g_e foreign key (id_empleado)
		references empleados(id)
		on delete cascade on update cascade
);