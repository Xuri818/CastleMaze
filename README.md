# 🏰 CastleMaze

**CastleMaze** es una aventura de ingenio ambientada en un oscuro laberinto medieval, donde el jugador debe desafiar los muros, explorar caminos ocultos y escapar de una trampa ancestral. Cada partida es única: los pasillos cambian, los atajos aparecen donde antes solo había piedra, y la salida nunca está garantizada. ¿Lograrás encontrar la ruta correcta o te perderás en la oscuridad?

## 🎯 Descripción

CastleMaze está desarrollado en **Python 3.13** utilizando **PyQt6 6.7.0** para la construcción de una interfaz gráfica moderna e interactiva. El núcleo del juego se basa en dos algoritmos fundamentales:

- **Depth-First Search (DFS)**: utilizado para generar laberintos perfectos, donde existe una única ruta entre dos puntos.
- Posteriormente, se aplica una **función de "ruptura de muros"**, que introduce atajos estratégicos y transforma el laberinto en una estructura imperfecta, agregando múltiples rutas posibles y mayor desafío.
- **Backtracking**: empleado para encontrar todas las soluciones válidas desde el punto de inicio hasta la meta, identificando además la ruta más corta.

Esta combinación algorítmica no solo asegura partidas dinámicas, sino que también refuerza el enfoque analítico detrás del diseño del juego.

## 🧠 Características principales

- 🔄 **Laberintos dinámicos**: se generan aleatoriamente en cada partida.
- 📐 **Tamaños configurables**:
  - Easy: 11x11
  - Standard: 17x17
  - Hard: 21x21
  - Extreme: 27x27
    
- 🧭 **Resolución automatizada**:
  - Visualización paso a paso de **backtracking** y la **ruta óptima**.

- 🎮 **Modos de juego**:
  - **Classic Mode**: control manual del jugador con teclado.
  - **Solver Mode**: se muestra cómo la IA resuelve el laberinto.
    
- 💾 **Guardado y carga de partidas**.
  
- 🖼️ **Renderizado con sprites** cargados desde un archivo JSON.
  
- 🗂️ **Estructura modular**:
  - `config/` para algoritmos y clases.
  - `ui/` para renderizado y texturas.
  - `assets/` para sprites y recursos visuales.

---

**Desarrollado por:**  
- Emilio Funes  
- David Calvo  

Tecnológico de Costa Rica — Ingeniería en Computación  
I Semestre, 2025
