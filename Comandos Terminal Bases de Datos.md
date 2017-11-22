### Comandos útiles del terminal relacionados con bases de datos

## Mongo


If you have installed mongodb through homebrew then you can simply start mongodb through

	>> brew services start mongodb

Then access the shell by

	>> mongo

You can shut down your db by

	>>brew services stop mongodb

For more options

	>>brew info mongodb


Asumiendo que los datos estan en el directorio de instalacion de mongo, puedes agregar bases de datos haciendo

	>> mongoimport --db test --collection nombre_base 
	--drop --file archivo.json --jsonArray
	
	
## Sqlite3
Abrir sqlite3 

	>> sqlite3
	
Importar base de datos .db

	>> .open archivo.db

Esquema de tabla

	>> .schema
	
El comando 

	>> .separator |

Sirve para indicar que el separador es el caracter "|" .
 
Ejecuta
  
	>>.import archivo.extension_tabla
 
Para importar el archivo a la tabla. (ej. .import datos.csv)

Ayuda

	>> .help
