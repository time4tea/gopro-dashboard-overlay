#include <Python.h>
#include <stdio.h>

#include <freetype2/ft2build.h>
#include FT_FREETYPE_H
#include FT_GLYPH_H
#include FT_BITMAP_H
#include FT_STROKER_H
#include FT_MULTIPLE_MASTERS_H
#include FT_SFNT_NAMES_H
#ifdef FT_COLOR_H
#include FT_COLOR_H
#endif

typedef struct {
    PyObject_HEAD FT_Face face;
    unsigned char *font_bytes;
    int layout_engine;
} FontObject;

static PyTypeObject Font_Type;


static PyObject* method_hello(PyObject *self, PyObject *args) {
    printf("Hello, World\n");
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef methods[] = {
    {"hello", method_hello, METH_VARARGS, "Hello"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_freetype",
    "Somecrap",
    -1,
    methods
};

static int init_module(PyObject *py_module) {
    return 0;
}

PyMODINIT_FUNC PyInit__freetype(void) {
    PYObject* m = PyModule_Create(&module);

    if ( init_module(m) < 0 ) {
        return NULL;
    }

    return m;
}