-- Base de datos para trabajo Programación

create database pro_sql;

use pro_sql;

create or replace table empleados(
	ID int auto_increment primary key,
	nombre varchar (20),
	DNI char (9) unique,
	Email varchar (50),
	Titulacion varchar (30),
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
    primary key(id_empleado, telf),
    foreign key (id_empleado)
        references empleados(ID)
        on delete cascade on update cascade
);

CREATE OR REPLACE TABLE prototipos(
	id INT AUTO_INCREMENT,
	id_proto_rel INT,
	Nombre VARCHAR(20)unique,
	Descripcion VARCHAR(200),
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

create or replace table se_asignan(
	id_recursos int(3),
	id_etapas int(3),
	primary key (id_recursos, id_etapas),
	constraint id_asignan_recursos foreign key(id_recursos)
		references recursos(id),
	constraint id_asignan_etapas foreign key(id_etapas)
		references etapas(id)
);

INSERT INTO empleados (nombre, DNI, Email, Titulacion, anos_experiencia, Tipo_via, Nombre_via, Codigo_Postal, Localidad, Provincia)
VALUES 
('admin', 'admin','admin', 'admin', 9999, null, null, null, null, null ),
('Juan Pérez', '12345678A', 'juan.perez@example.com', 'Ingeniero Informático', 5, 'Calle', 'Gran Vía', '28013', 'Madrid', 'Madrid'),
('Ana López', '87654321B', 'ana.lopez@example.com', 'Técnico en Redes', 3, 'Calle', 'Mayor', '08001', 'Barcelona', 'Barcelona'),
('Carlos Ruiz', '11223344C', 'carlos.ruiz@example.com', 'Desarrollador Web', 7, 'Calle', 'Diagonal', '46001', 'Valencia', 'Valencia');

INSERT INTO telf_empleados (id_empleado, telf) 
VALUES 
(1, '600123456'),
(1, '600654321'),
(2, '610987654');

INSERT INTO prototipos (id_proto_rel, Nombre, Descripcion, Fecha_inicio, Fecha_fin, Presupuesto, Horas_est)
VALUES 
(NULL, 'AppMovil', 'Desarrollo de una aplicación móvil', '2024-01-01', '2024-06-01', 10000.00, 200),
(1, 'WebCorp', 'Diseño de una página corporativa', '2024-02-01', '2024-07-01', 15000.00, 300),
(2, 'IoTProject', 'Implementación de IoT para hogares', '2024-03-01', '2024-09-01', 20000.00, 400);

INSERT INTO gastos (id_emp, id_proto, Descripcion, Fecha, Importe, Tipo) 
VALUES 
(1, 1, 'Compra de software', '2024-01-15', 500.00, 'Licencia'),
(2, 2, 'Adquisición de servidores', '2024-02-20', 1500.00, 'Hardware'),
(3, 3, 'Gastos de publicidad', '2024-03-10', 200.00, 'Marketing');

INSERT INTO etapas (nombre, fecha_inicio, fecha_fin, estado, id_protot) 
VALUES 
('Análisis', '2024-01-01', '2024-02-01', 'desarrollo', 1),
('Diseño', '2024-02-02', '2024-03-01', 'desarrollo', 1),
('Implementación', '2024-03-02', '2024-06-01', 'finalizada', 2);

INSERT INTO recursos (nombre, descripcion, tipo) 
VALUES 
('Servidor AWS', 'Instancia EC2', 'Infraestructura'),
('Laptop Dell', 'Portátil para desarrollo', 'Hardware'),
('Licencia Figma', 'Software de diseño', 'Software');

INSERT INTO se_asignan (id_recursos, id_etapas) 
VALUES 
(1, 1),
(2, 2),
(3, 3);
