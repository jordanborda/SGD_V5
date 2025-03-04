=============================================================
Manual de instalacion de Docker PAYARA
=============================================================

Versión 1.0
-------------

HISTORIAL DE VERSIONES
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
1. INTRODUCCIÓN
-------------------------------------------------------------------------------

Tradicionalmente, la instalación de **Payara Server** se lleva a cabo en servidores físicos
o virtuales, creando dominios y nodos independientes. Sin embargo, en muchos entornos
modernos el uso de **contenedores Docker** simplifica la configuración y administración.

En este manual, se detalla cómo **construir** y **ejecutar** Payara Server dentro de un solo
contenedor Docker, de manera que toda la operación de instalación y configuración suceda
de forma aislada y **reproducible**.

-------------------------------------------------------------------------------
2. OBJETIVOS Y ALCANCE
-------------------------------------------------------------------------------

2.1. Objetivos
--------------

- Proveer instrucciones para realizar una instalación de **Payara Server** dentro de un contenedor Docker, evitando la necesidad de configurar manualmente múltiples servidores.
- Facilitar el despliegue y la prueba de aplicaciones **Java EE** o **Jakarta EE** con Payara en un entorno Docker.

2.2. Alcance
------------

- Este documento sirve como guía de referencia para la construcción de una **imagen Docker** de Payara (usando Java 8 o Java 11).
- Incluye la configuración básica para iniciar el servidor y acceder a la **consola de administración** (DAS).

-------------------------------------------------------------------------------
3. GLOSARIO
-------------------------------------------------------------------------------

- **Docker**: Plataforma que automatiza la distribución de aplicaciones dentro de contenedores.
- **Imagen Docker**: Plantilla de solo lectura que contiene un stack de software para crear contenedores.
- **Contenedor Docker**: Instancia de una imagen Docker que se ejecuta de forma aislada.
- **Payara Server**: Servidor de aplicaciones compatible con Jakarta EE (antes Java EE), derivado de GlassFish.
- **DAS (Domain Administration Server)**: Servidor de administración de dominios de Payara, provee la consola y los comandos asadmin.
- **Dominio**: Estructura de configuración en Payara que agrupa recursos, instancias y clústeres.

-------------------------------------------------------------------------------
4. INSTALACIÓN DE SERVIDOR DE APLICACIONES PAYARA EN DOCKER
-------------------------------------------------------------------------------

.. note::
   En lugar de instalar Payara en varios servidores, utilizaremos **un único contenedor Docker**
   que incluye:
   
   - Sistema base (por ejemplo, Rocky Linux 9).
   - **Java** (Zulu 8 o Zulu 11, según se requiera).
   - **Payara Server** (versión 5.2022.4 como ejemplo).
   - Configuración de domain y secure-admin.

   Se asume que Docker ya está instalado en tu entorno.

4.1. Estructura de archivos recomendada
---------------------------------------

Crea un directorio de trabajo, por ejemplo ``payara-docker``, donde ubicarás:

.. code-block:: none

   payara-docker/
    ├─ Dockerfile
    ├─ scripts/      (opcional, para almacenar scripts .sh)
    └─ (otros archivos requeridos)


4.2. Ejemplo de Dockerfile (con Java 8)
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

4.3. Construcción de la imagen Docker
-------------------------------------

Para crear la imagen:

.. code-block:: bash

   docker build -t payara-docker:v1 .

Al terminar, tendrás una imagen local llamada ``payara-docker:v1``.

4.4. Ejecución del contenedor
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

4.5. Configuración con Java 11 (opcional)
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

4.6. Almacenamiento y persistencia
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

4.7. Personalización adicional (clusters, NFS, etc.)
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
5. NOTAS FINALES
-------------------------------------------------------------------------------

.. important::
   - Este ejemplo usa **Rocky Linux** como base, pero podrías iniciar con otras imágenes
     (Alpine, Ubuntu, Debian) o inclusive con la imagen oficial de Payara
     (``payara/server-full``).
   - Asegura los puertos de administración (``11048``, ``4848``) si vas a exponerlos
     en producción.
   - Para entornos de **desarrollo**, un solo contenedor Payara es suficiente.
   - El archivo Dockerfile se puede mejorar con **scripts** que ejecuten comandos
     asadmin adicionales (por ejemplo, para crear JDBC, JMS, etc.).

.. admonition:: Fin del Manual
   :class: hint

   Este manual te permite construir y arrancar rápidamente **Payara Server** en Docker,
   simplificando la puesta en marcha de aplicaciones Java EE / Jakarta EE en un
   entorno **contenedorizado**. ¡Feliz despliegue!
