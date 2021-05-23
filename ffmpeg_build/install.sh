#!/usr/bin/bash 

export PREFIX="$PWD"
mkdir -p "$PREFIX/src"
export SRC="$PREFIX/src"

rm -rf bin/* include/* lib/* share/* src/*
rmdir bin include lib share src
mkdir -p "$SRC"

cd "$SRC"

# Downloading or updating libraries

git clone --depth 1 https://git.ffmpeg.org/ffmpeg.git
git clone --depth 1 https://aomedia.googlesource.com/aom
git clone --depth 1 https://github.com/Netflix/vmaf
git clone --depth 1 https://code.videolan.org/videolan/dav1d

# Compiling

# ______________VMAF________________
cd "$SRC/vmaf/libvmaf"
meson --prefix="$PREFIX" --libdir lib --buildtype release -Denable_docs=false build
ninja -C build install

mkdir -p "$PREFIX/share"
cd "$PREFIX/src/vmaf"
cp -R -P -p model "$PREFIX/share"


# ______________dav1d_______________
cd "$PREFIX/src/dav1d"
meson --prefix="$PREFIX" --libdir lib --buildtype release -Dc_args="-O3 -march=native" -Denable_tools=false build
ninja -C build install


# ______________AOM_________________
cd "$SRC/aom"
mkdir -p cmake_build
cd cmake_build

cmake -DCMAKE_INSTALL_PREFIX="$PREFIX" -DBUILD_SHARED_LIBS=1 -DCMAKE_BUILD_TYPE=Release -DENABLE_EXAMPLES=1 -DENABLE_DOCS=0 -DENABLE_TESTS=0 -DCMAKE_CXX_FLAGS="-flto -O3 -march=native" -DCMAKE_C_FLAGS="-flto -O3 -march=native" -DCMAKE_C_FLAGS_INIT="-flto=8 -static" ..
cmake --build . -j 20
cmake --install .


# FFMPEG

cd "$PREFIX/src/ffmpeg"
PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig" ./configure --prefix=$PREFIX    \
        --extra-ldflags="-L $PREFIX/lib -Wl,-rpath,$PREFIX/lib"         \
        --enable-gpl --enable-nonfree --disable-doc                     \
                                                                        \
        --enable-openssl --enable-libass --enable-libbluray             \
        --enable-libfreetype --enable-libfribidi                        \
        --enable-libfontconfig                                          \
                                                                        \
        --enable-libfdk-aac --enable-libmp3lame --enable-libopus        \
        --enable-libvorbis                                              \
                                                                        \
        --enable-libx264 --enable-libx265 --enable-libvpx               \
                                                                        \
        --enable-libvmaf --enable-librav1e --enable-libsvtav1           \
        --enable-libaom  --enable-libdav1d


make -j
make install
