# **Backend Learned By Lucas Ferreyra (NeoN KiKe)**
## **Fecha de creacion: 4/9/2025**

## Explicacion learned
### ¿Que es learned?
Learned es un programa creado para poder facilitar la interaccion entre alumnos y profesores en el ambiente de clases.

### ¿Que diferencia a learned de otros programas?
Learned a diferencia de otros programas fue ya creado con la idea de ser una aplicacion para escuelas, Por lo que tiene maxima atencion a los detalles para que sea user friendly.
Ademas de eso presenta muchas opciones para mejorar la experiencia de usuario.

### ¿De donde surgio learned?
Learned sugio de la idea de revolucionar la educacion digital, Debido a la experiencia de los creadores de learned en epoca de pandemia.

### ¿Que tipo de monetizacion tendra learned?
Bueno mas alla de poder monetizar cosas cosmeticas learned podria dar la opcion de monetizar algunas opciones como la seleccion de servidores de la nube o añadir un limite de clases para crear o litimar las clases.

### ¿Quienes son sus creadores?
- Lucas Ferreyra
- Luca Aladro
- Mirko Isasmendi
- Santino Micheli
- Bautista Ithurat

## Descripcion del backend y base de datos

### Explicación base de datos:

La base de datos se realizo por la necesidad de almacenar cuentas y tareas para la aplicación, Ya que sin la base de datos esta tendría muchas limitaciones y no podría ser realizado.
El enfoque de la base de datos fue dado a la mejor comunicación de la misma con las tablas relacionales para evitar tiempos elevados en las peticiones de información.

### Descripción de base de datos:

Nombre de la base de datos: Learned DB

Motor utilizado. SQL

Problema que resuelve: El problema que resuelve es el echo de poder almacenar tareas, cuentas, y relaciones entre las mismas además de mas información para evitar que los usuarios tengan que colocar su información, crear clases y demás cosas cada que el server tenga un problema de conexión

Información que almacena:
Información de cuenta, Tareas, Clases, relaciones entre usuarios y clases, además de muchas otras relaciones y datos importantes para la utilización de la aplicación.

### Descripción de backend:

El backend busca la mayor optimización en peticiones con la mejor funcionalidad y seguridad posible desde el aprendizaje que hemos tenido estos años.

### El backend busca las siguiente funcionalidades:

- Cuentas obligatorias, Login y Register (cuentas con roles ej: Profesor, Alumno, Admin).
- Notificaciones de usuarios (invitaciones, Tareas nuevas, Tareas atrasadas).
- Clases a las que el usuario pertenece.
- Tareas activas por clases.
- Llamadas en vivo dentro de las clases.
- Chat de mensajería en vivo para la clase.
- Configuración de cuenta y de clase para mayor customización de todo.

### Optimizaciones que busca el backend:

El backend esta en busca la optimización masiva de las peticiones de la base de datos y procesos de la programación es decir si una petición tarda demasiado por tener en cuenta la mayor cantidad de cosas se va a buscar como optimizarlo reduciendo condiciones ya sea agregando nuevas tablas o sacando condicionales innecesarios que solo retrasan la utilización, Además de eso se va a tener en cuenta cosas como que a la hora de encriptar no se tarde demasiado para poder reducir los tiempos de espera

### Tecnologías implementadas:

Actualmente para la versión de prueba no se está prestando atención a las tecnologías utilizadas pero se esta trabajando con lo siguiente

- Python
- flask
- cors
- bcrypt

### Utilizacion del backend

La base de datos actualmente va con sql dentro de una carpeta que se debe crear y el orden quedaria asi
```
rot//:db/app.db
```

Tambien hace falta instalar las siguientes librerias
```
pip install flask
pip install cors
pip install bcrypt
```

Luego Para iniciar el backend se debe ejecutar el siguiente comando
```
python app.py
```

y listo ya tendras el backend funcionando

# **Muchas gracias por leer <3**
