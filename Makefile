CC       := g++
CXXFLAGS := --std=c++17 -Wall
LDLIBS   := -lstdc++fs

SDLFLAGS := -lGL `sdl2-config --cflags --libs`
TESTMAP  := /media/bikkie/Sandisk/Respawn/r1o/maps/mp_box.bsp

ifeq ($(OS),Windows_NT)
    CC       := x86_64-w64-mingw32-g++
    SDLFLAGS := -lm -Wl,-subsystem,windows -lopengl32 `sdl2-config --cflags --libs`
    # runs in MSYS2 MINGW64 when compiled via make in MSYS2 MINGW64, but not from Powershell...
    TESTMAP  := E:/Mod/TitanfallOnline/maps/mp_box.bsp
endif

DUMMY != mkdir -p build

.PHONY: all run


all: build/lump_names.exe build/glview.exe

run: build/glview.exe
	build/glview.exe $(TESTMAP)

# TODO: .o builds
# TODO: clean

build/lump_names.exe: src/lump_names.cpp src/bsp_tool.hpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@

# OpenGL .bsp viewer
# NOTE: untested on Windows
build/glview.exe: src/glview.cpp src/bsp_tool.hpp src/camera.hpp src/common.hpp src/respawn_entertainment/meshes.hpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@ $(SDLFLAGS)