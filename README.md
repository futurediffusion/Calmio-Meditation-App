# Calmio Meditation App

Calmio es un prototipo de aplicación de respiración construido con **PySide6**. A continuación se describen sus componentes principales y la lógica que los conecta. Este documento es la referencia básica antes de modificar cualquier parte del sistema.

## Contenido

- [Requisitos](#requisitos)
- [Pantalla principal de meditación](#pantalla-principal-de-meditación)
- [Menú y controles](#menú-y-controles)
- [Estadísticas](#estadísticas)
  - [Hoy](#hoy)
  - [Semana](#semana)
  - [Mes](#mes)
- [Finalización de sesión](#finalización-de-sesión)
- [Sistema de logros](#sistema-de-logros)
- [Lista de sesiones y detalles](#lista-de-sesiones-y-detalles)
- [Animaciones de fondo y ondas](#animaciones-de-fondo-y-ondas)
- [Modo desarrollador](#modo-desarrollador)
- [Resumen técnico del sistema](#resumen-técnico-del-sistema)

## Requisitos

- Python 3.8+
- PySide6
- platformdirs

En Windows puede ejecutarse `run_app.bat`, el script creará un entorno virtual en `venv`, instalará dependencias y lanzará la aplicación. En otros sistemas cree un entorno virtual manualmente y ejecute `python main.py`.

## Pantalla principal de meditación

- **BreathCircle** (`breath_circle.py`)
  - Círculo central que se expande al presionar el ratón o la barra espaciadora y se contrae al soltar.
  - Controla el conteo de respiraciones y el aumento gradual de tiempos de inhalación/exhalación.
  - Al finalizar cada exhalación válida genera un efecto de "ripple" y notifica a `MainWindow`.
  - Almacena la fase actual (`idle`, `inhaling`, `exhaling`) y cronometra cada ciclo.
- **Animaciones asociadas**
  - Expansión/contracción del radio mediante `QPropertyAnimation`.
  - Cambio de color entre el tono base y su complemento durante cada fase.
  - Efecto de anillo expansivo que se desvanece tras la exhalación.
- **Interacciones**
  - El usuario puede pulsar el círculo o mantener la barra espaciadora para respirar.
  - Cada ciclo incrementa el contador visual en la parte superior.
  - Mensajes motivacionales aparecen cada cierto número de respiraciones.

## Menú y controles

- Botón de tres puntos abre o cierra los botones secundarios:
  - Estadísticas (`📊`), Configuración (`⚙️`), Sonido (`🎵`), Finalizar sesión (`🛑`) y menú de desarrollador (`🐛`).
  - Los botones se ocultan cuando se pulsa fuera de ellos o al cerrar overlays.
- Finalizar sesión cierra la respiración en curso y muestra la vista de **Finalización de sesión**.
- El menú de configuración permite borrar todos los datos guardados.

## Estadísticas

El overlay de estadísticas (`stats_overlay.py`) muestra diferentes pestañas gestionadas mediante un `QStackedWidget`.

### Hoy

- **ProgressCircle** (`progress_circle.py`)
  - Círculo de progreso que se llena por cada 30 minutos meditados.
  - Muestra marcas de 10, 20 y 30 minutos alrededor del arco.
- Indicador de racha consecutiva de días (`🔥 n días consecutivos`).
- Botón "Ver sesiones" abre la lista de sesiones del día.
- Botón de logros del día muestra los badges obtenidos hoy.
- Se presenta la información de la última sesión realizada.

### Semana

- **WeeklyStatsView** (`weekly_stats.py`)
  - Gráfico de barras con los minutos meditados de lunes a domingo.
  - Textos muestran total semanal, promedio diario y sesión más larga.

### Mes

- **MonthlyStatsView** (`monthly_stats.py`)
  - Gráfico de línea suave con los minutos totales por semana del mes.
  - Indicadores de total mensual, promedio diario, mejor semana y racha más larga.
  - Anillo de progreso (`DonutProgress`) refleja el objetivo mensual (por defecto 600 minutos).

## Finalización de sesión

- Vista `SessionComplete` (`session_complete.py`).
  - Tarjeta con duración total, número de respiraciones y tiempos de inhalación/exhalación finales.
  - Muestra hora de inicio y fin de la sesión.
  - Si se obtuvieron logros durante la sesión aparece un botón resaltando el último badge.
  - Animación de estrellas efímeras al completar la sesión.
  - Botón **Listo** vuelve a la pantalla principal y actualiza las estadísticas del día.

## Sistema de logros

- Los códigos de logros y nombres visibles se definen en `badges.py`.
- `DataStore` guarda cuántas veces se ha conseguido cada logro y los obtenidos en el día.
- Tras guardar una sesión se calculan nuevos badges según:
  - Tiempo total meditado acumulado.
  - Cantidad de respiraciones en la sesión.
  - Número de sesiones en el mismo día.
  - Racha de días consecutivos.
- Las vistas `BadgesView` permiten visualizar los logros alcanzados en el día o en una sesión concreta.

## Lista de sesiones y detalles

- **TodaySessionsView** (`today_sessions.py`)
  - Lista desplazable con todas las sesiones del día, incluyendo duración, hora y datos de respiración inicial/final.
  - Al pulsar una sesión se abre la vista de detalles.
- **SessionDetailsView** (`session_details.py`)
  - Resume los datos de la sesión seleccionada.
  - Gráfico suave muestra la evolución de tiempos de inhalación y exhalación de cada ciclo.
  - Desde aquí también se pueden consultar los logros obtenidos en esa sesión.

## Animaciones de fondo y ondas

- **AnimatedBackground** (`animated_background.py`)
  - Fondea la ventana con un degradado radial que cambia de color siguiendo los siete colores de los chakras.
  - La transición al siguiente color ocurre cada vez que el contador de respiraciones alcanza ciertos umbrales del ciclo de 30.
  - Incluye tres anillos luminosos que giran lentamente alrededor del centro.
  - La opacidad del fondo aumenta durante la inhalación y se desvanece al exhalar.
- **WaveOverlay** (`wave_overlay.py`)
  - Al final de una inhalación se generan ondas circulares que se expanden desde el centro durante varios segundos.
  - Estas ondas se dibujan sobre la interfaz pero no bloquean la interacción.

## Sistema de sonido opcional

- El overlay `SoundOverlay` permite activar un ambiente (bosque, lluvia, fuego o mar).
- También puede activarse un **modo música** que reproduce la nota `notado.mp3`
  cambiando el tono en cada respiración (DO, RE, MI, FA, SOL, LA, SI, DO).
- Al llegar al punto máximo de cada inhalación suena `drop.mp3`.
- Una campana con fundido de salida suave (`bell.mp3`) se reproduce cada 10 respiraciones.
- Dos casillas (con indicación ON/OFF) permiten activar o desactivar tanto el modo música como la campana.
- Se agregaron deslizadores de volumen independientes para el modo música y para el sonido `drop`, además de los controles general y de campana.
- El botón **Silenciar todo** detiene cualquier sonido en reproducción.
- Los archivos `bosque.mp3`, `LLUVIA.mp3`, `fuego.mp3`, `mar.mp3`, `notado.mp3`,
  `bell.mp3` y `drop.mp3` deben ubicarse en `assets/sounds/`.

## Modo desarrollador

- El **DeveloperOverlay** ofrece dos funciones:
  - Cambiar la velocidad de animaciones y temporizador (10× más rápido para pruebas).
  - Avanzar virtualmente al día siguiente, útil para probar el cálculo de rachas y estadísticas.
- Se activa desde el botón 🐛 del menú principal.

## Resumen técnico del sistema

- `MainWindow` orquesta todos los widgets y controla el estado global de la sesión.
- `DataStore` persiste la información en `calmio_data.json` dentro del directorio de usuario mediante `platformdirs`.
- Los tiempos de respiración se incrementan ligeramente con cada ciclo para guiar una respiración cada vez más profunda.
- Las animaciones de fondo, texto y ondas se sincronizan con la fase de inhalación/exhalación.
- El sistema admite modo claro u oscuro adaptándose a la paleta de Qt, modificando colores del fondo animado.
- Los logros se detectan automáticamente al finalizar cada sesión y se almacenan con su fecha.
- El diseño modular permite extender vistas o lógicas sin afectar la pantalla principal.

