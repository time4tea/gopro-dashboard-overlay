#include <Python.h>
#include <stdio.h>
#include <stdlib.h>

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

static PyObject* method_freetype_init(PyObject* self, PyObject* args) {

    void* library = calloc(1, sizeof(FT_Library));

    if ( library == 0 ) {
        PyErr_NoMemory();
        Py_INCREF(Py_None);
        return Py_None;
    }

    if ( FT_Init_FreeType(library) != 0 ) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return PyLong_FromVoidPtr(library);
}

static PyObject* method_freetype_done(PyObject* self, PyObject* args) {
    PyObject* Llibrary = PyTuple_GetItem(args, 0);
    Py_INCREF(Llibrary);
    FT_Library* library = (FT_Library*) PyLong_AsVoidPtr(Llibrary);
    FT_Done_FreeType(*library);

    free(library);
    Py_DECREF(Llibrary);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* method_freetype_version(PyObject* self, PyObject* args) {

    PyObject* Llibrary = PyTuple_GetItem(args, 0);
    Py_INCREF(Llibrary);
    FT_Library* library = (FT_Library*) PyLong_AsVoidPtr(Llibrary);

    int major, minor, patch;

    printf("%p\n", library);

    FT_Library_Version(0, &major, &minor, &patch);

    printf("%d\n", major);

    PyObject* version = PyUnicode_FromFormat("%d.%d.%d", major, minor, patch);
    Py_DECREF(Llibrary);

    return version;
}

static PyMethodDef methods[] = {
    {"freetype_init", method_freetype_init, METH_VARARGS, "Init"},
    {"freetype_done", method_freetype_done, METH_VARARGS, "Done"},
    {"freetype_version", method_freetype_version, METH_VARARGS, "Version"},
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
    PyObject* m = PyModule_Create(&module);

    if ( init_module(m) < 0 ) {
        return NULL;
    }

    return m;
}