FROM debian:bullseye-slim

ENV PYENV_ROOT=/root/.pyenv
ENV PATH=${PYENV_ROOT}/bin:${PATH}

ARG PYTHON_VERSIONS

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libbz2-dev \
    libcurl4-openssl-dev \
    libedit-dev \
    libexpat1-dev \
    libffi-dev \
    libgdbm-dev \
    liblzma-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libnss3-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    llvm \
    make \
    tk-dev \
    wget \
    xz-utils \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://pyenv.run | bash

RUN for version in ${PYTHON_VERSIONS}; do \
      pyenv install $version; \
    done

RUN pyenv global ${PYTHON_VERSIONS}

RUN echo 'eval "$(pyenv init -)"' >> ~/.bashrc
