

# MedusaEngine

Medusa es un motor de juegos basado en Python y de código abierto (FOSS) para crear juegos en 2D con Pygame. No está destinado a empaquetarse como un módulo, sino a integrarse directamente en los archivos de tu proyecto.

Demos del juego a continuación

# Requisitos
Python 3.11 o una versión más reciente

requirements.txt: 
```
cx_Freeze==8.5.3
pygame-ce==2.5.6
pygbag==0.9.3
pyzmq==27.1.0
```
- Asegúrate de verificar las licencias individuales de cada requisito para saber qué puedes y no puedes hacer con ellos.
- Cx_freeze solo es necesario si usas build/buildwindows.py
- pygbag solo es necesario si usas build/buildweb.py
- Actualmente, el multijugador no está soportado en las compilaciones web

# Configuración del Proyecto
- Las instrucciones de configuración están diseñadas para PyCharm. La configuración para otros IDE puede variar.

1. `git clone https://github.com/AncientEntity/MedusaEngine.git`
2. Abre el proyecto en PyCharm
3. Configura un nuevo intérprete de Python/entorno virtual (venv) para el proyecto (Python 3.11>=)
4. Ejecuta `pip install -r requirements.txt` mientras estás en el venv (En la terminal de PyCharm, debería usar el venv automáticamente por defecto)
5. ¡Listo! Intenta ejecutar la configuración de ejecución "run game", ya que hay un juego de ejemplo que debería funcionar.

# Estructura del Proyecto
A continuación se muestra la estructura de proyecto prevista, pero no es necesario seguirla estrictamente.
- `/build`: Este directorio contiene scripts de compilación y archivos de salida para el proyecto. Si necesitas compilar o generar el proyecto, encontrarás los scripts y configuraciones necesarios aquí.

- `/engine`: Este directorio contiene los archivos del motor. Estos archivos son responsables de la funcionalidad principal del motor, como el renderizado, la física y el audio.

- `/game`: Este directorio contiene los archivos del juego. Aquí encontrarás los activos, scripts y otros recursos que conforman el juego en sí.

# Demos y Gifs

Demo de Knighty McKnightFace [(jugar aquí)](https://anciententity.itch.io/knighty-mcknightyface) (el código fuente está en la rama master)

![python_EA7pzBiGDy](https://github.com/AncientEntity/MedusaEngine/assets/22735861/2d6d4a19-3c53-4a3e-b414-f3aecea981dd)

Demo de Knighty McKnightFace [(jugar aquí)](https://anciententity.itch.io/knighty-mcknightyface) (el código fuente está en la rama master)

![python_BFsRluECuz](https://github.com/AncientEntity/MedusaEngine/assets/22735861/7ff670b8-0db8-4f6b-bd8f-63489d57ac3c)

Demo de Tiny Factory [(jugar aquí)](https://anciententity.itch.io/tiny-factory-remastered) (el código fuente está en la rama tiny-factory-remake)

![chrome_qQIUbQQSkM](https://github.com/AncientEntity/MedusaEngine/assets/22735861/21df0074-4c44-4731-b59e-3c6df15cf031)

Demo de Búsqueda de Ruta A* [(jugar aquí)](https://anciententity.itch.io/medusa-astar-demo) (el código fuente está en la rama tilemap-pathfinding)

![python_JWMPJNHslx](https://github.com/user-attachments/assets/3a5f0afc-5813-4d55-9ef9-80f314c2cf8d)

Demo Topdown [(jugar aquí)](https://anciententity.itch.io/topdown-shooter-demo) (el código fuente está en la rama topdown)

![undefined - Imgur](https://github.com/user-attachments/assets/ed102781-46b1-4dcc-b0a6-10706a2b1545)

Demo Topdown [(jugar aquí)](https://anciententity.itch.io/topdown-shooter-demo) (el código fuente está en la rama topdown)
![python_nd4VQ0PyAy](https://github.com/user-attachments/assets/8c8a05a9-c495-4945-97f7-31cf07bc24ec)


# Aviso de Licencia de Demos de Terceros

Varias demos de Medusa contienen activos de terceros con sus propias licencias separadas.

- [16x16 Dungeon Tileset](https://0x72.itch.io/dungeontileset-ii) - Licencia MIT
- [Brackey's Platform Bundle](https://brackeysgames.itch.io/brackeys-platformer-bundle) - CC0
- [Pixeloid Mono Font](https://www.dafont.com/pixeloid-mono.font) - [Licencia de Fuentes Abiertas SIL V1.1](https://openfontlicense.org/open-font-license-official-text/)

Cualquier activo no listado arriba es personalizado y sigue la Licencia MIT del Motor Medusa.
