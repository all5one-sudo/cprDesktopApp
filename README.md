# RCP Desktop App
## Acerca del proyecto
En este repositorio se encuentra la aplicación desarrollada para uso conjunto con el Simulador de RCP Neonatal. El simulador al que se hace referencia se trata de un proyecto bajo la tutela del Profesor Oscar Cáceres, que consiste en un muñeco que mediante sensores realiza mediciones de maniobras de RCP. Este muñeco se encarga de medir presión ejercida sobre el pecho, así como la frecuencia con la que se realizan las compresiones.

En la aplicación de escritorio se tienen 2 modos de uso:
- Entrenamiento: se pueden ver gráficas en tiempo real del desempeño del usuario.
- Evaluación: se realizan pruebas a ciegas para comprobar lo aprendido.

El objetivo del proyecto es brindar apoyo a personas especializadas en la capacitación en RCP para neonatos. El modo de entrenamiento sirve para entrenar, valga la redundancia. Mientras que el modo de evaluación permite un feedback para las personas evaluadas.

## Aplicación
La aplicación está programada enteramente en Python. Se hace uso de la librería `PyQt6` para el diseño de la GUI (interfaz gráfica de usuario). Luego, se aplican métodos correspondientes al uso del puerto serie y análisis estadísticos.

### Interfaz de usuario

![GUI](/img/gui.png)

La imagen muestra la interfaz de usuario que aparece en el momento de ejecución de la misma. Por defecto nos encontramos en el modo de entrenamiento, sin embargo, al pasar al modo de evaluación, se tiene lo siguiente:

![Modo Evaluación](/img/eval.png)

### Uso
Al trabajar en modo de entrenamiento, las gráficas en tiempo real tienen la siguiente apariencia:

![Graficas](/img/train.png)

Una vez que se pasa al modo de entrenamiento, luego de finalizada la evaluación, se tiene la posibilidad de exportar un reporte en formato PDF, que incluye las gráficas de desempeño. Sin embargo, los porcentajes de calidad tanto de compresiones como de frecuencia se muestran ni bien se presiona el botón de finalizar como se muestra a continuación.

![Fin evaluación](/img/endEval.png)

Al seleccionar la opción de exportar resultados, se abre una ventana del explorador de archivos que permite seleccionar la ubicación y el nombre del archivo que contiene el reporte de desempeño. De allí se obtiene algo como lo que se puede ver a continuación:

![Reporte](/img/report.png)

