# Infraestructura SIE

Este repositorio contiene la configuración necesaria para levantar el ecosistema de la asignatura **Sistemas de Información Empresariales** (SIE). Configuraremos un entorno profesional utilizando GitHub y Docker, lo que nos permitirá realizar las actividades planificadas con diferentes herramientas de gestión empresarial, usando todos la misma infraestructura, minimizando los problemas técnicos y facilitando la limpieza del equipo una vez finalizado el trabajo.

## 📑 Índice
- [Infraestructura SIE](#infraestructura-sie)
  - [📑 Índice](#-índice)
  - [🧰 Herramientas](#-herramientas)
  - [📂 Estructura del Repositorio](#-estructura-del-repositorio)
  - [🛠️ Requisitos y Herramientas Externas](#️-requisitos-y-herramientas-externas)
  - [🚀 Inicio Rápido](#-inicio-rápido)
  - [⚙️ Configuración](#️-configuración)
    - [A. SuiteCRM (CRM)](#a-suitecrm-crm)
    - [B. smtp4dev (Servidor de correo electrónico)](#b-smtp4dev-servidor-de-correo-electrónico)
    - [C. Bonita Runtime (BPM)](#c-bonita-runtime-bpm)
    - [D. Odoo (ERP)](#d-odoo-erp)
      - [Módulos Personalizados en Odoo (Addons)](#módulos-personalizados-en-odoo-addons)
    - [E. n8n (iPaaS)](#e-n8n-ipaas)
    - [F. pgAdmin (Gestión de Bases de Datos PostgreSQL)](#f-pgadmin-gestión-de-bases-de-datos-postgresql)
    - [G. phpMyAdmin (Gestión de Bases de Datos MariaDB/MySQL)](#g-phpmyadmin-gestión-de-bases-de-datos-mariadbmysql)
    - [H. Ollama (IA - LLM)](#h-ollama-ia---llm)
    - [I. FastAPI (API personalizada)](#i-fastapi-api-personalizada)
  - [🌐 Red interna Docker](#-red-interna-docker)
  - [🖥️ Alternativas (Instalación Local)](#️-alternativas-instalación-local)
  - [🐳 Comandos útiles de Docker](#-comandos-útiles-de-docker)
  - [❓ FAQ y Resolución de Problemas](#-faq-y-resolución-de-problemas)

<span id="herramientas"></span>
## 🧰 Herramientas
Las herramientas con las que vamos a trabajar son:

| Herramienta | Categoría | Función Principal |
|------------|-----------|-------------------|
| Docker | Virtualización y Contenedores | Plataforma que permite ejecutar y aislar las aplicaciones en contenedores para que funcionen igual en cualquier equipo. |
| Odoo | ERP (Enterprise Resource Planning) | Gestión integral de una empresa: ventas, inventario, compras, contabilidad, RRHH, etc. |
| SuiteCRM | CRM (Customer Relationship Management) | Gestión de clientes, oportunidades comerciales, campañas de marketing y servicio posventa. |
| Bonita | BPM (Business Process Management) | Automatización y ejecución de procesos de negocio. |
| n8n | iPaaS (Integration Platform as a Service) | Conecta aplicaciones y automatiza tareas mediante flujos de trabajo. |
| smtp4dev | Servidor de Email de Pruebas | Atrapa los correos salientes de las aplicaciones para verlos en un panel local sin enviar emails reales. |
| pgAdmin | Administración de Bases de Datos PostgreSQL | Interfaz web para administrar y monitorizar bases de datos PostgreSQL. |
| phpMyAdmin | Administración de Bases de Datos MariaDB/MySQL | Interfaz web para administrar y monitorizar bases de datos MariaDB o MySQL. |
| Ollama | IA - LLM | Permite descargar, gestionar y ejecutar modelos de lenguaje de forma local. |
| FastAPI | API personalizada | Framework de Python para crear APIs REST de forma rápida y sencilla. | 

<span id="estructura"></span>
## 📂 Estructura del Repositorio

La mayor parte de los servicios almacenan sus datos en volúmenes Docker. Las carpetas que aparecen a continuación contienen únicamente los archivos necesarios para crear y desplegar la infraestructura, así como otros que es habitual querer consultar o modificar.

* `bonita/`: 
    * `exports/`: Carpeta recomendada para guardar tus ficheros de Bonita Studio (`.bos`, `.bar`,...).
* `fastapi/`: 
    * `Dockerfile`: Instrucciones de construcción de la imagen de Python personalizada.
    * `main.py`: Contiene la definición de la API y sus endpoints.
    * `requirements.txt`: Lista de dependencias de Python necesarias para ejecutar la API definida en `main.py`.
* `n8n/`:
    * `workflows/`: Carpeta donde exportar tus flujos exportados manualmente (`.json`) desde n8n.
* `odoo/`:
    * `addons/`: Carpeta para tus módulos personalizados.
    * `config/`: Contiene el fichero `odoo.conf` de configuración.
* `suitecrm/`:
    * `languages/`: Contiene el pack de idioma español (.zip) listo para instalar tras lanzar el servicio. Puedes descargar y añadir aquí otros idiomas si lo deseas (más abajo se describe cómo hacerlo).
    * `upload/`: Carpeta utilizada para persistir los documentos y archivos subidos al CRM.
    * `Dockerfile`: Instrucciones de construcción de la imagen de PHP personalizada.
* `.env`: Definición de variables de entorno utilizadas en `docker-compose.yml`.
* `.gitignore`: Fichero en el que indicar carpetas o ficheros a ignorar por el control de versiones de Git.
* `docker-compose.yml`: Archivo principal que define y orquesta todos los contenedores para los diferentes servicios.
* `README.md`: Este documento.

También hay varios ficheros `.gitkeep` en carpetas inicialmente vacías para que el control de versiones no las ignore por estar vacías.


<span id="requisitos"></span>
## 🛠️ Requisitos y Herramientas Externas

Antes de comenzar, necesitaremos tener instaladas las siguientes herramientas "externas" (que no se encuentran en el repositorio que hemos creado):

1.  **Docker Desktop:** [Descargar](https://www.docker.com/products/docker-desktop/)
    * Es el motor que permite ejecutar todos los servicios (Odoo, SuiteCRM, etc.) contenidos en este repositorio.
    * **IMPORTANTE**: Hay que aceptar la licencia (Docker Subscription Service Agreement) aunque podemos saltarnos los pasos que pidan crear una cuenta o iniciar sesión.
2.  **[OPCIONAL] Acceso a una cuenta de GitHub:** [Enlace](https://github.com)
    * Necesaria para crear y alojar tu propio repositorio a partir del repositorio "plantilla" que proporcionamos.
3.  **[OPCIONAL] Git:** [Descargar](https://git-scm.com/downloads) 
    * Permite mantener tu repositorio actualizado y gestionar versiones. Si no deseas usarlo, puedes descargar el repositorio como un archivo ZIP.
4.  **Bonita Studio:** Información para su descarga en [Enseñanza Virtual](https://ev.us.es/)
    * Necesario para diseñar y modelar tus procesos de negocio, que posteriormente se ejecutarán en el motor (Bonita Runtime) incluido en el `docker-compose.yml`. 
    * **IMPORTANTE**: Las versiones de Bonita Studio y de Bonita Runtime deben ser la misma para que los procesos se puedan desplegar correctamente. En [Enseñanza Virtual](https://ev.us.es/) encontrarás los enlaces para su descarga, ya sea para Windows, Mac o Linux.
    * Requiere **Java 17** o superior. Puedes descargarlo desde la web de [Adoptium](https://adoptium.net), una opción que usan muchas empresas por tener una licencia más permisiva, o desde [Oracle](https://www.oracle.com/es/java/technologies/downloads), que tiene más restricciones pero que también podemos usar sin coste.


<span id="inicio"></span>
## 🚀 Inicio Rápido

1. **Crear tu propio repositorio:** Inicia sesión en GitHub y pulsa el botón verde **"Use this template"** arriba a la derecha en el repositorio del curso.
    * **Nombre del repositorio:** Es _OBLIGATORIO_ que siga el formato: `sie-UVUS` (siendo `UVUS` tu propio UVUS).
    * **Privacidad:** Privado (si fuera necesario el profesor podrá pedirte que lo añadas como colaborador).

2. **Clonar o Descargar:** Clona el repositorio (por ejemplo, usando `git clone <tu-nueva-url>` o usando Visual Studio Code), o descarga el ZIP (pulsando el botón `Code` y luego `Download ZIP`) y descomprímelo.

3. **Arrancar:** Entra en la carpeta desde una terminal y ejecuta: **`docker compose up -d --build`**.
    > La primera ejecución puede tardar varios minutos porque Docker descargará las imágenes necesarias y construirá las imágenes personalizadas. En las siguientes ejecuciones el arranque será mucho más rápido.

4. **Verificar:** No es necesario configurar todavía ninguna herramienta. Simplemente comprueba que todos los servicios responden correctamente y sin errores:
    * **Odoo:** [http://localhost:8069](http://localhost:8069)
    * **SuiteCRM:** [http://localhost:8080](http://localhost:8080)
    * **Bonita Runtime:** [http://localhost:8081](http://localhost:8081)
    * **n8n:** [http://localhost:5678](http://localhost:5678)
    * **smtp4dev:** [http://localhost:3000](http://localhost:3000)
    * **pgAdmin:** [http://localhost:5050](http://localhost:5050)
    * **phpMyAdmin:** [http://localhost:8088](http://localhost:8088)
    * **Ollama:** [http://localhost:11434](http://localhost:11434)
    * **FastAPI:** [http://localhost:8000](http://localhost:8000)

> **Nota sobre los parámetros de `docker compose up -d --build`:**
>    * El parámetro `-d` activa el "*detached mode*", es decir, ejecuta los contenedores en segundo plano.
>    * El parámetro `--build` solo es necesario la primera vez o si se modifica algún `Dockerfile` usado para crear alguna de las imágenes usadas en el *compose* (no te preocupes por tus datos; gracias a los volúmenes de Docker, no perderás configuraciones ni archivos aunque reinicies los contenedores o reconstruyas las imágenes).


<span id="configuracion"></span>
## ⚙️ Configuración

En esta sección vamos a comentar aspectos básicos para poder empezar a trabajar con las herramientas incluidas en este repositorio.

<span id="config-suitecrm"></span>
### A. SuiteCRM (CRM)

A diferencia del resto de herramientas, SuiteCRM debe terminar de instalarse una vez lanzado el servicio.

Antes de nada, debemos saber que al acceder al instalador en [http://localhost:8080](http://localhost:8080) se hace una comprobación inicial que no debe dar errores.

A continuación seguiremos los pasos del asistente de instalación, que nos pedirá que rellenemos lo siguiente:

* **URL OF SUITECRM INSTANCE:** `http://localhost:8080`
* **SuiteCRM Database User:** suitecrm_user
* **SuiteCRM Database User Password:** suitecrm_pass
* **Host Name:** db_suitecrm (Es muy importante usar el nombre del servicio de Docker, no "localhost")
* **Database Name:** suitecrm_db
* **Database Port:** 3306 (Es el puerto por defecto de MariaDB)
* **POPULATE DATABASE WITH DEMO DATA?:** Sí (Recomendable para ver ejemplos de cuentas, contactos, etc.).
* **SuiteCRM Application Admin Name:** [escribe el username que quieras para tu usuario administrador, por ejemplo tu *UVUS*]
* **SuiteCRM Admin User Password:** [escribe la contraseña que quieras para tu usuario administrador]

Una vez instalado SuiteCRM podremos iniciar sesión con el usuario y contraseña indicados durante la instalación, y nos aparecerá el asistente que recopila información básica de nuestro usuario, aunque también se podrá hacer más adelante, por ejemplo cuando tengamos instalado el idioma español y el Euro como moneda.

Para poner SuiteCRM en español una vez completado el asistente, accede con el usuario administrador que has creado y sigue estos pasos:
1. **Instalación:** Pulsa el icono de usuario en la esquina superior derecha > Menú **Admin** > Sección **Admin Tools** > Opción **Module Loader**, sube el archivo `.zip` que está en la carpeta `suitecrm/languages/` del repositorio, pulsa **Install** y luego **Commit**.
2. **Verificación:** Ve a **Admin** > **Languages**. Comprueba que el idioma "Spanish" aparece en la columna **Enabled**. Si no es así, muévelo a esa columna y pulsa el botón para guardar los cambios.
3. **Selección:** Cierra sesión. En la pantalla de inicio de sesión verás un selector para elegir el idioma que desees.

> **Descarga de traducciones:** Puedes encontrar los paquetes de idioma listos para descargar en [SuiteCRM Translations (SourceForge)](https://sourceforge.net/projects/suitecrmtranslations/files/). Para las versiones más recientes o para colaborar en la traducción, visita [SuiteCRM Crowdin](https://crowdin.com/project/suitecrmtranslations).

---

<span id="config-smtp4dev"></span>
### B. smtp4dev (Servidor de correo electrónico)

Entre las herramientas se encuentra un servidor de correo "fake" (smtp4dev), que simula el envío de correos electrónicos para hacer pruebas sin necesidad de enviarlos realmente. Será util para configurar las demás herramientas y probar funcionalidades que impliquen el envío de correos electrónicos. Por ejemplo, en SuiteCRM podremos configurar la creación de nuevos usuarios haciendo que reciban su contraseña de acceso por email, o en Bonita podremos diseñar procesos que en un determinado paso envíen un correo electrónico.

La configuración que debemos usar en una herramienta desde la que queremos usar este servicio varía en función de si dicha herramienta se ejecuta dentro de la red de Docker (otros servicios incluidos en nuestra infraestructura) o fuera de la red de Docker (una herramienta externa a la infraestructura, como Bonita Studio). Por ejemplo, podemos diseñar procesos en Bonita Studio con tareas que envían correos electrónicos y desplegar esos procesos en Bonita Runtime, pero Bonita Studio es una herramienta de escritorio que reside fuera de la red de Docker y Bonita Runtime es uno de los servicios que se ejecutan dentro de la red de Docker, por lo que la configuración para llegar hasta smtp4dev será distinta. A continuación mostramos los parámetros a usar en cada caso.

| Configuración | Desde Docker (Odoo,SuiteCRM,n8n,Bonita Runtime,...) | Desde fuera de Docker (Bonita Studio,...) |
| :--- | :--- | :--- |
| **Servidor (Host)** | `smtp4dev` | `localhost` |
| **Puerto SMTP** | `25` | `2525` |

> **Ver Emails:** Accede a [http://localhost:3000](http://localhost:3000) para ver los correos capturados.

---

<span id="config-bonita"></span>
### C. Bonita Runtime (BPM)

Tras lanzar el servicio el sistema no tendrá nada (organización, BDM, procesos,...). Todos estos elementos deberán ser desplegados por el usuario denominado "superadministrador", que es el único que inicialmente puede iniciar sesión con las credenciales `install / install`. 

Una vez desplegada la organización, con sus usuarios, perfiles y membresías, ya se podrá acceder con los usuarios "normales" para hacer uso de los procesos y aplicaciones que se hayan desplegado tras ser diseñados en la herramienta Bonita Studio.

---

<span id="config-odoo"></span>
### D. Odoo (ERP)

Al acceder a Odoo por primera vez podremos crear una primera base de datos para gestionar nuestra organización (podemos crear varias, por ejemplo, una para realizar pruebas y otra para su uso en producción). En este punto tendremos que usar la **"Master password"** definida en el fichero `odoo/config/odoo.conf` que por defecto es `admin_password`. También será necesaria para crear nuevas bases de datos o realizar operaciones sobre las bases de datos que ya tengamos creadas. 

#### Módulos Personalizados en Odoo (Addons)
Si has añadido una carpeta de módulo en `odoo/addons/`, sigue estos pasos para que aparezca:
1. **Activar Modo Desarrollador:** Ve a **Ajustes** y, al final de la página, pulsa en **Activar modo desarrollador**.
2. **Actualizar Lista de Aplicaciones:** Ve al menú **Aplicaciones** y, en la barra superior, pulsa en **Actualizar lista de aplicaciones** > **Actualizar**.
3. **Instalar:** Busca tu módulo en el buscador (quita el filtro "Aplicaciones" si no aparece) y pulsa **Activar**.
    
> **Nota:** Si has hecho cambios en el código Python del módulo, debes reiniciar el contenedor con `docker compose restart odoo`. Si solo has cambiado XML/CSS, basta con **Actualizar** el módulo desde la interfaz.

---

<span id="config-n8n"></span>
### E. n8n (iPaaS)

Esta herramienta permite crear flujos de trabajo automatizados que integran los diferentes servicios desplegados en esta infraestructura empresarial, además de miles de aplicaciones y servicios externos para los que existen conectores listos para usar. Por ejemplo, podremos crear flujos que reaccionen ante eventos en Odoo o SuiteCRM, consulten un modelo de IA mediante Ollama o invoquen nuestra API desarrollada con FastAPI. Este tipo de integraciones requerirán configurar el acceso a esos servicios y sus API.

La primera vez que accedas a n8n será necesario crear una cuenta de usuario local para administrar la plataforma.

---

<span id="config-pgadmin"></span>
### F. pgAdmin (Gestión de Bases de Datos PostgreSQL)

Usaremos esta herramienta para acceder directamente a las bases de datos PostgreSQL que usan Odoo y Bonita Runtime, lo que nos permitirá ver las tablas que se utilizan y los campos que incluyen. En principio, los datos se gestionarán siempre a través de las interfaces de las herramientas (Odoo y Bonita) que permiten crear nuevos registros y modificarlos, pero a veces, para tareas de bajo nivel o depuración de errores, puede venirnos bien este método para acceder a los datos de forma "directa". 

Podremos acceder usando las siguientes credenciales:
* **Email:** `admin@sie.com`
* **Password:** `admin`

Para añadir los servidores, haz clic derecho en **Servers** > **Register** > **Server...** y usa la siguiente configuración:

**1. Servidor Odoo:**
* **General (Name):** `Odoo DB`
* **Connection (Host name/address):** `db_odoo`
* **Username:** `odoo`
* **Password:** `odoo_pass`

**2. Servidor Bonita:**
* **General (Name):** `Bonita DB`
* **Connection (Host name/address):** `db_bonita`
* **Username:** `bonita`
* **Password:** `bpm`

> Los nombres `db_odoo` y `db_bonita` son los nombres de los servicios definidos en el fichero `docker-compose.yml`. Funcionan porque pgAdmin se ejecuta dentro de la misma red Docker que las bases de datos de Odoo y Bonita.

---

<span id="config-phpmyadmin"></span>
### G. phpMyAdmin (Gestión de Bases de Datos MariaDB/MySQL)

Usaremos esta herramienta para acceder directamente a la base de datos MariaDB utilizada por SuiteCRM, de forma similar a lo que podemos hacer con pgAdmin para las bases de datos PostgreSQL. Existen aplicaciones que permiten acceder a ambos tipos de sistemas de gestión de bases de datos (SGBD), pero por motivos didácticos hemos preferido incluir en esta infraestructura una aplicación especializada para cada SGBD.

A diferencia de lo que ocurre con pgAdmin, aquí la conexión con el servidor ya está configurada automáticamente, por lo que únicamente tendrás que iniciar sesión con alguno de los siguientes usuarios:

* **Servidor:** `db_suitecrm` *(configurado por defecto)*
* **Usuario:** `suitecrm_user`
* **Contraseña:** `suitecrm_pass`

> También puedes acceder con el usuario administrador de MariaDB:
> * **Usuario:** `root`
> * **Contraseña:** `root_pass`

---

<span id="config-ollama"></span>
### H. Ollama (IA - LLM)

Con Ollama podremos descargar y ejecutar modelos de lenguaje (LLM) de código abierto que nos permitirán incorporar funcionalidades de inteligencia artificial a nuestra infraestructura. Podremos interactuar con estos modelos mediante un chat o utilizar sus capacidades desde otras aplicaciones a través de su API, y utilizaremos Ollama como motor de IA local, evitando depender de servicios externos.

* **Descargar un modelo:** `docker compose exec ollama ollama pull llama3.2:3b`
    > Puedes sustituir `llama3.2:3b` por cualquier otro modelo compatible.

* **Ver los modelos instalados:** `docker compose exec ollama ollama list`
    > También puedes consultar la API de Ollama para obtener un listado en formato JSON: [http://localhost:11434/api/tags](http://localhost:11434/api/tags)

* **Ejecutar un modelo:** `docker compose exec ollama ollama run llama3.2:3b`
    > Una vez iniciado podrás conversar con el modelo desde la terminal. Escribe `/?` para ver los comandos disponibles durante la conversación.


Para saber qué modelos hay disponibles consulta la web [https://ollama.com/library](https://ollama.com/library). Algunos modelos son:

| Modelo | Tamaño | Memoria RAM recomendada | Uso recomendado |
|---------|:------:|:-----------------------:|-----------------|
| `llama3.2:1b` | 1B | 2-3 GB | Equipos con pocos recursos o pruebas rápidas. |
| `llama3.2:3b` ⭐ | 3B | 4-6 GB | **Modelo recomendado.** |
| `gemma3:4b` | 4B | 6-8 GB | Muy buen equilibrio entre calidad y velocidad. |
| `qwen3:4b` | 4B | 6-8 GB | Excelente para programación y razonamiento. |
| `qwen3:8b` | 8B | 10-12 GB | Mayor calidad si el equipo dispone de suficiente memoria. |
| `deepseek-r1:8b` | 8B | 10-12 GB | Especialmente orientado a tareas de razonamiento complejo. |

---

<span id="config-fastapi"></span>
### I. FastAPI (API personalizada)

FastAPI es un framework para Python que nos permitirá crear nuestra propia API REST. A partir del fichero `main.py` podremos definir nuevos endpoints o ampliar los existentes para que puedan ser consumidos por otras aplicaciones o servicios de nuestra infraestructura.

Actualmente la API incluye los siguientes endpoints accesibles desde la URL de base [http://localhost:8000/](http://localhost:8000/):

| Método | Endpoint | Descripción |
|---------|----------|-------------|
| GET | `/` | Comprueba que la API está funcionando correctamente. Devuelve el JSON `{"mensaje": "API de integración SIE"}`. |
| GET | `/health` | Endpoint de monitorización que devuelve el estado de la API. Devuelve el JSON `{"status": "ok"}`. |
| GET | `/servicios` | Muestra las direcciones configuradas de los principales servicios de la infraestructura. Muestra un JSON con las direcciones configuradas para los distintos servicios de la infraestructura. |
| GET | `/docs` | Documentación interactiva generada automáticamente mediante Swagger UI. |
| GET | `/redoc` | Documentación interactiva generada automáticamente mediante ReDoc. |
| GET | `/openapi.json` | Especificación OpenAPI de la API en formato JSON. |

> Cada vez que añadas nuevos endpoints al fichero `main.py`, la documentación se actualizará automáticamente.


<span id="network"></span>
## 🌐 Red interna Docker

Todos los servicios definidos en este proyecto pertenecen a una misma red privada de Docker denominada `sie-network`. Esto permite que los contenedores puedan comunicarse entre sí utilizando directamente el nombre del servicio definido en `docker-compose.yml`. No es necesario conocer la dirección IP de cada contenedor, ya que Docker proporciona un servidor DNS interno que resuelve automáticamente estos nombres.

* **Inspeccionar la red:** `docker network inspect sie-network` (para visualizar la configuración de la red y los contenedores conectados a ella)

* **Tipos de redes en Docker:** Docker ofrece diferentes controladores (*drivers*) de red que se resumen en la siguiente tabla.

| Driver | Uso principal |
|---------|---------------|
| `bridge` | Red privada dentro del mismo equipo (la utilizada en este proyecto). |
| `host` | El contenedor comparte directamente la red del sistema anfitrión. |
| `none` | El contenedor no dispone de conectividad de red. |
| `overlay` | Comunicación entre contenedores distribuidos en varios equipos (Docker Swarm). |
| `macvlan` | El contenedor obtiene una dirección IP propia dentro de la red física. |

Usamos el driver **bridge**, ya que es el más sencillo y adecuado para un entorno de desarrollo local.


<span id="alternativas"></span>
## 🖥️ Alternativas (Instalación Local)
Si por limitaciones de hardware o problemas de otra índole tu equipo no permite ejecutar Docker, hay otras opciones para instalar y ejecutar estas mismas herramientas por separado:

* Odoo: Visita la web oficial y descarga el instalador nativo o usa la versión cloud con restricciones en [https://www.odoo.com/es/page/download](https://www.odoo.com/es/page/download).
* SuiteCRM: Descarga los archivos desde la web oficial de SuiteCRM [https://suitecrm.com/download](https://suitecrm.com/download). Requiere un servidor con PHP y MySQL, recomendamos [XAMPP](https://www.apachefriends.org/es/download.html), y ajustar la configuración de PHP siguiendo las [recomendaciones](https://docs.suitecrm.com/8.x/admin/installation-guide/downloading-installing/). 
* n8n: Usa la versión community de la herramienta siguiendo las indicaciones de la documentación oficial [https://docs.n8n.io/choose-n8n](https://docs.n8n.io/choose-n8n).
* Bonita Runtime: Puedes descargarla desde la misma URL desde la que se descarga Bonita Studio ([https://www.bonitasoft.com/es/old-versions](https://www.bonitasoft.com/es/old-versions)), y recuerda que ambas deben ser de la misma versión. Si no pudiese llevarse a cabo la instalación de Bonita Runtime, Bonita Studio incluye un servidor local para pruebas rápidas que te permitirá validar los procesos que se diseñen.
* smtp4dev: En el repositorio oficial en GitHub podemos encontrar ficheros de instalación para diferentes sistemas operativos [https://github.com/rnwood/smtp4dev/releases](https://github.com/rnwood/smtp4dev/releases).
* pgAdmin: Podemos descargarla desde [https://www.pgadmin.org](https://www.pgadmin.org)
* phpMyAdmin: Incluida en [XAMPP](https://www.apachefriends.org/es/download.html). También podemos descargarla desde [https://www.phpmyadmin.net/downloads/](https://www.phpmyadmin.net/downloads/).
* Ollama: Disponible para distintos sistemas operativos en [https://ollama.com/download](https://ollama.com/download).
* FastAPI: Se necesita un interprete de Python (descargable desde [https://www.python.org/downloads/](https://www.python.org/downloads/)) para poder ejecutar el script con la definición de la API.


<span id="comandos-docker"></span>
## 🐳 Comandos útiles de Docker

A continuación se muestran algunos de los comandos que podemos utilizar para gestionar la infraestructura:

* **Arrancar todos los servicios:** `docker compose up -d`
* **Reconstruir las imágenes y arrancar los servicios:** `docker compose up -d --build`
* **Reconstruir una imagen desde cero:** `docker compose build --no-cache <servicio>`
* **Arrancar un servicio:** `docker compose up -d <servicio>`
* **Detener todos los servicios:** `docker compose down`
* **Reiniciar un servicio:** `docker compose restart <servicio>`
* **Ver el estado de los contenedores:** `docker compose ps`
* **Ver los registros (logs) de todos los servicios:** `docker compose logs`
* **Ver los registros (logs) de un único servicio:** `docker compose logs <servicio>`
* **Seguir los registros en tiempo real:** `docker compose logs -f <servicio>`
* **Ejecutar un comando dentro de un contenedor:** `docker compose exec <servicio> <comando>`
    > *Ejemplos:*
    > * `docker compose exec ollama ollama list`
    > * `docker compose exec ollama ollama pull llama3.2:3b`
    > * `docker compose exec ollama ollama run llama3.2:3b`
* **Abrir una terminal dentro de un contenedor:** `docker compose exec <servicio> sh`
* **Ver las redes Docker:** `docker network ls`
* **Inspeccionar la red utilizada por la infraestructura:** `docker network inspect sie-network`
* **Ver los volúmenes Docker:** `docker volume ls`
* **Eliminar contenedores, redes y volúmenes:** `docker compose down -v`
    > **¡Atención!** Este comando elimina también los datos persistentes almacenados en los volúmenes Docker.


<span id="faq"></span>
## ❓ FAQ y Resolución de Problemas
* **¿Debo aceptar la licencia que me aparece al instalar Docker Desktop?** 
    * Sí, durante el proceso de instalación aparecerá un mensaje sobre los términos de servicio (Docker Subscription Service Agreement) y debéis aceptarlo para poder continuar aunque no es necesario crear una cuenta o iniciar sesión para usar la herramienta. Docker Desktop es gratuito para uso educativo y no es necesario realizar ningún pago ni introducir datos bancarios.
* **¿Qué versión de Docker Desktop debo descargar?**
    * Windows: La mayoría de los ordenadores utilizan la opción AMD64 (procesadores Intel o AMD estándar). Solo elige ARM64 si tienes un dispositivo con procesador basado en arquitectura ARM (como nuevos modelos con chips Snapdragon o series SQ). 
        * Durante la instalación, asegúrate de activar WSL 2. Si la instalación de WSL falla, abre PowerShell como administrador, ejecuta `wsl --install` y reinicia el sistema.
    * macOS: Apple Silicon (ARM64) para modelos con chips M1, M2, M3 o posteriores. Intel Chip (AMD64) para modelos de Mac anteriores a 2020.
    * Linux: Sigue las instrucciones de la web oficial según tu distribución.
* **¿Qué hago si me da un error tipo "port is already allocated"?** 
    * Significa que otra aplicación de tu equipo ya está usando ese puerto. Solución: Abre `docker-compose.yml`, busca el servicio afectado y cambia el primer número del puerto (ej. de 8080:80 a 8082:80). Guarda y ejecuta de nuevo `docker compose up -d --build`.
* **¿Se borra mi trabajo si cierro Docker Desktop o apago el equipo?** 
    * No. Los datos persisten en los volúmenes definidos en el `docker-compose.yml`, tanto los internos de Docker como los ligados a las carpetas locales de tu proyecto.
* **¿Cómo detengo los servicios?** 
    * Ejecuta `docker compose stop` en la carpeta del proyecto (aunque no es estrictamente necesario para apagar tu equipo). 
    * También puedes ejecutar `docker compose down` pero ten cuidado y no lo uses con el parámetro `-v` (o `--volumes`) o se borrarán todos los datos guardados hasta la fecha.
* **¿Problemas con la virtualización?** 
    * Si Docker no arranca, verifica en la BIOS que la "Virtualización" (VT-x o AMD-V) esté habilitada.
    * Docker Desktop recomienda un mínimo de 4GB de RAM.
* **¿Cómo empiezo de cero con un servicio instalado eliminando todos los datos creados hasta la fecha?**
    1. Páralo todo con `docker compose down` desde la carpeta del proyecto.
    2. Saca el listado de volúmenes con `docker volume ls`.
    3. Elimina los relacionados con ese servicio con `docker volume rm <VOLUMEN_A_ELIMINAR>`.
    4. Vuelve a lanzar los servicios con `docker compose up -d`.
* **¿Puedo eliminar un servicio por completo?**
    * Sí, por ejemplo, porque hayamos modificado la configuración y necesitemos construirlo desde cero. 
    * Puedes hacerlo con `docker rm -f <servicio>` (Vuelve a lanzarlo con `docker compose up -d --build`).
    * Si lo que quieres es empezar de cero con todo lo que hay en el *compose* ejecuta `docker compose down -v --rmi all --remove-orphans` y termina con `docker system prune -a --volumes`.
* **¿Por qué tenemos dos servicios de PostgreSQL?** 
    * En esta infraestructura tenemos uno para Odoo y otro para Bonita Runtime. De esta forma, si tuviéramos que eliminar uno o diera cualquier problema no perderíamos los datos del otro.
* **¿Cómo accedo a un fichero que está dentro de un contenedor?**
    * Ejecuta por ejemplo `cat` para ver el contenido con `docker exec -it <servicio> cat /ruta/al/archivo.txt`
    * Copia el fichero a tu sistema `Host` con `docker cp <servicio>:/ruta/en/contenedor/archivo.txt /ruta/en/host/archivo.txt` 
* **¿Puedo abrir un terminal dentro de un contenedor?**
    * Sí, por ejemplo para instalar modulos adicionales en el intérprete de Python de Odoo (por ejemplo, porque al activar un módulo nos haya salido un error porque falta una dependencia). 
    * Abre un terminal ejecutando `docker exec -it sie_odoo bash`, instala el módulo con `pip` y comprueba si funciona. Por ejemplo, para instalar Pandas ejecutaríamos `pip3 install pandas` y luego `python3 -c "import pandas; print(pandas.__version__)"` para ver si se muestra la versión de Pandas instalada.
    * Para volver al terminal del *Host* ejecuta `exit`, y reiniciamos el servicio si es necesario. Por ejemplo, en el caso de instalar un módulo Python para Odoo será necesario reiniciarlo con `docker restart sie_odoo`.
