
# Praktikum Aufbau einer Simulationsumgebung für Neurorobotik-Experimente

Praktikum von _Björn Jürgens_ im Jahr 2019 am KIT

## getting started

``` 
docker build -t pra . 
docker run --rm -it -p 8888:8888 -v $(pwd)/neuro_robotic.ipynb:/home/jovyan/pra/neuro_robotic.ipynb pra  start-notebook.sh --NotebookApp.token=''
```

Man kann sich das Notebook auch im github anschauen. [link](https://github.com/spikingevolution/praktikum_neurorobotic_SS19/blob/master/neuro_robotic.ipynb). 
Es sei darauf hingewiesen, dass github nach jedem push ein paar Minuten braucht, bis das notebook im web richtig dargestellt wird.

