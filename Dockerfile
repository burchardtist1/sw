FROM python:3.10-buster

ARG UID
ARG GID
ENV USER=user
RUN groupadd -g $GID -o $USER
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $USER
USER $USER

WORKDIR /code
COPY --chown=${UID}:${GID} . /code/

ENV PATH=$PATH:/home/$USER/.local/bin
RUN pip install 'poetry==1.1.12'
RUN poetry config virtualenvs.create false && poetry update

ENV PYTHONUNBUFFERED=1