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
#include FT_CACHE_H
#ifdef FT_COLOR_H
#include FT_COLOR_H
#endif

#define MAYBE_UNUSED __attribute__ ((unused))

static  char cap_library[] = "library";
static  char cap_manager[] = "manager";

/* Start FT_Library <-> Capsule */
static FT_Library* FT_Library_FromCapsule( PyObject* capsule) {
    return (FT_Library*) PyCapsule_GetPointer(capsule, cap_library);
}

static void PyCapsule_FreeLibrary(PyObject* capsule) {
    if ( PyCapsule_IsValid(capsule, cap_library)) {
        free(FT_Library_FromCapsule(capsule));
    }
}

static PyObject* PyCapsule_FromLibrary( FT_Library* library ) {
    return PyCapsule_New(library, cap_library, PyCapsule_FreeLibrary);
}
/* Start FT_Library <-> Capsule */

/* Start FTC_Manager <-> Capsule */
static FTC_Manager* FTC_Manager_FromCapsule( PyObject* capsule) {
    return (FTC_Manager*) PyCapsule_GetPointer(capsule, cap_manager);
}

static void PyCapsule_Free_FTC_Manager(PyObject* capsule) {
    if ( PyCapsule_IsValid(capsule, cap_manager)) {
        free(FTC_Manager_FromCapsule(capsule));
    }
}

static PyObject* PyCapsule_From_FTC_Manager( FTC_Manager* library ) {
    return PyCapsule_New(library, cap_manager, PyCapsule_Free_FTC_Manager);
}
/* Start FTC_Manager <-> Capsule */


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

    return PyCapsule_FromLibrary(library);
}

static PyObject* method_freetype_done(PyObject* self, PyObject* args) {

    PyObject* Clibrary;

    if (!PyArg_ParseTuple(args, "O", &Clibrary)) {
        return NULL;
    }

    FT_Library* library = FT_Library_FromCapsule(Clibrary);
    FT_Done_FreeType(*library);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* method_freetype_version(PyObject* self, PyObject* args) {

    PyObject* Clibrary;

    if (!PyArg_ParseTuple(args, "O", &Clibrary)) {
        return NULL;
    }

    FT_Library* library = FT_Library_FromCapsule(Clibrary);

    int major, minor, patch;

    FT_Library_Version(*library, &major, &minor, &patch);

    return PyUnicode_FromFormat("%d.%d.%d", major, minor, patch);;
}

static int face_requester( FTC_FaceID face_id, FT_Library library, FT_Pointer req_data, FT_Face* face) {
    return 0;
}

static PyObject* method_manager_new(PyObject* self, PyObject* args) {

    PyObject* Clibrary;

    if (!PyArg_ParseTuple(args, "O", &Clibrary)) {
        return NULL;
    }

    FT_Library* library = FT_Library_FromCapsule(Clibrary);

    FT_Pointer req_data = NULL;

    void* manager = calloc(1, sizeof(FTC_Manager));

    if ( FTC_Manager_New(*library, 0, 0, 0L, face_requester, req_data, manager) != 0 ) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return PyCapsule_From_FTC_Manager(manager);
}

static PyObject* method_manager_done(PyObject* self, PyObject* args) {
    PyObject* Cmanager;

    if (!PyArg_ParseTuple(args, "O", &Cmanager)) {
        return NULL;
    }

    FTC_Manager* manager = FTC_Manager_FromCapsule(Cmanager);
    FTC_Manager_Done(*manager);

    return NULL;
}

static PyMethodDef methods[] = {
    {"freetype_init", method_freetype_init, METH_VARARGS, "Init"},
    {"freetype_done", method_freetype_done, METH_VARARGS, "Done"},
    {"freetype_version", method_freetype_version, METH_VARARGS, "Version"},
    {"cache_manager_new", method_manager_new, METH_VARARGS, "New Cache Manager"},
    {"cache_manager_done", method_manager_done, METH_VARARGS, "Del Cache Manager"},
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