cmake_minimum_required(VERSION 3.20)
project(EngineeringDataCpp VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Ścieżka do vcpkg
set(CMAKE_TOOLCHAIN_FILE "C:/Tools/vcpkg/scripts/buildsystems/vcpkg.cmake" CACHE STRING "")
set(VCPKG_TARGET_TRIPLET "x64-mingw-dynamic")

# CPR
set(cpr_DIR "C:/Tools/vcpkg/installed/x64-mingw-dynamic/share/cpr")
find_package(cpr CONFIG REQUIRED)

# nlohmann_json
set(nlohmann_json_DIR "C:/Tools/vcpkg/installed/x64-mingw-dynamic/share/nlohmann_json")
find_package(nlohmann_json CONFIG REQUIRED)

# CURL (jeśli nie wykrywa automatycznie przez CPR)
find_package(CURL REQUIRED)

# Tworzymy executable
add_executable(${PROJECT_NAME} cpp/main.cpp cpp/eurostat.cpp)

# Linkowanie bibliotek
target_link_libraries(${PROJECT_NAME}
    PRIVATE
    cpr::cpr
    nlohmann_json::nlohmann_json
    CURL::libcurl
)
