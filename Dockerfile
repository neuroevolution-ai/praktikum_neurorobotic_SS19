FROM jupyter/scipy-notebook
ENV cache_breaker 2019_11_22
USER root

RUN apt-get update && apt-get dist-upgrade -y

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential cmake \
    libltdl7-dev libreadline6-dev \
    libncurses5-dev libgsl0-dev python-all-dev python-numpy python-scipy \
    python-matplotlib ipython openmpi-bin libopenmpi-dev python-nose \
    cython wget git autoconf libgsl-dev \
    python3-pip python3-dev python3

RUN pip3 install numpy

##################
### neurosim
##################

RUN git clone https://github.com/INCF/libneurosim.git \
    && cd libneurosim \
    && touch README \
    && autoreconf --install --force \
    && autoconf configure.ac \
    && ./configure  --with-python=3  --prefix=/libneurosim.install \
    && make && make check && make install && make clean distclean \
    && cd .. && rm -rf libneurosim

# workaround for nest issue #1080
RUN cd /libneurosim.install/lib \
    && ln -s libpy3neurosim.la libpyneurosim.la \
    && ln -s libpy3neurosim.a libpyneurosim.a\
    && ln -s libpy3neurosim.so libpyneurosim.so\
    && ln -s libpy3neurosim.so.0.0.0 libpyneurosim.so.0.0.0


##################
### install nest
##################

RUN wget https://codeload.github.com/nest/nest-simulator/tar.gz/v2.16.0 && \
    tar -xzvf v2.16.0 && \
    rm -f v2.16.0

RUN mkdir /usr/bin/nest && mkdir nest-build && cd nest-build  && \
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr/bin/nest \
     -Dwith-gsl=ON \
     -Dwith-libneurosim=/libneurosim.install \
     /home/jovyan/nest-simulator-2.16.0

RUN cd nest-build && make && make install

# we can't source nest-vars.sh as in a dockerfile,
# so instead we set the respective  variables directly
USER $NB_UID
ENV NEST_INSTALL_DIR=/usr/bin/nest
ENV NEST_DATA_DIR=$NEST_INSTALL_DIR/share/nest
ENV NEST_DOC_DIR=$NEST_INSTALL_DIR/share/doc/nest
ENV NEST_MODULE_PATH=$NEST_INSTALL_DIR/lib/nest
ENV NEST_PYTHON_PREFIX=$NEST_INSTALL_DIR/lib/python3.7/site-packages
ENV PYTHONPATH=$NEST_PYTHON_PREFIX:$PYTHONPATH
ENV PATH=$NEST_INSTALL_DIR/bin:$PATH
USER root


##################
### pybullet
##################

# need to compile myself so numpy is used for getCameraImage
RUN git clone --recurse-submodules https://github.com/bulletphysics/bullet3.git \
 && cd bullet3 \
 && ./build_cmake_pybullet_double.sh

RUN chown -R $NB_UID /home/jovyan
USER $NB_UID
RUN cd bullet3 && python3 -m pip install .

#######################################
### roboschool and ANN-requirements
#######################################

# this is the environment that was used to create the example ANN.
# until we have full conversion of the environment (physic simulation and brain simulation basically) we install the full environment into this container as well. After we have full conversion we can ditch those dependencies again.
# These dependencies are copied from here: https://github.com/spikingevolution/evolution-strategies/blob/master/Dockerfile

# Update the system and install base and roboschool requirements
USER root
RUN  apt-get install -y git xvfb ffmpeg libgl1-mesa-dev libharfbuzz0b libpcre3-dev libqt5x11extras5
USER $NB_USER

RUN conda install --quiet --yes \
    'gast==0.2.2' \
    'matplotlib' \
    'pandas' \
    'ipywidgets'


RUN conda clean --yes --all -f && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER


RUN pip install --quiet \
    tensorflow==1.14.0 \
    numpy==1.16.4 \
    gym \
    roboschool==1.0.48

########################
### SNN Toolbox
########################

# USER root
RUN git clone https://github.com/bjuergens/snn_toolbox.git
# USER $NB_USER

RUN cd snn_toolbox && pip install --user .


##################
### final stuff
##################

# install pynn from source to fix warning "unable to find nest extension"
RUN python3 -m pip install --no-binary :all: PyNN

# ipympl must be installed as user jovyan
RUN python3 -m pip install ipympl

RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager \
    && jupyter labextension install jupyter-matplotlib

RUN mkdir base_repository
WORKDIR base_repository



# xvfb-run allows rendering in roboschool

CMD ["xvfb-run", "-s", "-screen 0 1400x900x24", "start-notebook.sh", "--NotebookApp.token=''"]

#CMD ["start-notebook.sh", "--NotebookApp.token=''"]
