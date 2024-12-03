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

CREATE OR REPLACE TABLE prototipos(
	id INT AUTO_INCREMENT,
	id_proto_rel INT,
	Nombre VARCHAR(20)unique,
	Descripción VARCHAR(200),
	Fecha_inicio DATE,
	Fecha_fin DATE,
	Presupuesto FLOAT(10,2) UNSIGNED,
	Horas_est INT(6),
	PRIMARY KEY(id),
	CONSTRAINT rel FOREIGN KEY(id_proto_rel)
		REFERENCES prototipos(id)
		ON DELETE set null,
	CONSTRAINT fecha CHECK (Fecha_fin > Fecha_inicio),
	CONSTRAINT max_horas CHECK (Horas_est >= 30)
);

CREATE OR REPLACE TABLE gastos(
	id INT AUTO_INCREMENT,
	id_emp INT,
	id_proto INT,
	Descripcion VARCHAR(200),
	Fecha DATE,
	Importe FLOAT(7,2) UNSIGNED,
	Tipo VARCHAR(20),
	PRIMARY KEY(id),
	CONSTRAINT FKemp FOREIGN KEY(id_emp)
		REFERENCES empleados(id)
		ON DELETE cascade,
	CONSTRAINT FKproto FOREIGN KEY(id_proto)
		REFERENCES prototipos(id)
		ON DELETE CASCADE,
	CONSTRAINT lim_gasto CHECK (Importe <= 20000)
);

CREATE OR REPLACE TABLE etapas(
	id INT auto_increment PRIMARY KEY,
	nombre VARCHAR(20),
	fecha_inicio DATE,
	fecha_fin DATE,
	estado ENUM('desarrollo', 'finalizada'),
	id_protot INT,
	CONSTRAINT id_prototipos FOREIGN KEY (id_protot)
		REFERENCES prototipos(id)
);

create or replace TABLE recursos(
	id int(3) auto_increment primary key,
	nombre varchar(20),
	descripcion varchar(50),
	tipo varchar(20)
);
