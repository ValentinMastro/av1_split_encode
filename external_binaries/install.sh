#!/usr/bin/bash

export PREFIX="$PWD"
mkdir -p "$PREFIX/src"
export SRC="$PREFIX/src"

rm -rf bin/* include/* lib/* share/* src/*
rmdir bin include lib share src
mkdir -p "$SRC"

compile_vmaf () {
	# Download
	cd "$SRC"
	git clone --depth 1 https://github.com/Netflix/vmaf
	# Compile
	cd "$SRC/vmaf/libvmaf"
	meson --prefix="$PREFIX" --libdir lib --buildtype release -Denable_docs=false build
	ninja -C build install

	mkdir -p "$PREFIX/share"
	cd "$PREFIX/src/vmaf"
	cp -R -P -p model "$PREFIX/share"
}

compile_dav1d () {
	# Download
	cd "$SRC"
	git clone --depth 1 https://code.videolan.org/videolan/dav1d
	# Compile
	cd "$PREFIX/src/dav1d"
	meson --prefix="$PREFIX" --libdir lib --buildtype release -Dc_args="-O3 -march=native" -Denable_tools=false build
	ninja -C build install
}

compile_aomenc () {
	# Download
	cd "$SRC"
	git clone --depth 1 https://aomedia.googlesource.com/aom
	# Compile
	cd "$SRC/aom"
	mkdir -p cmake_build
	cd cmake_build

	cmake -DCMAKE_INSTALL_PREFIX="$PREFIX" -DBUILD_SHARED_LIBS=0 -DCONFIG_TUNE_VMAF=0 -DCMAKE_BUILD_TYPE=Release -DENABLE_EXAMPLES=1 -DENABLE_DOCS=0 -DENABLE_TESTS=0 -DCMAKE_CXX_FLAGS="-O3 -march=native" -DCMAKE_C_FLAGS="-O3 -march=native" -DCMAKE_C_FLAGS_INIT="-static" ..
	cmake --build . -j
	cmake --install .
}

compile_svt_av1 () {
	# Download
	cd "$SRC"
	git clone --depth 1 https://github.com/OpenVisualCloud/SVT-AV1
	# Compile
	cd "$SRC/SVT-AV1"
	mkdir -p build
	cd build

	cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$PREFIX" -DCMAKE_BUILD_TYPE=Release -DBUILD_DEC=OFF -DBUILD_SHARED_LIBS=OFF ..
	make -j
	make install
}

compile_ffmpeg () {
	# Download
	cd "$SRC"
	git clone --depth 1 https://git.ffmpeg.org/ffmpeg.git
	# Compile
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
}

compile_vapoursynth () {
	# Download
	cd "$SRC"
	git clone --depth 1 https://github.com/vapoursynth/vapoursynth.git
	# Compile
	cd "$SRC/vapoursynth"
	autoreconf -ivf
	./autogen.sh
	./configure --prefix="$PREFIX"
	make
	make install

	cd "$PREFIX"
	cp libvslsmashsource.so lib/vapoursynth/libvslsmashsource.so
}

compile_vmaf
compile_dav1d
compile_aomenc
compile_svt_av1
compile_ffmpeg
compile_vapoursynth
