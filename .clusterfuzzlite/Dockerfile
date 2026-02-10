FROM gcr.io/oss-fuzz-base/base-builder-python

# Install system dependencies
RUN apt-get update && apt-get install -y make git

# Copy the project source into the image
COPY . $SRC/compliance-trestle
WORKDIR $SRC/compliance-trestle

# Install the project and its dependencies
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install .

# Copy the build script
COPY .clusterfuzzlite/build.sh $SRC/