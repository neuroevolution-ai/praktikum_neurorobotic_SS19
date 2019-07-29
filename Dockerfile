FROM jupyter/scipy-notebook
ENV cache_breaker 2019_07_27
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


##################
### final stuff
##################

# install pynn from source to fix warning "unable to find nest extension"
RUN python3 -m pip install --no-binary :all: PyNN

# ipympl must be installed as user jovyan
RUN python3 -m pip install ipympl

RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager \
    && jupyter labextension install jupyter-matplotlib

RUN mkdir pra
WORKDIR pra

ADD neuro_robotic.ipynb neuro_robotic_readonly.ipynb
