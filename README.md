Taller 1 – Sistema Conversión Cloud
* Gina Eveling Posada , Martin Daniel Rincón, Juan Camilo Muñoz, Felipe Serrano
* MINE semestre 202410
* Universidad de los Andes, Bogotá, Colombia
* {g.posadas, md.rincon, jc.munozc12, ff.serrano42}@uniandes.edu.co
* Descripción:
  * Entrega del Taller 1 correspondiente a la plataforma cloud que convierte los siguientes formatos de archivos DOCX, PPTX, XLSX, ODT  a PDF
  * Esta entrega esta compuesta de un servicio API restfull, un broker RabbitMq, un consumer de transformacion de archivos y una interfaz WEB en streamlit desplegada en la nube publica GCP
* Requerimientos:
  * Documento de arquitectura de la aplicación.
  * Colecciones, documentación y escenarios de pruebas en POSTMAN.
  *  Ajustes a la aplicacion para que cumpla con los requerimientos de arquitecturas definidos
  *  * Se solicita el despliegue del componente web, el worker y el sistema de almacenamiento de archivos en tres instancias de cómputo diferentes (máquinas virtuales):
  *  *  *   Instalar, configurar y ejecutar todas las dependencias (servidor de aplicaciones, librerías, etc.) y herramientas requeridas (firewall, llaves de acceso, etc.) para desplegar la aplicación web en una instancia de GCP denominada Web Server.
  *  *  *  Instalar, configurar y ejecutar el componente worker que procesa los archivos en la segunda instancia de GCP. Para que el escenario sea comparable, establezca el mismo mecanismo y la misma tasa de procesamiento de archivos por unidad de tiempo.
  *  *  *  Instalar, configurar y ejecutar un sistema de archivos de red (NFS) en la tercera instancia de GCP. Dicho elemento se denominará File Server y en él los componentes web y worker deberán almacenar y acceder a todos los archivos originales y procesados. Se deberá realizar la instalación en los componentes webworker del cliente NFS para que ambos puedan ingresar y guardar los archivos en el File Server.
  *  *  * Configurar el servicio Cloud SQL para administrar la base de datos de la aplicación web. Lo anterior exige modificar el web server y el worker para que ahora todos los datos transaccionales se gestionen en la base de datos creada. No es necesario definir ningún mecanismo de replicación ni alta disponibilidad adicional.
* Archivos
  * Documento de arquitectura, esta en la carpeta Documentos con el nombre Entrega 2 - Arquitectura, conclusiones y consideraciones.pdf
  * github: https://github.com/ffserrano42/sc_entrega2_1
  * video sustentacion: https://www.youtube.com/watch?v=if4X6BWsQu8
