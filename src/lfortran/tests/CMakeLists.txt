project(tests)

macro(ADDTEST name)
    add_executable(${name} ${name}.cpp)
    target_link_libraries(${name} lfortran_lib  ${ARGN})
    add_test(${name} ${PROJECT_BINARY_DIR}/${name})
endmacro(ADDTEST)

macro(ADDTESTC name)
    add_executable(${name} ${name}.c)
    target_link_libraries(${name} lfortran_lib  ${ARGN})
    add_test(${name} ${PROJECT_BINARY_DIR}/${name})
endmacro(ADDTESTC)

# Copies file from source to binary directory for out-of-tree builds
macro(COPYFILE filename)
    if (NOT(${CMAKE_CURRENT_SOURCE_DIR} STREQUAL ${CMAKE_CURRENT_BINARY_DIR}))
        add_custom_target(copy-${filename} ALL DEPENDS
            ${CMAKE_CURRENT_BINARY_DIR}/${filename})
        add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${filename}
            COMMAND ${CMAKE_COMMAND} -E copy
                ${CMAKE_CURRENT_SOURCE_DIR}/${filename}
                ${CMAKE_CURRENT_BINARY_DIR}/${filename}
            DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${filename})
    endif()
endmacro(COPYFILE)


ADDTEST(test_parse p::doctest)
ADDTEST(test_ast)
ADDTESTC(test_cwrapper)

ADDTEST(test_pickle p::doctest)
COPYFILE(ref_pickle.txt)

ADDTEST(x)
if (WITH_JSON)
    ADDTEST(test_ast_to_json p::doctest)
endif()
if (WITH_LLVM)
    ADDTEST(test_llvm p::doctest)
endif()
