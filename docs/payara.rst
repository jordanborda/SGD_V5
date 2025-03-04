=============================================================
Manual de instalacion de servidor local-virtual PAYARA
=============================================================

Historial de versiones
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

---------------------
INTRODUCCIÓN
---------------------

Cuando se desarrolla una aplicación en **Payara Server**, es muy común desplegarla
directamente en la instancia local del **Servidor de Administración de Dominios (DAS)**,
pues es la forma más sencilla y directa de probar rápidamente las aplicaciones en desarrollo.

Al llevar una aplicación a producción, sin embargo, es muy probable que se utilice un
**dominio** con varias instancias independientes o en **clúster**, que residan en múltiples
servidores remotos.

-------------------------------------------------------------------------------
OBJETIVOS Y ALCANCE
-------------------------------------------------------------------------------

Objetivos
--------------

- Brindar las instrucciones para realizar una correcta instalación del servidor de aplicaciones **Payara**.

Alcance
------------

- Este documento sirve como guía de referencia para la instalación del servidor de aplicaciones Payara en un entorno **Linux (Rocky Linux 9)**, utilizando **Java 8** y **Java 11**.

-------------------------------------------------------------------------------
GLOSARIO
-------------------------------------------------------------------------------

- **Servidor**: Aplicación que contiene los recursos protegidos mediante API REST.  
- **Cliente**: Aplicación que realiza las peticiones a un servidor para interactuar con los recursos protegidos.  
- **Autenticación**: Proceso a través del cual un cliente garantiza su identidad (por ejemplo, con usuario y contraseña).  
- **Autorización**: Proceso a través del cual se determina si un cliente tiene la autoridad para acceder a ciertos recursos protegidos.  
- **Sistema Operativo**: Conjunto de programas que administra los recursos de una computadora.  
- **Servidor de aplicaciones**: Servidor en una red de computadoras que ejecuta aplicaciones y que proporciona servicios de aplicación a clientes.

-------------------------------------------------------------------------------
INSTALACIÓN DE SERVIDOR DE APLICACIONES PAYARA
-------------------------------------------------------------------------------

.. important::
   Se asume que **Rocky Linux 9** ya está configurado correctamente en cada servidor.
   Sin ese paso previo, **no** se garantiza el correcto funcionamiento de los pasos siguientes.

A continuación, se describen los servidores involucrados:

::

   192.168.49.97   srv-balanceador-sgd-prod   srv-balanceador-sgd-prod.onpe.gob.pe
   192.168.49.98   srv-app1-sgd-prod          srv-app1-sgd-prod.onpe.gob.pe
   192.168.49.102  srv-app2-sgd-prod          srv-app2-sgd-prod.onpe.gob.pe
   192.168.49.103  srv-app3-sgd-prod          srv-app3-sgd-prod.onpe.gob.pe
   192.168.49.110  srv-app4-sgd-prod          srv-app4-sgd-prod.onpe.gob.pe
   192.168.49.111  srv-app5-sgd-prod          srv-app5-sgd-prod.onpe.gob.pe

.. note::
   El IP ``192.168.49.97`` (con **NGINX**) funcionará también como **DAS** (Domain Administration Server)
   de Payara. Será el **administrador de los clústeres**.

Preparación del entorno en Rocky Linux 9
---------------------------------------------

Estas configuraciones aplican tanto para el **servidor DAS** como para los **nodos**.

**Instalar fuentes e idioma (ubicación** ``/usr/share/fonts``**):**

.. code-block:: bash

   wget https://rpmfind.net/linux/fedora/linux/releases/37/Everything/x86_64/os/Packages/x/xorg-x11-font-utils-7.5-54.fc37.x86_64.rpm
   wget https://downloads.sourceforge.net/project/mscorefonts2/rpms/msttcore-fonts-installer-2.6-1.noarch.rpm

   sudo dnf localinstall xorg-x11-font-utils-7.5-54.fc37.x86_64.rpm -y
   sudo dnf install cabextract fontconfig nfs-utils -y
   sudo dnf localinstall msttcore-fonts-installer-2.6-1.noarch.rpm -y

**Configurar nombre de dominio** en ``/etc/idmapd.conf``:

.. code-block:: bash

   sudo sed -i '/^#Domain/s/^#//;/Domain = /s/=.*/= onpe.gob.pe/' /etc/idmapd.conf
   # Verificar la configuración:
   sudo nano /etc/idmapd.conf

**Activar el servicio NFS**:

.. code-block:: bash

   sudo systemctl enable --now nfs-server rpcbind

Instalación y configuración de Java 8
------------------------------------------

.. important::
   Se instalará **Java 8 (ZULU)** en el **DAS** y en cada **nodo**.

Servidores donde se instalará **Java 8**:

- DAS: ``192.168.49.97``
- Nodos: ``192.168.49.98``, ``192.168.49.102``, ``192.168.49.103``, ``192.168.49.110``, ``192.168.49.111``

**Crear el usuario para Payara Java 8** (con privilegios ``sudo``):

.. code-block:: bash

   sudo groupadd payara
   sudo useradd -c "Payara Producción Java 8" -d /opt/payara_prod1 -g payara -m -s /bin/bash payara_prod1
   sudo passwd payara_prod1  # Asignar contraseña, por ejemplo: Apayara5$

**Ingresar** con el nuevo usuario:

.. code-block:: bash

   su - payara_prod1

**Instalar Java 8** (ZULU):

.. code-block:: bash

   wget https://cdn.azul.com/zulu/bin/zulu8.68.0.19-ca-jdk8.0.362-linux_x64.zip
   unzip zulu8.68.0.19-ca-jdk8.0.362-linux_x64.zip
   mv zulu8.68.0.19-ca-jdk8.0.362-linux_x64 .zulu8

.. tip::
   Mantener el JDK en un directorio oculto (``.zulu8``) ayuda a tener múltiples versiones de Java en un mismo servidor.

**Configurar variables de entorno** en ``~/.bash_profile`` y ``~/.bashrc``:

Agregar lo siguiente (en ambos archivos):

.. code-block:: bash

   export JAVA_HOME=$HOME/.zulu8
   export PATH=${JAVA_HOME}/bin:$PATH

Luego, **verificar la versión**:

.. code-block:: bash

   exit
   su - payara_prod1
   java -version

**Generar clave SSH** (opcional, pero recomendado):

.. code-block:: bash

   ssh-keygen -t rsa -b 4096

Configuración del servidor DAS (Java 8)
-------------------------------------------

.. important::
   **IP del DAS**: ``192.168.49.97``.

Asegúrese de haber instalado Java 8 y creado el usuario ``payara_prod1`` en **todos los nodos**.

**Ingresar** con el usuario ``payara_prod1`` en el DAS:

.. code-block:: bash

   ssh payara_prod1@192.168.49.97

**Descargar Payara** (ejemplo: versión 5.2022.4):

.. code-block:: bash

   wget https://nexus.payara.fish/repository/payara-community/fish/payara/distributions/payara/5.2022.4/payara-5.2022.4.zip
   unzip payara-5.2022.4.zip
   cd payara5/bin

**Eliminar dominios creados** por defecto (si existen):

.. code-block:: bash

   ./asadmin delete-domain domain_prod1
   ./asadmin delete-domain domain1

**Crear un nuevo dominio** (ej.: ``domain_prod1``) con base en Java 8:

.. code-block:: bash

   ./asadmin create-domain --portbase 11000 \
       --template ../glassfish/common/templates/gf/appserver-domain.jar \
       domain_prod1

**Iniciar el dominio** recién creado:

.. code-block:: bash

   ./asadmin start-domain domain_prod1

**Definir la contraseña** de administración:

.. code-block:: bash

   echo "AS_ADMIN_PASSWORD=Apayara5" > /opt/payara_prod1/payara5/pserver

**Habilitar el acceso seguro** a la consola de administración (SSL):

.. code-block:: bash

   ./asadmin --port 11048 --user admin \
       --passwordfile /opt/payara_prod1/payara5/pserver \
       enable-secure-admin

**Reiniciar el dominio**:

.. code-block:: bash

   ./asadmin restart-domain domain_prod1

**Configurar llaves SSH** en cada nodo (se pedirá la contraseña de ``payara_prod1``):

.. code-block:: bash

   ./asadmin setup-ssh --sshuser payara_prod1 srv-app1-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod1 srv-app2-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod1 srv-app3-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod1 srv-app4-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod1 srv-app5-sgd-prod.onpe.gob.pe

**Instalar Payara en los nodos** de forma remota:

.. code-block:: bash

   ./asadmin install-node --sshuser payara_prod1 srv-app1-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod1 srv-app2-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod1 srv-app3-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod1 srv-app4-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod1 srv-app5-sgd-prod.onpe.gob.pe

**Crear los nodos** en el DAS:

.. code-block:: bash

   ./asadmin --passwordfile /opt/payara_prod1/payara5/pserver \
       --port 11048 create-node-ssh \
       --nodehost srv-app1-sgd-prod.onpe.gob.pe \
       --sshuser payara_prod1 node-app1

   ./asadmin --passwordfile /opt/payara_prod1/payara5/pserver \
       --port 11048 create-node-ssh \
       --nodehost srv-app2-sgd-prod.onpe.gob.pe \
       --sshuser payara_prod1 node-app2

   ./asadmin --passwordfile /opt/payara_prod1/payara5/pserver \
       --port 11048 create-node-ssh \
       --nodehost srv-app3-sgd-prod.onpe.gob.pe \
       --sshuser payara_prod1 node-app3

   ./asadmin --passwordfile /opt/payara_prod1/payara5/pserver \
       --port 11048 create-node-ssh \
       --nodehost srv-app4-sgd-prod.onpe.gob.pe \
       --sshuser payara_prod1 node-app4

   ./asadmin --passwordfile /opt/payara_prod1/payara5/pserver \
       --port 11048 create-node-ssh \
       --nodehost srv-app5-sgd-prod.onpe.gob.pe \
       --sshuser payara_prod1 node-app5

.. tip::
   Para simplificar el uso de ``asadmin``, se puede crear un **alias** en ``~/.bashrc``:

   .. code-block:: bash

      cd ~
      nano .bashrc

   Agregar:

   .. code-block:: bash

      alias asadmin='$HOME/payara5/bin/asadmin --port 11048 --user admin --passwordfile $HOME/payara5/pserver'

Creación de un NFS Server para compartir archivos (Java 8)
---------------------------------------------------------------

Realizar estos pasos en el DAS (``192.168.49.97``) con usuario **sudo**.

**Crear directorios** y asignar permisos:

.. code-block:: bash

   sudo mkdir -p /var/nfs/prod1/sgd_repo
   sudo chmod -R 777 /var/nfs/prod1/
   sudo chown -R nobody:nobody /var/nfs/prod1/

**Configurar** ``/etc/exports``:

.. code-block:: bash

   sudo nano /etc/exports

Agregar (o ajustar):

.. code-block:: none

   /var/nfs/prod1  192.168.49.0/24(rw,sync,no_subtree_check)

**Exportar** y reiniciar **NFS**:

.. code-block:: bash

   sudo exportfs -a
   sudo systemctl restart nfs-server

.. warning::
   Exponer los recursos NFS en un rango amplio puede suponer un riesgo de seguridad.
   Ajustar según las políticas de la organización.

**Habilitar el puerto 11048** en el firewall:

.. code-block:: bash

   sudo firewall-cmd --permanent --add-port=11048/tcp
   sudo firewall-cmd --reload

.. caution::
   En entornos de producción, **NO** se recomienda exponer abiertamente el puerto de administración.

**Crear enlace simbólico** al NFS con usuario ``payara_prod1``:

.. code-block:: bash

   su - payara_prod1
   ln -s /var/nfs/prod1/sgd_repo/ /opt/payara_prod1/sgd_repo

**Configuración en los servidores nodo** (Java 8)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

En cada nodo (``192.168.49.98, .102, .103, .110, .111``) con usuario **sudo**:

.. code-block:: bash

   # Verificar que el DAS comparte NFS
   sudo showmount -e 192.168.49.97

   # Crear el punto de montaje e iniciar el montaje
   sudo mkdir /mnt/nfs_prod1
   sudo mount -t nfs 192.168.49.97:/var/nfs/prod1 /mnt/nfs_prod1

   # Editar /etc/fstab para montaje automático
   sudo nano /etc/fstab

Agregar la línea:

.. code-block:: none

   192.168.49.97:/var/nfs/prod1  /mnt/nfs_prod1  nfs  defaults  0 0

Luego, como usuario ``payara_prod1`` en cada nodo:

.. code-block:: bash

   su - payara_prod1
   unlink sgd_repo   # Si existía previamente
   ln -s /mnt/nfs_prod1/sgd_repo/ /opt/payara_prod1/sgd_repo
   ls -l

Con esto, los nodos comparten el repositorio ``/var/nfs/prod1/sgd_repo`` vía NFS.

Instalación y configuración de Java 11
-------------------------------------------

El proceso es muy **similar** al de **Java 8**, pero con otro usuario (ej.: ``payara_prod2``) y otro dominio (``domain_prod2``).

Preparar Java 11 en cada servidor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Se repiten los pasos en:

- DAS: ``192.168.49.97``
- Nodos: ``192.168.49.98``, ``192.168.49.102``, ``192.168.49.103``, ``192.168.49.110``, ``192.168.49.111``

**Crear usuario y grupo**:

.. code-block:: bash

   sudo groupadd payara  # (Si no existe)
   sudo useradd -c "Payara Producción Java 11" -d /opt/payara_prod2 -g payara -m -s /bin/bash payara_prod2
   sudo passwd payara_prod2  # Ejemplo: Apayara5$

**Instalar Java 11 (ZULU)** con ``payara_prod2``:

.. code-block:: bash

   su - payara_prod2
   wget https://cdn.azul.com/zulu/bin/zulu11.62.17-ca-jdk11.0.18-linux_x64.zip
   unzip zulu11.62.17-ca-jdk11.0.18-linux_x64.zip
   mv zulu11.62.17-ca-jdk11.0.18-linux_x64 .zulu11

**Configurar variables de entorno** (``~/.bash_profile`` y ``~/.bashrc``):

.. code-block:: bash

   export JAVA_HOME=$HOME/.zulu11
   export PATH=${JAVA_HOME}/bin:$PATH

**Verificar**:

.. code-block:: bash

   exit
   su - payara_prod2
   java -version

**Generar claves SSH** (opcional):

.. code-block:: bash

   ssh-keygen -t rsa -b 4096

Configuración del DAS con Java 11
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Ingresar** con el usuario ``payara_prod2`` en el DAS (``192.168.49.97``):

.. code-block:: bash

   ssh payara_prod2@192.168.49.97

**Descargar Payara** (ej. 5.2022.4):

.. code-block:: bash

   wget https://nexus.payara.fish/repository/payara-community/fish/payara/distributions/payara/5.2022.4/payara-5.2022.4.zip
   unzip payara-5.2022.4.zip
   cd payara5/bin

**Eliminar dominios** previos:

.. code-block:: bash

   ./asadmin delete-domain domain_prod2
   ./asadmin delete-domain domain1

**Crear el dominio** ``domain_prod2`` (Java 11):

.. code-block:: bash

   ./asadmin create-domain --portbase 12000 \
       --template ../glassfish/common/templates/gf/appserver-domain.jar \
       domain_prod2

**Iniciar** el dominio:

.. code-block:: bash

   ./asadmin start-domain domain_prod2

**Configurar contraseña** de administración:

.. code-block:: bash

   echo "AS_ADMIN_PASSWORD=Apayara5" > /opt/payara_prod2/payara5/pserver
   ./asadmin --port 12048 --user admin --passwordfile /opt/payara_prod2/payara5/pserver enable-secure-admin

**Reiniciar** el dominio:

.. code-block:: bash

   ./asadmin restart-domain domain_prod2

**Configurar llaves SSH** (con ``payara_prod2``) para cada nodo:

.. code-block:: bash

   ./asadmin setup-ssh --sshuser payara_prod2 srv-app1-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod2 srv-app2-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod2 srv-app3-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod2 srv-app4-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod2 srv-app5-sgd-prod.onpe.gob.pe

**Instalar Payara** en los nodos:

.. code-block:: bash

   ./asadmin install-node --sshuser payara_prod2 srv-app1-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod2 srv-app2-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod2 srv-app3-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod2 srv-app4-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod2 srv-app5-sgd-prod.onpe.gob.pe

**Crear los nodos** en el DAS (Java 11):

.. code-block:: bash

   ./asadmin --passwordfile /opt/payara_prod2/payara5/pserver \
     --port 12048 create-node-ssh \
     --nodehost srv-app1-sgd-prod.onpe.gob.pe \
     --sshuser payara_prod2 node-app1

   ./asadmin --passwordfile /opt/payara_prod2/payara5/pserver \
     --port 12048 create-node-ssh \
     --nodehost srv-app2-sgd-prod.onpe.gob.pe \
     --sshuser payara_prod2 node-app2

   ./asadmin --passwordfile /opt/payara_prod2/payara5/pserver \
     --port 12048 create-node-ssh \
     --nodehost srv-app3-sgd-prod.onpe.gob.pe \
     --sshuser payara_prod2 node-app3

   ./asadmin --passwordfile /opt/payara_prod2/payara5/pserver \
     --port 12048 create-node-ssh \
     --nodehost srv-app4-sgd-prod.onpe.gob.pe \
     --sshuser payara_prod2 node-app4

   ./asadmin --passwordfile /opt/payara_prod2/payara5/pserver \
     --port 12048 create-node-ssh \
     --nodehost srv-app5-sgd-prod.onpe.gob.pe \
     --sshuser payara_prod2 node-app5

.. tip::
   Al igual que con Java 8, se puede configurar un alias para ``asadmin`` en
   ``~/.bashrc`` para **simplificar** los comandos.

Creación de un NFS Server para Java 11
------------------------------------------

En el DAS (``192.168.49.97``), con usuario **sudo**:

**Crear directorios** y permisos:

.. code-block:: bash

   sudo mkdir -p /var/nfs/prod2/sgd_repo
   sudo chmod -R 777 /var/nfs/prod2/
   sudo chown -R nobody:nobody /var/nfs/prod2/

**Editar** ``/etc/exports``:

.. code-block:: bash

   sudo nano /etc/exports

Agregar:

.. code-block:: none

   /var/nfs/prod2  192.168.49.0/24(rw,sync,no_subtree_check)

**Exportar** y reiniciar:

.. code-block:: bash

   sudo exportfs -a
   sudo systemctl restart nfs-server

**Habilitar el puerto 12048** en el firewall:

.. code-block:: bash

   sudo firewall-cmd --permanent --add-port=12048/tcp
   sudo firewall-cmd --reload

**Crear enlace simbólico** con usuario ``payara_prod2``:

.. code-block:: bash

   su - payara_prod2
   ln -s /var/nfs/prod2/sgd_repo/ /opt/payara_prod2/sgd_repo

**Configuración en los nodos** (Java 11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Verificar el NFS
   sudo showmount -e 192.168.49.97

   # Crear punto de montaje
   sudo mkdir /mnt/nfs_prod2
   sudo mount -t nfs 192.168.49.97:/var/nfs/prod2 /mnt/nfs_prod2

   # Editar /etc/fstab
   sudo nano /etc/fstab

Agregar la línea:

.. code-block:: none

   192.168.49.97:/var/nfs/prod2  /mnt/nfs_prod2  nfs  defaults  0 0

Luego, desde ``payara_prod2``:

.. code-block:: bash

   su - payara_prod2
   unlink sgd_repo  # si ya existía
   ln -s /mnt/nfs_prod2/sgd_repo/ /opt/payara_prod2/sgd_repo
   ls -l

Con esto se completa la configuración de Payara con **Java 8** y **Java 11**, compartiendo
directorios vía **NFS** para despliegues y administración remota.

-------------------------------------------------------------------------------
NOTAS FINALES
-------------------------------------------------------------------------------

.. important::
   - En un entorno real de producción, **reforzar la seguridad** de los puertos de administración
     (``11048``, ``12048``), limitando su acceso a direcciones confiables o VPN.
   - Verificar regularmente el correcto montaje NFS en todos los nodos para evitar
     problemas de disponibilidad en el despliegue de aplicaciones.
   - Ajustar los nombres de dominio y las direcciones IP de acuerdo con la
     infraestructura real.
   - Se recomienda **automatizar** la instalación con scripts o herramientas de
     orquestación (Ansible, Puppet, etc.) si se maneja un gran número de servidores.


-------------------------------------------------------------------------------
Continuacion de Configuracion del servidor Payara
-------------------------------------------------------------------------------

Configuración del DAS JAVA 8
-----------------------------

1. **Verificar el estado del servidor Payara (Server DAS)**:

.. code-block:: bash

   ssh payara_prod1@192.168.49.97
   cd payara5/bin/
   ./asadmin start-domain domain_prod1

::

   Acceder a la consola de administración:
   https://192.168.49.97:11048 (Usuario: admin, Contraseña: Apayara5)

   Configurar Data Grid:

   Menú **Domain** -> **Data Grid**

   Configuración:

      Data Grid Group Name: GridSGD1prod
      Data Grid Discovery Mode: domain

   Presionar botón SAVE.

2. **Copiar librerías JDBC y scripts para JAVA 8**:

.. list-table::
   :header-rows: 1
   :widths: 25 20 20 35

   * - Archivo Origen
     - Servidor Destino
     - Usuario Servidor
     - Ruta Destino
   * - ojdbc8-12.2.0.1.jar
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/payara5/glassfish/domains/domain_prod1/lib
   * - postgresql-42.5.0.jar
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/payara5/glassfish/domains/domain_prod1/lib
   * - instance.sh
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/
   * - deploy-sgd_prod.sh
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/
   * - deploy-wsiotramite.sh
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/
   * - deploy-notisgd.sh
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/
   * - deploy-ssev.sh
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/
   * - crea_instancia_sgd_prod.sh
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/scripts/
   * - crea_instancia_ws_iotramite.sh
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/scripts/
   * - crea_instancia_notifica.sh
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/scripts/
   * - crea_instancia_ssev.sh
     - 192.168.49.97
     - payara_prod1
     - /payara_prod1/scripts/

3. **Crear directorios**:

.. code-block:: bash

   ssh payara_prod1@192.168.49.97
   mkdir /opt/payara_prod1/scripts/
   mkdir /opt/payara_prod1/war-files/
   mkdir /opt/payara_prod1/sgd_repo/tmp

::


4. **Cambiar permisos de ejecución a scripts y reiniciar DOMAIN**:

.. code-block:: bash

   ssh payara_prod1@192.168.49.97
   chmod 700 *.sh
   cd payara5/bin/
   ./asadmin restart-domain domain_prod1

::


5. **Crear Instancias Java 8**:

.. code-block:: bash

   ssh payara_prod1@192.168.49.97
   cd scripts/
   chmod 700 *.sh
   ./crea_instancia_sgd_prod.sh
   ./crea_instancia_ws_iotramite.sh
   ./crea_instancia_notifica.sh
   ./crea_instancia_ssev.sh

::


6. **Instalar certificados CA (LDAP)**:

.. code-block:: bash

   ssh payara_prod1@192.168.49.97
   keytool -import -trustcacerts -keystore .zulu8/jre/lib/security/cacerts \
       -storepass changeit -alias onpe-CA -file onpe-ca.cer

::


.. note::
   (Copiar ``onpe-ca.cer`` previamente al servidor)

7. **Reiniciar y listar instancias Java 8**:

.. code-block:: bash

   ssh payara_prod1@192.168.49.97
   cd
   ./instance.sh restart sgd_prod-instance1 && ./instance.sh restart sgd_prod-instance2 && ./instance.sh restart sgd_prod-instance3
   ./instance.sh restart ws_iotramite-instance1 && ./instance.sh restart ws_iotramite-instance2
   ./instance.sh list

::



Configuración del DAS JAVA 11
-----------------------------

1. **Verificar el estado del servidor Payara (Server Balanceador NGINX)**:

.. code-block:: bash

   ssh payara_prod2@192.168.49.97
   cd payara5/bin/
   ./asadmin start-domain domain_prod2

::


   Acceder a la consola de administración:
   https://192.168.49.97:12048 (Usuario: admin, Contraseña: Apayara5)

   Configurar Data Grid:

   Menú **Domain** -> **Data Grid**

   Configuración:

      Data Grid Group Name: GridSGD2prod
      Data Grid Discovery Mode: domain

   Presionar botón SAVE.

2. **Copiar librerías JDBC y scripts para JAVA 11**:

.. list-table::
   :header-rows: 1
   :widths: 25 20 20 35

   * - Archivo Origen
     - Servidor Destino
     - Usuario Servidor
     - Ruta Destino
   * - ojdbc8-12.2.0.1.jar
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/payara5/glassfish/domains/domain_prod2/lib
   * - postgresql-42.5.0.jar
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/payara5/glassfish/domains/domain_prod2/lib
   * - instance.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - deploy-elastic-api.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - deploy-repo.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - deploy-repo_migra.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - deploy-storage_pri.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - deploy-storage_his.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - deploy-apisgdv2.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - deploy-tokensecurity.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - deploy-verifica_sgd.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - deploy-visor_pdf.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - deploy-ws_verifica.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/
   * - crea_instancia_repo.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/scripts/
   * - crea_instancia_storage_pri.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/scripts/
   * - crea_instancia_storage_his.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/scripts/
   * - crea_instancia_token_security.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/scripts/
   * - crea_instancia_apisgd.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/scripts/
   * - crea_instancia_elastic.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/scripts/
   * - crea_instancia_repo_migra.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/scripts/
   * - crea_instancia_verifica.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/scripts/
   * - crea_instancia_visorpdf.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/scripts/
   * - crea_instancia_backend.sh
     - 192.168.49.97
     - payara_prod2
     - /payara_prod2/scripts/

3. **Crear directorios**:

.. code-block:: bash

   ssh payara_prod2@192.168.49.97
   mkdir /opt/payara_prod2/scripts/
   mkdir /opt/payara_prod2/war-files/
   mkdir /opt/payara_prod2/sgd_repo/tmp

::


4. **Cambiar permisos de ejecución a scripts y reiniciar DOMAIN**:

.. code-block:: bash

   ssh payara_prod2@192.168.49.97
   chmod 700 *.sh
   cd payara5/bin/
   ./asadmin restart-domain domain_prod2

::


5. **Crear Instancias Java 11**:

.. code-block:: bash

   ssh payara_prod2@192.168.49.97
   cd scripts/
   chmod 700 *.sh
   ./crea_instancia_repo.sh
   ./crea_instancia_storage_pri.sh
   ./crea_instancia_storage_his.sh
   ./crea_instancia_token_security.sh
   ./crea_instancia_apisgd.sh
   ./crea_instancia_elastic.sh
   ./crea_instancia_repo_migra.sh
   ./crea_instancia_verifica.sh
   ./crea_instancia_visorpdf.sh
   ./crea_instancia_backend.sh

::


6. **Instalar certificados CA (LDAP)**:

.. code-block:: bash

   ssh payara_prod2@192.168.49.97
   keytool -import -trustcacerts -keystore .zulu11/jre/lib/security/cacerts \
       -storepass changeit -alias onpe-CA -file onpe-ca.cer

::


.. note::
   (Copiar ``onpe-ca.cer`` previamente al servidor)

7. **Reiniciar y listar instancias Java 11**:

.. code-block:: bash

   ssh payara_prod2@192.168.49.97
   cd
   ./instance.sh restart ws_backend-instance1 && ./instance.sh restart ws_backend-instance2
   ./instance.sh restart ws_apisgd-instance1 && ./instance.sh restart ws_apisgd-instance2
   ./instance.sh restart api_elastic-instance1 && ./instance.sh restart api_elastic-instance2
   ./instance.sh restart repo_doc-instance1 && ./instance.sh restart repo_doc-instance2 && ./instance.sh restart repo_doc-instance3
   ./instance.sh restart storage_pri-instance1 && ./instance.sh restart storage_pri-instance2
   ./instance.sh restart storage_his-instance1 && ./instance.sh restart storage_his-instance2
   ./instance.sh restart token_security-instance1 && ./instance.sh restart token_security-instance2
   ./instance.sh restart verifica-instance1 && ./instance.sh restart verifica-instance2
   ./instance.sh restart visorpdf-instance1 && ./instance.sh restart visorpdf-instance2
   ./instance.sh restart repo_migra-instance1
   ./instance.sh list

::

