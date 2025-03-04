=============================================================
Manual de instalacion de Docker PAYARA
=============================================================

Historial de Versiones
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 20 10 40 30

   * - FECHA DE APROBACIÓN
     - VERSIÓN
     - DESCRIPCIÓN
     - ELABORADO POR
   * - 04/03/2025
     - 1.0
     - Elaboración del Documento: Manual de Instalación de Servidor de Aplicaciones Payara
     - Jordan Piero Borda Colque

-------------------------------------------------------------------------------
INTRODUCCIÓN
-------------------------------------------------------------------------------

Tradicionalmente, la instalación de **Payara Server** se lleva a cabo en servidores físicos
o virtuales, creando dominios y nodos independientes. Sin embargo, en muchos entornos
modernos el uso de **contenedores Docker** simplifica la configuración y administración.

En este manual, se detalla cómo **construir** y **ejecutar** Payara Server dentro de un solo
contenedor Docker, de manera que toda la operación de instalación y configuración suceda
de forma aislada y **reproducible**.

-------------------------------------------------------------------------------
OBJETIVOS Y ALCANCE
-------------------------------------------------------------------------------

Objetivos
--------------

- Proveer instrucciones para realizar una instalación de **Payara Server** dentro de un contenedor Docker, evitando la necesidad de configurar manualmente múltiples servidores.
- Facilitar el despliegue y la prueba de aplicaciones **Java EE** o **Jakarta EE** con Payara en un entorno Docker.

Alcance
------------

- Este documento sirve como guía de referencia para la construcción de una **imagen Docker** de Payara (usando Java 8 o Java 11).
- Incluye la configuración básica para iniciar el servidor y acceder a la **consola de administración** (DAS).

-------------------------------------------------------------------------------
GLOSARIO
-------------------------------------------------------------------------------

- **Docker**: Plataforma que automatiza la distribución de aplicaciones dentro de contenedores.
- **Imagen Docker**: Plantilla de solo lectura que contiene un stack de software para crear contenedores.
- **Contenedor Docker**: Instancia de una imagen Docker que se ejecuta de forma aislada.
- **Payara Server**: Servidor de aplicaciones compatible con Jakarta EE (antes Java EE), derivado de GlassFish.
- **DAS (Domain Administration Server)**: Servidor de administración de dominios de Payara, provee la consola y los comandos asadmin.
- **Dominio**: Estructura de configuración en Payara que agrupa recursos, instancias y clústeres.

-------------------------------------------------------------------------------
INSTALACIÓN DE SERVIDOR DE APLICACIONES PAYARA EN DOCKER
-------------------------------------------------------------------------------

.. note::
   En lugar de instalar Payara en varios servidores, utilizaremos **un único contenedor Docker**
   que incluye:
   
   - Sistema base (por ejemplo, Rocky Linux 9).
   - **Java** (Zulu 8 o Zulu 11, según se requiera).
   - **Payara Server** (versión 5.2022.4 como ejemplo).
   - Configuración de domain y secure-admin.

   Se asume que Docker ya está instalado en tu entorno.

Estructura de archivos recomendada
---------------------------------------

Crea un directorio de trabajo, por ejemplo ``payara-docker``, donde ubicarás:

.. code-block:: none

   payara-docker/
    ├─ Dockerfile
    ├─ scripts/      (opcional, para almacenar scripts .sh)
    └─ (otros archivos requeridos)


Ejemplo de Dockerfile (con Java 8)
---------------------------------------

.. important::
   El siguiente Dockerfile descarga e instala Payara 5.2022.4 con **Zulu 8 (Java 8)**.
   Ajusta las **versiones** y **enlaces** según sea necesario.

.. code-block:: docker

   # -------------------------------------------------------------
   # DOCKERFILE EJEMPLO PARA PAYARA + JAVA 8
   # -------------------------------------------------------------
   FROM rockylinux:9 AS base

   # Variables de entorno (puedes ajustarlas a conveniencia)
   ENV JAVA_VERSION=8.68.0.19-ca-jdk8.0.362 \
       PAYARA_VERSION=5.2022.4 \
       PAYARA_DOMAIN_NAME=domain_prod1 \
       PAYARA_PWD=Apayara5 \
       PORT_BASE=11000 \
       ADMIN_USER=admin

   # Instalar utilidades necesarias
   RUN dnf update -y && \
       dnf install -y curl unzip wget fontconfig cabextract && \
       dnf clean all

   # Crear usuario payara dentro del contenedor (opcional)
   RUN groupadd payara && \
       useradd -m -g payara -s /bin/bash payara_prod1

   USER payara_prod1
   WORKDIR /home/payara_prod1

   # Instalar Zulu JDK 8
   RUN wget https://cdn.azul.com/zulu/bin/zulu${JAVA_VERSION}-linux_x64.zip && \
       unzip zulu${JAVA_VERSION}-linux_x64.zip && \
       mv zulu${JAVA_VERSION}-linux_x64 .zulu8 && \
       rm zulu${JAVA_VERSION}-linux_x64.zip

   # Ajustar variables de entorno Java
   ENV JAVA_HOME=/home/payara_prod1/.zulu8
   ENV PATH=$JAVA_HOME/bin:$PATH

   # Descargar y descomprimir Payara
   RUN wget https://nexus.payara.fish/repository/payara-community/fish/payara/distributions/payara/${PAYARA_VERSION}/payara-${PAYARA_VERSION}.zip && \
       unzip payara-${PAYARA_VERSION}.zip && \
       rm payara-${PAYARA_VERSION}.zip

   # Crear un dominio nuevo
   WORKDIR /home/payara_prod1/payara5/bin
   RUN ./asadmin delete-domain domain1 || true

   # Creamos el dominio con puertos base (11000, 11048, etc.)
   RUN ./asadmin create-domain --portbase ${PORT_BASE} \
       --template ../glassfish/common/templates/gf/appserver-domain.jar \
       ${PAYARA_DOMAIN_NAME}

   # Configuración de la contraseña de admin
   RUN echo "AS_ADMIN_PASSWORD=${PAYARA_PWD}" > /home/payara_prod1/payara5/pserver && \
       echo "AS_ADMIN_NEWPASSWORD=${PAYARA_PWD}" >> /home/payara_prod1/payara5/pserver

   # Habilitar el Secure Admin
   RUN ./asadmin start-domain ${PAYARA_DOMAIN_NAME} && \
       ./asadmin --port $((PORT_BASE+48)) --user ${ADMIN_USER} \
           --passwordfile /home/payara_prod1/payara5/pserver enable-secure-admin && \
       ./asadmin restart-domain ${PAYARA_DOMAIN_NAME}

   # Exponer puertos relevantes (ajusta según tu necesidad)
   EXPOSE 11080  # HTTP
   EXPOSE 11048  # Admin (HTTPS/secure admin)

   # Comando de arranque: inicia el dominio y mantiene el contenedor corriendo
   CMD ["./asadmin", "start-domain", "-v", "domain_prod1"]

.. tip::
   - **Puertos**:
     - 11080 para acceder por HTTP a las aplicaciones.
     - 11048 para la consola de administración Payara (HTTPS/secure).

   - **Usuario** de administración: admin  
   - **Contraseña**: Apayara5 (definida en la variable ``PAYARA_PWD``).

Construcción de la imagen Docker
-------------------------------------

Para crear la imagen:

.. code-block:: bash

   docker build -t payara-docker:v1 .

Al terminar, tendrás una imagen local llamada ``payara-docker:v1``.

Ejecución del contenedor
-----------------------------

Para arrancar **Payara** y acceder a la consola de administración y/o tus aplicaciones:

.. code-block:: bash

   docker run -d --name payara-docker \
     -p 11080:11080 \
     -p 11048:11048 \
     payara-docker:v1

.. note::
   - Payara estará accesible en ``http://localhost:11080`` (o la IP de tu host).  
   - La **consola de administración** (DAS) en ``https://localhost:11048``.  
   - El usuario de administración es ``admin``.  
   - La contraseña (según el Dockerfile) es ``Apayara5``.

   Dado que se habilitó secure-admin, la consola usa **HTTPS**. Posiblemente veas una
   advertencia de certificado autofirmado.

Configuración con Java 11 (opcional)
-----------------------------------------

Si deseas utilizar **Java 11** en lugar de Java 8, basta con **modificar** el Dockerfile:

.. code-block:: none

   ENV JAVA_VERSION=11.62.17-ca-jdk11.0.18
   ...
   RUN wget https://cdn.azul.com/zulu/bin/zulu${JAVA_VERSION}-linux_x64.zip && \
       unzip zulu${JAVA_VERSION}-linux_x64.zip && \
       mv zulu${JAVA_VERSION}-linux_x64 .zulu11 && \
       rm zulu${JAVA_VERSION}-linux_x64.zip

   ENV JAVA_HOME=/home/payara_prod1/.zulu11
   ENV PATH=$JAVA_HOME/bin:$PATH

Asimismo, podrías querer cambiar el **puerto base** (por ejemplo, 12000) y el nombre de dominio
(``domain_prod2``) para que no colisione con tu contenedor anterior.

Almacenamiento y persistencia
----------------------------------

.. caution::
   En el Dockerfile anterior, todo reside dentro del contenedor (``/home/payara_prod1``).
   Si eliminas el contenedor, pierdes los datos.

Para **persistir** la configuración, logs o despliegues entre reinicios, monta un volumen:

.. code-block:: bash

   docker run -d --name payara-docker \
     -p 11080:11080 \
     -p 11048:11048 \
     -v /ruta/local/volumen-dominio:/home/payara_prod1/payara5/glassfish/domains/domain_prod1 \
     payara-docker:v1

Con esto, si el contenedor se borra, la carpeta local ``/ruta/local/volumen-dominio`` mantendrá
el contenido del **dominio Payara**.

Personalización adicional (clusters, NFS, etc.)
----------------------------------------------------

Este ejemplo describe un **único contenedor** con un **único dominio Payara**. Sin embargo,
Payara admite configuraciones de **clúster** y **múltiples nodos**. Para simularlo con Docker:

- Crear varios contenedores.
- Configurar SSH y red Docker para que el DAS pueda conectarse a los nodos Payara.
- Usar volúmenes compartidos para las claves.

.. tip::
   - Para **entornos reales** con alta disponibilidad, se recomiendan orquestadores
     como **Docker Swarm** o **Kubernetes**.
   - Puedes combinar Payara con Docker Compose o Helm Charts para configurar
     clusters de forma más robusta.


-------------------------------------------------------------------------------
Continuación de la Configuración del Servidor Payara (Docker)
-------------------------------------------------------------------------------

Introducción
------------

En este apartado, vamos a **replicar** los pasos de configuración (creación de instancias,
copiado de librerías JDBC, etc.) que antes se hacían en servidores físicos/virtuales con
Payara, pero ahora **dentro** de nuestro **contenedor Docker** llamado ``payara-docker``.

.. important::
   - Asumimos que ya tienes **un contenedor** corriendo con la imagen ``payara-docker:v1``:
     ::
     
       docker run -d --name payara-docker \
         -p 11080:11080 \
         -p 11048:11048 \
         payara-docker:v1
         
   - El dominio se llama ``domain_prod1`` (creado en el Dockerfile) y el usuario
     es ``payara_prod1`` (home en ``/home/payara_prod1``).
   - La contraseña de administración es ``Apayara5``.

Configuración del DAS (Java 8) en Docker
----------------------------------------

1. **Verificar el estado del servidor Payara dentro del contenedor**:

.. code-block:: bash

   # Listar contenedores en ejecución
   docker ps

   # Entrar al contenedor 'payara-docker'
   docker exec -it payara-docker /bin/bash

   # Ya dentro del contenedor:
   cd payara5/bin/
   ./asadmin start-domain domain_prod1

::

   - Acceder a la **consola de administración** desde tu **host**:
     
     https://localhost:11048  
     (Usuario: admin, Contraseña: Apayara5)

   - **Configurar Data Grid**:
     
     Menú **Domain** -> **Data Grid**

     Ajustar:
     
       Data Grid Group Name: GridSGD1prod  
       Data Grid Discovery Mode: domain  

     Presionar **SAVE**.

   - Salir si deseas:
     ```
     exit
     ```

2. **Copiar librerías JDBC y scripts (Java 8) al contenedor**:

   Suponiendo que en tu **host** tienes archivos como `ojdbc8-12.2.0.1.jar`, `postgresql-42.5.0.jar`,
   `instance.sh`, etc. Para copiarlos **al contenedor** en las rutas correspondientes,
   utiliza `docker cp`. Por ejemplo:

.. list-table::
   :header-rows: 1
   :widths: 25 20 20 35

   * - Archivo Origen (Host)
     - Contenedor (Destino)
     - Ruta en contenedor
     - Comando de ejemplo
   * - ojdbc8-12.2.0.1.jar
     - payara-docker
     - /payara_prod1/payara5/glassfish/domains/domain_prod1/lib
     - ``docker cp ojdbc8-12.2.0.1.jar payara-docker:/payara_prod1/payara5/glassfish/domains/domain_prod1/lib``
   * - postgresql-42.5.0.jar
     - payara-docker
     - /payara_prod1/payara5/glassfish/domains/domain_prod1/lib
     - ``docker cp postgresql-42.5.0.jar payara-docker:/payara_prod1/payara5/glassfish/domains/domain_prod1/lib``
   * - instance.sh
     - payara-docker
     - /payara_prod1/
     - ``docker cp instance.sh payara-docker:/payara_prod1/``
   * - deploy-sgd_prod.sh
     - payara-docker
     - /payara_prod1/
     - ``docker cp deploy-sgd_prod.sh payara-docker:/payara_prod1/``
   * - ... (resto de scripts)
     - payara-docker
     - /payara_prod1/
     - ``docker cp <script> payara-docker:/payara_prod1/``

   .. note::
      Si lo prefieres, podrías **incorporar** estos archivos directamente en el **Dockerfile**
      para no tener que copiarlos manualmente cada vez.

3. **Crear directorios** dentro del contenedor:

.. code-block:: bash

   docker exec -it payara-docker /bin/bash
   mkdir -p /opt/payara_prod1/scripts/
   mkdir -p /opt/payara_prod1/war-files/
   mkdir -p /opt/payara_prod1/sgd_repo/tmp
   exit

::

4. **Cambiar permisos de ejecución a scripts y reiniciar el dominio**:

.. code-block:: bash

   docker exec -it payara-docker /bin/bash
   cd /payara_prod1
   chmod 700 *.sh
   cd /home/payara_prod1/payara5/bin
   ./asadmin restart-domain domain_prod1
   exit

::

5. **Crear Instancias Java 8**:

.. code-block:: bash

   docker exec -it payara-docker /bin/bash
   cd /opt/payara_prod1/scripts/
   chmod 700 *.sh
   ./crea_instancia_sgd_prod.sh
   ./crea_instancia_ws_iotramite.sh
   ./crea_instancia_notifica.sh
   ./crea_instancia_ssev.sh
   exit

::

6. **Instalar certificados CA (LDAP)**:

.. code-block:: bash

   # Copiamos el certificado onpe-ca.cer desde el host al contenedor
   docker cp onpe-ca.cer payara-docker:/opt/payara_prod1/

   # Entramos al contenedor y usamos keytool
   docker exec -it payara-docker /bin/bash
   cd /opt/payara_prod1
   keytool -import -trustcacerts -keystore .zulu8/jre/lib/security/cacerts \
       -storepass changeit -alias onpe-CA -file onpe-ca.cer
   exit

::

.. note::
   (Asegúrate de tener ``onpe-ca.cer`` en tu **host** antes de usar `docker cp`.)

7. **Reiniciar y listar instancias Java 8**:

.. code-block:: bash

   docker exec -it payara-docker /bin/bash
   cd /opt/payara_prod1
   ./instance.sh restart sgd_prod-instance1 && ./instance.sh restart sgd_prod-instance2 && ./instance.sh restart sgd_prod-instance3
   ./instance.sh restart ws_iotramite-instance1 && ./instance.sh restart ws_iotramite-instance2
   ./instance.sh list
   exit

::

---

Configuración del DAS (Java 11) en Docker (Opcional)
----------------------------------------------------

Para usar **Java 11**, tendrías dos opciones:

1. **Crear otra imagen** (por ejemplo, `payara-docker-java11:v1`) con el Dockerfile adaptado
   a `ENV JAVA_VERSION=11.xxxx ...`, `ENV PAYARA_DOMAIN_NAME=domain_prod2`, etc.
2. Modificar la misma imagen y exponer puertos distintos (como `12080` y `12048`) para
   evitar conflictos.

Suponiendo que ya levantaste un contenedor llamado ``payara-docker-java11`` con su dominio
``domain_prod2`` y el usuario ``payara_prod2``, el proceso es análogo:

.. code-block:: bash

   # Copiar archivos
   docker cp ojdbc8-12.2.0.1.jar payara-docker-java11:/payara_prod2/payara5/...
   # Entrar al contenedor
   docker exec -it payara-docker-java11 /bin/bash
   cd payara5/bin
   ./asadmin start-domain domain_prod2
   # etc.

   # Al finalizar
   exit

El resto de pasos (cambiar permisos, reiniciar dominio, instalar certificados CA, etc.)
son exactamente los mismos, **ajustando** las rutas (``/payara_prod2`` en vez de
``/payara_prod1``) y el **nombre** del dominio (`domain_prod2`).

---

.. tip::
   - Para entornos de desarrollo, un solo contenedor Payara (Java 8 o Java 11)
     pued

