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
git clone --depth 1 https://github.com/OpenVisualCloud/SVT-AV1
git clone --depth 1 https://github.com/vapoursynth/vapoursynth.git

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

cmake -DCMAKE_INSTALL_PREFIX="$PREFIX" -DBUILD_SHARED_LIBS=0 -DCONFIG_TUNE_VMAF=1 -DCMAKE_BUILD_TYPE=Release -DENABLE_EXAMPLES=1 -DENABLE_DOCS=0 -DENABLE_TESTS=0 -DCMAKE_CXX_FLAGS="-O3 -march=native" -DCMAKE_C_FLAGS="-O3 -march=native" -DCMAKE_C_FLAGS_INIT="-static" ..
cmake --build . -j
cmake --install .


# ______________SVT-AV1_____________
cd "$SRC/SVT-AV1"
mkdir -p build
cd build

cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$PREFIX" -DCMAKE_BUILD_TYPE=Release -DBUILD_DEC=OFF -DBUILD_SHARED_LIBS=OFF ..
make -j
make install


# FFMPEG

cd "$SRC/ffmpeg"
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
        --enable-libdav1d


make -j
make install


# ________________VAPOURSYNTH_____________________
cd "$SRC/vapoursynth"
autoreconf -ivf
./autogen.sh
./configure --prefix="$PREFIX"
make
make install 

cd "$PREFIX"
cp libvslsmashsource.so lib/vapoursynth/libvslsmashsource.so
