FROM gcr.io/oss-fuzz-base/base-builder-python

RUN apt-get update && apt-get install -y make git

COPY . $SRC/compliance-trestle
WORKDIR $SRC/compliance-trestle

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install atheris && \
    python3 -m pip install .

COPY .clusterfuzzlite/build.sh $SRC/build.sh