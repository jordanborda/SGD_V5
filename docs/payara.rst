=============================================================
MANUAL DE INSTALACIÓN DE SERVIDOR DE APLICACIONES PAYARA
=============================================================

Versión 1.0
===========

HISTORIAL DE VERSIONES
======================

.. list-table::
   :header-rows: 1
   :widths: 20 10 40 30

   * - FECHA DE APROBACIÓN
     - VERSIÓN
     - DESCRIPCIÓN
     - ELABORADO POR
   * - 12/02/2024
     - 1.0
     - Elaboración del Documento: Manual de Instalación de Servidor de Aplicaciones Payara
     - Jordan Piero Borda Colque

ÍNDICE
======

1. INTRODUCCIÓN  
2. OBJETIVOS Y ALCANCE  
   2.1. Objetivos  
   2.2. Alcance  
3. GLOSARIO  
4. INSTALACIÓN DE SERVIDOR DE APLICACIONES PAYARA  
   4.1. Preparación del entorno en Rocky Linux 9  
   4.2. Instalación y configuración de Java 8  
   4.3. Configuración del servidor DAS (Java 8)  
   4.4. Creación de un NFS Server para compartir archivos entre los nodos (Java 8)  
   4.5. Instalación y configuración de Java 11  
       4.5.1. Preparar Java 11 en cada servidor  
       4.5.2. Configuración del DAS con Java 11  
   4.6. Creación de un NFS Server para Java 11  
5. NOTAS FINALES  

.. contents::
   :local:
   :depth: 2

----------------------------------------------------------------
1. INTRODUCCIÓN
----------------------------------------------------------------

Cuando se desarrolla una aplicación en Payara Server, es muy común desplegarla
directamente en la instancia local del Servidor de Administración de Dominios (DAS),
pues es la forma más sencilla y directa de probar rápidamente las aplicaciones en desarrollo.

Al llevar una aplicación a producción, sin embargo, es muy probable que se utilice un
dominio con varias instancias independientes o en clúster, que residan en múltiples
servidores remotos.

----------------------------------------------------------------
2. OBJETIVOS Y ALCANCE
----------------------------------------------------------------

2.1. Objetivos
--------------

   - Brindar las instrucciones para realizar una correcta instalación del servidor de aplicaciones Payara.

2.2. Alcance
------------

   - Este documento sirve como guía de referencia para la instalación del servidor de aplicaciones Payara en un entorno Linux (Rocky Linux 9), utilizando Java 8 y Java 11.

----------------------------------------------------------------
3. GLOSARIO
----------------------------------------------------------------

   - **Servidor**: Aplicación que contiene los recursos protegidos mediante API REST.  
   - **Cliente**: Aplicación que realiza las peticiones a un servidor para interactuar con los recursos protegidos.  
   - **Autenticación**: Proceso a través del cual un cliente garantiza su identidad (por ejemplo, con usuario y contraseña).  
   - **Autorización**: Proceso a través del cual se determina si un cliente tiene la autoridad para acceder a ciertos recursos protegidos.  
   - **Sistema Operativo**: Conjunto de programas que administra los recursos de una computadora.  
   - **Servidor de aplicaciones**: Servidor en una red de computadoras que ejecuta aplicaciones y que proporciona servicios de aplicación a clientes.

----------------------------------------------------------------
4. INSTALACIÓN DE SERVIDOR DE APLICACIONES PAYARA
----------------------------------------------------------------

**Nota previa**: Se asume que ya se encuentra configurado Rocky Linux 9 en cada servidor, según el procedimiento correspondiente. Sin ese paso, no se garantiza la correcta configuración posterior.

A continuación se describen los servidores involucrados:

::

   192.168.49.97   srv-balanceador-sgd-prod   srv-balanceador-sgd-prod.onpe.gob.pe
   192.168.49.98   srv-app1-sgd-prod          srv-app1-sgd-prod.onpe.gob.pe
   192.168.49.102  srv-app2-sgd-prod          srv-app2-sgd-prod.onpe.gob.pe
   192.168.49.103  srv-app3-sgd-prod          srv-app3-sgd-prod.onpe.gob.pe
   192.168.49.110  srv-app4-sgd-prod          srv-app4-sgd-prod.onpe.gob.pe
   192.168.49.111  srv-app5-sgd-prod          srv-app5-sgd-prod.onpe.gob.pe

**Importante**: El IP ``192.168.49.97`` (que tiene configurado NGINX) se configurará también como servidor DAS (Domain Administration Server) de Payara, cumpliendo la función de administrador de los clústeres.

4.1. Preparación del entorno en Rocky Linux 9
---------------------------------------------

Estas configuraciones aplican tanto para el servidor DAS como para los nodos.

Instalar fuentes e idioma (ubicación ``/usr/share/fonts``)::

   wget https://rpmfind.net/linux/fedora/linux/releases/37/Everything/x86_64/os/Packages/x/xorg-x11-font-utils-7.5-54.fc37.x86_64.rpm
   wget https://downloads.sourceforge.net/project/mscorefonts2/rpms/msttcore-fonts-installer-2.6-1.noarch.rpm

   sudo dnf localinstall xorg-x11-font-utils-7.5-54.fc37.x86_64.rpm -y
   sudo dnf install cabextract fontconfig nfs-utils -y
   sudo dnf localinstall msttcore-fonts-installer-2.6-1.noarch.rpm -y

Configurar nombre de dominio en ``/etc/idmapd.conf``::

   sudo sed -i '/^#Domain/s/^#//;/Domain = /s/=.*/= onpe.gob.pe/' /etc/idmapd.conf
   # Verificar la configuración:
   sudo nano /etc/idmapd.conf

Activar el servicio NFS::

   sudo systemctl enable --now nfs-server rpcbind

4.2. Instalación y configuración de Java 8
------------------------------------------

Esta instalación se realiza en todos los servidores:

- DAS: ``192.168.49.97``
- Nodos: ``192.168.49.98, 192.168.49.102, 192.168.49.103, 192.168.49.110, 192.168.49.111``

Ingresar con usuario privilegiado (sudo) y crear el usuario para Payara Java 8::

   sudo groupadd payara
   sudo useradd -c "Payara Producción Java 8" -d /opt/payara_prod1 -g payara -m -s /bin/bash payara_prod1
   sudo passwd payara_prod1  # Asignar contraseña, por ejemplo: Apayara5$

Ingresar con el nuevo usuario::

   su - payara_prod1

Instalar Java 8 (ZULU)::

   wget https://cdn.azul.com/zulu/bin/zulu8.68.0.19-ca-jdk8.0.362-linux_x64.zip
   unzip zulu8.68.0.19-ca-jdk8.0.362-linux_x64.zip
   mv zulu8.68.0.19-ca-jdk8.0.362-linux_x64 .zulu8

Configurar variables de entorno en ``~/.bash_profile``::

   nano ~/.bash_profile

Añadir:

::

   export JAVA_HOME=$HOME/.zulu8
   export PATH=${JAVA_HOME}/bin:$PATH

Configurar variables de entorno en ``~/.bashrc``::

   nano ~/.bashrc

Añadir:

::

   export JAVA_HOME=$HOME/.zulu8
   export PATH=${JAVA_HOME}/bin:$PATH

Salir y volver a ingresar con el usuario ``payara_prod1`` para verificar la versión::

   exit
   su - payara_prod1
   java -version

Generar clave SSH (opcional, pero recomendado para la administración remota entre nodos)::

   ssh-keygen -t rsa -b 4096

(Presionar ENTER en todos los pasos, salvo que se desee cifrar la clave con contraseña.)

4.3. Configuración del servidor DAS (Java 8)
-------------------------------------------

IP del DAS: ``192.168.49.97``

**Nota**: Antes de continuar, asegúrese de haber repetido los pasos de instalación de Java 8 y la creación del usuario ``payara_prod1`` en todos los nodos.

Ingresar con el usuario ``payara_prod1`` en el servidor DAS::

   ssh payara_prod1@192.168.49.97

Descargar Payara (versión 5.2022.4, como ejemplo)::

   wget https://nexus.payara.fish/repository/payara-community/fish/payara/distributions/payara/5.2022.4/payara-5.2022.4.zip
   unzip payara-5.2022.4.zip
   cd payara5/bin

Eliminar los dominios creados por defecto, si existieran::

   ./asadmin delete-domain domain_prod1
   ./asadmin delete-domain domain1

Crear un nuevo dominio (por ejemplo, ``domain_prod1``) con base en Java 8::

   ./asadmin create-domain --portbase 11000 \
       --template ../glassfish/common/templates/gf/appserver-domain.jar \
       domain_prod1

Iniciar el dominio recién creado::

   ./asadmin start-domain domain_prod1

Definir la contraseña de administración para Payara::

::

   echo "AS_ADMIN_PASSWORD=Apayara5" > /opt/payara_prod1/payara5/pserver

Habilitar el acceso seguro a la consola de administración::

   ./asadmin --port 11048 --user admin \
       --passwordfile /opt/payara_prod1/payara5/pserver \
       enable-secure-admin

Reiniciar el dominio::

   ./asadmin restart-domain domain_prod1

Configurar las llaves SSH para acceder a cada nodo (se solicitará la contraseña del usuario ``payara_prod1``)::

   ./asadmin setup-ssh --sshuser payara_prod1 srv-app1-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod1 srv-app2-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod1 srv-app3-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod1 srv-app4-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod1 srv-app5-sgd-prod.onpe.gob.pe

Instalar Payara en los nodos de manera remota::

   ./asadmin install-node --sshuser payara_prod1 srv-app1-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod1 srv-app2-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod1 srv-app3-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod1 srv-app4-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod1 srv-app5-sgd-prod.onpe.gob.pe

Crear cada uno de los nodos Payara en el DAS::

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

(Opcional) Crear un alias para ``asadmin`` en el archivo ``~/.bashrc`` del usuario ``payara_prod1``::

   cd ~
   nano .bashrc

Agregar:

::

   alias asadmin='$HOME/payara5/bin/asadmin --port 11048 --user admin --passwordfile $HOME/payara5/pserver'

4.4. Creación de un NFS Server para compartir archivos entre los nodos (Java 8)
-------------------------------------------------------------------------------

Esta operación se realiza en el DAS (``192.168.49.97``) con usuario sudo.

Crear directorios y asignar permisos::

   sudo mkdir -p /var/nfs/prod1/sgd_repo
   sudo chmod -R 777 /var/nfs/prod1/
   sudo chown -R nobody:nobody /var/nfs/prod1/

Editar ``/etc/exports`` para configurar el rango de direcciones IP con acceso::

   sudo nano /etc/exports

Agregar (o modificar según sea necesario)::

   /var/nfs/prod1  192.168.49.0/24(rw,sync,no_subtree_check)

Exportar y reiniciar NFS::

   sudo exportfs -a
   sudo systemctl restart nfs-server

Habilitar el puerto ``11048`` en el firewall (para la consola web de Payara):  
(En producción no se recomienda exponer este puerto abiertamente.)::

   sudo firewall-cmd --permanent --add-port=11048/tcp
   sudo firewall-cmd --reload

Con el usuario ``payara_prod1``, crear un enlace simbólico al NFS::

::

   su - payara_prod1
   ln -s /var/nfs/prod1/sgd_repo/ /opt/payara_prod1/sgd_repo

Configuración en los servidores nodo (Java 8)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

En cada nodo (``192.168.49.98, 192.168.49.102, 192.168.49.103, 192.168.49.110, 192.168.49.111``) con usuario sudo:

Verificar que el DAS comparte NFS::

   sudo showmount -e 192.168.49.97

Crear el punto de montaje e iniciar el montaje::

   sudo mkdir /mnt/nfs_prod1
   sudo mount -t nfs 192.168.49.97:/var/nfs/prod1 /mnt/nfs_prod1

Editar ``/etc/fstab`` para montar automáticamente al reiniciar::

   sudo nano /etc/fstab

Agregar línea::

   192.168.49.97:/var/nfs/prod1  /mnt/nfs_prod1  nfs  defaults  0 0

Desde el usuario ``payara_prod1`` en cada nodo, crear (o actualizar) el enlace simbólico::

::

   su - payara_prod1
   unlink sgd_repo   # Solo si existía un enlace previo.
   ln -s /mnt/nfs_prod1/sgd_repo/ /opt/payara_prod1/sgd_repo
   ls -l

Con esto, los nodos comparten el mismo repositorio (``/var/nfs/prod1/sgd_repo``) vía NFS.

4.5. Instalación y configuración de Java 11
-------------------------------------------

El proceso es muy similar al de Java 8, pero utilizando otro usuario (por ejemplo, ``payara_prod2``) y otro dominio (``domain_prod2``).

4.5.1. Preparar Java 11 en cada servidor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Se repiten los pasos en:

- DAS: ``192.168.49.97``
- Nodos: ``192.168.49.98, 192.168.49.102, 192.168.49.103, 192.168.49.110, 192.168.49.111``

Crear el usuario y grupo::

   sudo groupadd payara  # (Si no existe ya)
   sudo useradd -c "Payara Producción Java 11" -d /opt/payara_prod2 -g payara -m -s /bin/bash payara_prod2
   sudo passwd payara_prod2  # Ejemplo: Apayara5$

Instalar Java 11 (ZULU) con el usuario ``payara_prod2``::

   su - payara_prod2
   wget https://cdn.azul.com/zulu/bin/zulu11.62.17-ca-jdk11.0.18-linux_x64.zip
   unzip zulu11.62.17-ca-jdk11.0.18-linux_x64.zip
   mv zulu11.62.17-ca-jdk11.0.18-linux_x64 .zulu11

Configurar variables de entorno (``~/.bash_profile`` y ``~/.bashrc``)::

   nano ~/.bash_profile

Agregar:

::

   export JAVA_HOME=$HOME/.zulu11
   export PATH=${JAVA_HOME}/bin:$PATH

Repetir en ``~/.bashrc``::

   nano ~/.bashrc

::

   export JAVA_HOME=$HOME/.zulu11
   export PATH=${JAVA_HOME}/bin:$PATH

Verificar::

   exit
   su - payara_prod2
   java -version

Generar claves SSH si se desea (igual que en Java 8)::

   ssh-keygen -t rsa -b 4096

4.5.2. Configuración del DAS con Java 11
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ingresar con el usuario ``payara_prod2`` en el DAS (``192.168.49.97``)::

   ssh payara_prod2@192.168.49.97

Descargar Payara::

   wget https://nexus.payara.fish/repository/payara-community/fish/payara/distributions/payara/5.2022.4/payara-5.2022.4.zip
   unzip payara-5.2022.4.zip
   cd payara5/bin

Eliminar posibles dominios previos::

   ./asadmin delete-domain domain_prod2
   ./asadmin delete-domain domain1

Crear el dominio ``domain_prod2`` con base en Java 11::

   ./asadmin create-domain --portbase 12000 \
       --template ../glassfish/common/templates/gf/appserver-domain.jar \
       domain_prod2

Iniciar el dominio::

   ./asadmin start-domain domain_prod2

Configurar la contraseña de administración::

::

   echo "AS_ADMIN_PASSWORD=Apayara5" > /opt/payara_prod2/payara5/pserver
   ./asadmin --port 12048 --user admin --passwordfile /opt/payara_prod2/payara5/pserver enable-secure-admin

Reiniciar el dominio::

   ./asadmin restart-domain domain_prod2

Configurar llaves SSH para cada nodo (con ``payara_prod2``)::

   ./asadmin setup-ssh --sshuser payara_prod2 srv-app1-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod2 srv-app2-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod2 srv-app3-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod2 srv-app4-sgd-prod.onpe.gob.pe
   ./asadmin setup-ssh --sshuser payara_prod2 srv-app5-sgd-prod.onpe.gob.pe

Instalar Payara en los nodos::

   ./asadmin install-node --sshuser payara_prod2 srv-app1-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod2 srv-app2-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod2 srv-app3-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod2 srv-app4-sgd-prod.onpe.gob.pe
   ./asadmin install-node --sshuser payara_prod2 srv-app5-sgd-prod.onpe.gob.pe

Crear los nodos en el DAS (Java 11)::

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

(Opcional) Crear alias para ``asadmin`` (Java 11)::

   cd ~
   nano .bashrc

Agregar:

::

   alias asadmin='$HOME/payara5/bin/asadmin --port 12048 --user admin --passwordfile $HOME/payara5/pserver'

4.6. Creación de un NFS Server para Java 11
------------------------------------------

En el DAS (``192.168.49.97``), con usuario sudo:

Crear directorios y asignar permisos::

   sudo mkdir -p /var/nfs/prod2/sgd_repo
   sudo chmod -R 777 /var/nfs/prod2/
   sudo chown -R nobody:nobody /var/nfs/prod2/

Editar ``/etc/exports``::

   sudo nano /etc/exports

Agregar (o modificar)::

   /var/nfs/prod2  192.168.49.0/24(rw,sync,no_subtree_check)

Exportar y reiniciar::

   sudo exportfs -a
   sudo systemctl restart nfs-server

Habilitar el puerto ``12048`` en el firewall (para la consola)::

   sudo firewall-cmd --permanent --add-port=12048/tcp
   sudo firewall-cmd --reload

Con el usuario ``payara_prod2``, crear el enlace simbólico::

::

   su - payara_prod2
   ln -s /var/nfs/prod2/sgd_repo/ /opt/payara_prod2/sgd_repo

Configuración en los servidores nodo (Java 11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verificar el NFS en el DAS::

   sudo showmount -e 192.168.49.97

Crear el punto de montaje y montar::

   sudo mkdir /mnt/nfs_prod2
   sudo mount -t nfs 192.168.49.97:/var/nfs/prod2 /mnt/nfs_prod2

Editar ``/etc/fstab``::

   sudo nano /etc/fstab

Añadir::

   192.168.49.97:/var/nfs/prod2  /mnt/nfs_prod2  nfs  defaults  0 0

Desde ``payara_prod2``, actualizar el enlace simbólico::

::

   su - payara_prod2
   unlink sgd_repo   # si ya existía
   ln -s /mnt/nfs_prod2/sgd_repo/ /opt/payara_prod2/sgd_repo
   ls -l

Con esto se completa la configuración de Payara en un entorno con Java 8 y Java 11, con el DAS y los nodos compartiendo directorios NFS, permitiendo despliegues y administración remota.

----------------------------------------------------------------
5. NOTAS FINALES
----------------------------------------------------------------

- En un entorno real de producción, se recomienda reforzar la seguridad de los puertos de administración (``11048``, ``12048``), restringiendo su acceso solo a redes o IP autorizadas.
- Verificar de forma periódica el correcto montaje NFS en todos los nodos para evitar problemas de disponibilidad en el despliegue de aplicaciones.
- Ajustar los nombres de dominio y las direcciones IP según la infraestructura real de cada organización.
- Se recomienda automatizar parte de la configuración con scripts o herramientas de orquestación si el número de servidores es alto.

Fin del Manual
