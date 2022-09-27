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
static FT_Library* FT_Library_FromCapsule(PyObject* capsule) {
    return (FT_Library*) PyCapsule_GetPointer(capsule, cap_library);
}

static void PyCapsule_FreeLibrary(PyObject* capsule) {
    if ( PyCapsule_IsValid(capsule, cap_library)) {
        free(FT_Library_FromCapsule(capsule));
    }
}

static PyObject* PyCapsule_FromLibrary(FT_Library* library ) {
    return PyCapsule_New(library, cap_library, PyCapsule_FreeLibrary);
}
/* Start FT_Library <-> Capsule */

/* Start FTC_Manager <-> Capsule */
static FTC_Manager* FTC_Manager_FromCapsule(PyObject* capsule) {
    return (FTC_Manager*) PyCapsule_GetPointer(capsule, cap_manager);
}

static void PyCapsule_Free_FTC_Manager(PyObject* capsule) {
    if ( PyCapsule_IsValid(capsule, cap_manager)) {
        free(FTC_Manager_FromCapsule(capsule));
    }
}

static PyObject* PyCapsule_From_FTC_Manager(FTC_Manager* manager ) {
    return PyCapsule_New(manager, cap_manager, PyCapsule_Free_FTC_Manager);
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

    printf("Freeing FreeType %p\n", library);

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

static int face_requester(FTC_FaceID face_id, FT_Library library, FT_Pointer req_data, FT_Face* face) {


    PyObject* args = Py_BuildValue("(l)", face_id);
    PyObject* result = PyObject_CallObject( (PyObject*) req_data, args);
    Py_DECREF(args);

    if ( result == NULL ) {
        // error
        printf("Error calling python\n");
    }

    PyObject* pathObject = PyUnicode_AsUTF8String(result);
    char* path = PyBytes_AsString(pathObject);
    Py_DECREF(pathObject);

    printf("Path is %s\n", path);

    return FT_New_Face(library, path , 0, face);
}

static PyObject* method_manager_new(PyObject* self, PyObject* args) {

    PyObject* Clibrary;
    PyObject* id_to_path;

    if (!PyArg_ParseTuple(args, "OO", &Clibrary, &id_to_path)) {
        return NULL;
    }

    if (!PyCallable_Check(id_to_path)) {
        PyErr_SetString(PyExc_TypeError, "parameter must be callable");
        return NULL;
    }

    FT_Library* library = FT_Library_FromCapsule(Clibrary);

    void* manager = calloc(1, sizeof(FTC_Manager));

    if ( manager == 0 ) {
        PyErr_NoMemory();
        Py_INCREF(Py_None);
        return Py_None;
    }

    Py_INCREF(id_to_path);

    if ( FTC_Manager_New(*library, 0, 0, 0L, face_requester, (FT_Pointer) id_to_path, manager) != 0 ) {
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

    printf("Freeing Cache Manager %p\n", manager);
    FTC_Manager_Done(*manager);

    Py_INCREF(Py_None);
    return Py_None;
}

static void dbg_ft_face(FT_Face face) {

    printf("FT_Face\n");
    printf("\tNum Faces: %lu\n", face->num_faces);
    printf("\tFace Index: %lu\n", face->face_index);
    printf("\tFace Flags: %lu\n", face->face_flags);
    printf("\tStyle Flags: %lu\n", face->style_flags);
    printf("\tNum Glyphs: %lu\n", face->num_glyphs);
    printf("\tFamily Name: %s\n", face->family_name);
    printf("\tStyle Name: %s\n", face->style_name);
    printf("\tFixed Sizes: %d\n", face->num_fixed_sizes);
    printf("\tNum Charmaps: %d\n", face->num_charmaps);
}

static PyObject* method_manager_ft_get_face(PyObject* self, PyObject* argsOiII) {
    PyObject* Cmanager;
    FT_UInt width, height;
    long int faceId;

    if (!PyArg_ParseTuple(argsOiII, "OlII", &Cmanager, &faceId, &width, &height)) {
        return NULL;
    }

    FTC_ScalerRec scaler_rec = {
        .face_id = (FTC_FaceID) faceId,
        .width = width,
        .height = height,
        .pixel = 1,
        .x_res = 0,
        .y_res = 0,
    };

    FT_SizeRec *size_rec;

    FTC_Manager* manager = FTC_Manager_FromCapsule(Cmanager);

    if ( FTC_Manager_LookupSize(*manager, &scaler_rec, &size_rec) != 0 ) {
        return NULL;
    }

    dbg_ft_face(size_rec->face);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef methods[] = {
    {"freetype_init", method_freetype_init, METH_VARARGS, "Init"},
    {"freetype_done", method_freetype_done, METH_VARARGS, "Done"},
    {"freetype_version", method_freetype_version, METH_VARARGS, "Version"},
    {"cache_manager_new", method_manager_new, METH_VARARGS, "New Cache Manager"},
    {"cache_manager_done", method_manager_done, METH_VARARGS, "Del Cache Manager"},
    {"cache_manager_get_face", method_manager_ft_get_face, METH_VARARGS, "Manager Get Face"},

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