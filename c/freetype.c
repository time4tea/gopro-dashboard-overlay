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

/* Copied from Pillow */
#define IMAGING_MODE_LENGTH \
    6 + 1 /* Band names ("1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "BGR;xy") */

#if SIZEOF_SHORT == 2
#define INT16 short
#elif SIZEOF_INT == 2
#define INT16 int
#else
#define INT16 short /* most things works just fine anyway... */
#endif

#define UINT8 unsigned char

#if SIZEOF_SHORT == 4
#define INT32 short
#elif SIZEOF_INT == 4
#define INT32 int
#elif SIZEOF_LONG == 4
#define INT32 long
#else
#error Cannot find required 32-bit integer type
#endif

struct ImagingPaletteInstance {
    /* Format */
    char mode[IMAGING_MODE_LENGTH]; /* Band names */

    /* Data */
    int size;
    UINT8 palette[1024]; /* Palette data (same format as image data) */

    INT16 *cache;   /* Palette cache (used for predefined palettes) */
    int keep_cache; /* This palette will be reused; keep cache */
};

typedef struct ImagingPaletteInstance *ImagingPalette;
typedef struct ImagingMemoryInstance *Imaging;

typedef struct {
    char *ptr;
    int size;
} ImagingMemoryBlock;

struct ImagingMemoryInstance {
    /* Format */
    char mode[IMAGING_MODE_LENGTH]; /* Band names ("1", "L", "P", "RGB", "RGBA", "CMYK",
                                       "YCbCr", "BGR;xy") */
    int type;                       /* Data type (IMAGING_TYPE_*) */
    int depth;                      /* Depth (ignored in this version) */
    int bands;                      /* Number of bands (1, 2, 3, or 4) */
    int xsize;                      /* Image dimension. */
    int ysize;

    /* Colour palette (for "P" images only) */
    ImagingPalette palette;

    /* Data pointers */
    UINT8 **image8;  /* Set for 8-bit images (pixelsize=1). */
    INT32 **image32; /* Set for 32-bit images (pixelsize=4). */

    /* Internals */
    char **image;               /* Actual raster data. */
    char *block;                /* Set if data is allocated in a single block. */
    ImagingMemoryBlock *blocks; /* Memory blocks for pixel storage */

    int pixelsize; /* Size of a pixel, in bytes (1, 2 or 4) */
    int linesize;  /* Size of a line, in bytes (xsize * pixelsize) */

    /* Virtual methods */
    void (*destroy)(Imaging im);
};


static  char cap_library[] = "FT_library";
static  char cap_manager[] = "FTC_manager";
static  char cap_size[] = "FT_size";
static  char cap_imagecache[] = "FTC_ImageCache";
static  char cap_bitcache[] = "FTC_SBitCache";

/* Start FT_Library <-> Capsule */
static FT_Library MAYBE_UNUSED FT_Library_FromCapsule(PyObject* capsule) {
    return (FT_Library) PyCapsule_GetPointer(capsule, cap_library);
}

static PyObject* MAYBE_UNUSED PyCapsule_FromLibrary(FT_Library library ) {
    return PyCapsule_New(library, cap_library, NULL);
}
/* End FT_Library <-> Capsule */

/* Start FTC_Manager <-> Capsule */
static FTC_Manager MAYBE_UNUSED FTC_Manager_FromCapsule(PyObject* capsule) {
    return (FTC_Manager) PyCapsule_GetPointer(capsule, cap_manager);
}

static PyObject* MAYBE_UNUSED PyCapsule_From_FTC_Manager(FTC_Manager manager ) {
    return PyCapsule_New(manager, cap_manager, NULL);
}
/* End FTC_Manager <-> Capsule */

/* Start FT_SizeRec <-> Capsule */
static FT_Size MAYBE_UNUSED FT_Size_FromCapsule(PyObject* capsule) {
    return (FT_Size) PyCapsule_GetPointer(capsule, cap_size);
}

static PyObject* MAYBE_UNUSED PyCapsule_From_FT_Size(FT_Size size ) {
    return PyCapsule_New(size, cap_size, NULL);
}
/* End FT_SizeRec <-> Capsule */

/* Start FTC_ImageCache <-> Capsule */
static FTC_ImageCache MAYBE_UNUSED FTC_ImageCache_FromCapsule(PyObject* capsule) {
    return (FTC_ImageCache) PyCapsule_GetPointer(capsule, cap_imagecache);
}

static PyObject* MAYBE_UNUSED PyCapsule_From_FTC_ImageCache(FTC_ImageCache imagecache ) {
    return PyCapsule_New(imagecache, cap_imagecache, NULL);
}
/* End FTC_ImageCache <-> Capsule */

/* Start FTC_SBitCache <-> Capsule */
static FTC_SBitCache MAYBE_UNUSED FTC_SBitCache_FromCapsule(PyObject* capsule) {
    return (FTC_SBitCache) PyCapsule_GetPointer(capsule, cap_bitcache);
}

static PyObject* MAYBE_UNUSED PyCapsule_From_FTC_SBitCache(FTC_SBitCache bitcache ) {
    return PyCapsule_New(bitcache, cap_bitcache, NULL);
}
/* End FTC_SBitCache <-> Capsule */

/* Start FTC_CMapCache <-> Capsule */
static FTC_CMapCache MAYBE_UNUSED FTC_CMapCache_FromCapsule(PyObject* capsule) {
    return (FTC_CMapCache) PyCapsule_GetPointer(capsule, cap_bitcache);
}

static PyObject* MAYBE_UNUSED PyCapsule_From_FTC_CMapCache(FTC_CMapCache bitcache ) {
    return PyCapsule_New(bitcache, cap_bitcache, NULL);
}
/* End FTC_CMapCache <-> Capsule */


static PyObject* method_freetype_init(PyObject* self, PyObject* args) {

    FT_Library library;

    if ( FT_Init_FreeType(&library) != 0 ) {
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

    FT_Done_FreeType(FT_Library_FromCapsule(Clibrary));
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* method_freetype_version(PyObject* self, PyObject* args) {

    PyObject* Clibrary;

    if (!PyArg_ParseTuple(args, "O", &Clibrary)) {
        return NULL;
    }

    FT_Library library = FT_Library_FromCapsule(Clibrary);

    int major, minor, patch;

    FT_Library_Version(library, &major, &minor, &patch);

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

    FT_Library library = FT_Library_FromCapsule(Clibrary);

    Py_INCREF(id_to_path);
    FTC_Manager manager;

    if ( FTC_Manager_New(library, 0, 0, 0L, face_requester, (FT_Pointer) id_to_path, &manager) != 0 ) {
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

    FTC_Manager_Done(FTC_Manager_FromCapsule(Cmanager));

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* method_cmapcache_new(PyObject* self, PyObject* args) {
    PyObject* Cmanager;

    if (!PyArg_ParseTuple(args, "O", &Cmanager)) {
        return NULL;
    }

    FTC_Manager manager = FTC_Manager_FromCapsule(Cmanager);

    FTC_CMapCache cmapcache;

    if ( FTC_CMapCache_New(manager, &cmapcache) != 0 ) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return PyCapsule_From_FTC_CMapCache(cmapcache);
}

static PyObject* method_imagecache_new(PyObject* self, PyObject* args) {

    PyObject* Cmanager;

    if (!PyArg_ParseTuple(args, "O", &Cmanager)) {
        return NULL;
    }

    FTC_Manager manager = FTC_Manager_FromCapsule(Cmanager);

    FTC_ImageCache imagecache;

    if ( FTC_ImageCache_New(manager, &imagecache) != 0 ) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return PyCapsule_From_FTC_ImageCache(imagecache);
}

static PyObject* method_bitcache_new(PyObject* self, PyObject* args) {

    PyObject* Cmanager;

    if (!PyArg_ParseTuple(args, "O", &Cmanager)) {
        return NULL;
    }

    FTC_Manager manager = FTC_Manager_FromCapsule(Cmanager);

    FTC_SBitCache bitcache;

    if ( FTC_SBitCache_New(manager, &bitcache) != 0 ) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return PyCapsule_From_FTC_SBitCache(bitcache);
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

static PyObject* method_manager_ft_get_face(PyObject* self, PyObject* argsOlII) {
    PyObject* Cmanager;
    FT_UInt width, height;
    long int faceId;

    if (!PyArg_ParseTuple(argsOlII, "OlII", &Cmanager, &faceId, &width, &height)) {
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

    FTC_Manager manager = FTC_Manager_FromCapsule(Cmanager);

    FT_Size size;
    if ( FTC_Manager_LookupSize(manager, &scaler_rec, &size) != 0 ) {
        return NULL;
    }

    dbg_ft_face(size->face);

    return PyCapsule_From_FT_Size(size);
}


//#define PIXEL(x) ((((x) + 32) & -64) >> 6)
#define PIXEL(x) (x >> 16)

static PyObject* method_blit_glyph(PyObject* self, PyObject* args) {

    Py_ssize_t dest_image_id;
    int dest_x, dest_y;
    int src_width, src_height, src_pitch;
    PyObject* src_mv;
    unsigned char ink_r, ink_g, ink_b;

    if (!PyArg_ParseTuple(args, "(bbb)niiOiii", &ink_r, &ink_g, &ink_b, &dest_image_id, &dest_x, &dest_y, &src_mv, &src_width, &src_height, &src_pitch)) {
        return NULL;
    }

    Py_buffer* buffer = PyMemoryView_GET_BUFFER(src_mv);

    unsigned char* source = (unsigned char*) buffer->buf;

    Imaging im = (Imaging) dest_image_id;

    // Ensure target image mode is RGBA
    if ( ! (im->mode[0] == 'R' && im->mode[1] == 'G' && im->mode[2] == 'B' && im->mode[3] == 'A') ) {
        PyErr_SetString(PyExc_TypeError, "Image mode must be RGBA");
        return NULL;
    }

    for (int y = 0; y < src_height; y++ ) {
        int target_y = dest_y + y;
        if (target_y < 0 || target_y >= im->ysize) {
            continue;
        }
        unsigned char* target = (unsigned char *)im->image[target_y] + dest_x * 4;
        for ( int x = 0 ; x < src_width; x++ ) {
            int target_x = dest_x + x;
            if ( target_x < 0 || target_x >= im->xsize ) {
                continue;
            }
            unsigned char v = source[x];
            if (target[x * 4 + 3] < v) {
                target[x * 4 + 0] = ink_r;
                target[x * 4 + 1] = ink_g;
                target[x * 4 + 2] = ink_b;
                target[x * 4 + 3] = v;
            }
        }
        source += src_pitch;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject* method_render_string_stroker(PyObject* self, PyObject* args) {

    PyObject* Cimagecache;
    PyObject* Clibrary;
    PyObject* Ccmapcache;
    FT_UInt width, height;
    long int faceId;
    PyObject* string;
    PyObject* cb;

    int stroke_width = 2;

    if (!PyArg_ParseTuple(args, "OOOlIIOO", &Clibrary, &Ccmapcache, &Cimagecache, &faceId, &width, &height, &string, &cb)) {
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

    FT_Library library = FT_Library_FromCapsule(Clibrary);
    FTC_ImageCache imagecache = FTC_ImageCache_FromCapsule(Cimagecache);
    FTC_CMapCache cmapcache = FTC_CMapCache_FromCapsule(Ccmapcache);

    FT_Stroker stroker;

    FT_Error error = FT_Stroker_New(library, &stroker);
    if (error) {
        return NULL;
    }

    FT_Stroker_Set( stroker, (FT_Fixed)stroke_width * 64, FT_STROKER_LINECAP_ROUND, FT_STROKER_LINEJOIN_ROUND, 0);

    FT_Glyph glyph;
    Py_UCS4 current_char;
    FT_UInt char_index;

    Py_ssize_t length = PyUnicode_GET_LENGTH(string);
    for (int i = 0 ; i < length; i++ ) {
        current_char = PyUnicode_READ_CHAR(string, i);
        char_index = FTC_CMapCache_Lookup( cmapcache, (FTC_FaceID) faceId, -1, current_char);

        if (FTC_ImageCache_LookupScaler(
            imagecache,
            &scaler_rec,
            FT_LOAD_NO_BITMAP,
            char_index,
            &glyph,
            NULL
        )) {
            return NULL;
        }

        FT_Glyph_Stroke(&glyph, stroker, 1);
        FT_Vector origin = {0, 0};
        FT_Glyph_To_Bitmap(&glyph, FT_RENDER_MODE_NORMAL, &origin, 1);

        FT_BitmapGlyph bitmap_glyph = (FT_BitmapGlyph)glyph;

        if ( bitmap_glyph->bitmap.pixel_mode != FT_PIXEL_MODE_GRAY) {
            PyErr_SetString(PyExc_TypeError, "Only Greyscale Pixel Format Supported");
            return NULL;
        }

        PyObject* args = Py_BuildValue(
                                        "(iiiiiiiiiO)",
                                        bitmap_glyph->bitmap.width, bitmap_glyph->bitmap.rows,
                                        bitmap_glyph->left, bitmap_glyph->top,
                                        0, bitmap_glyph->bitmap.num_grays,
                                        bitmap_glyph->bitmap.pitch,
                                        PIXEL(glyph->advance.x), PIXEL(glyph->advance.y),
                                        PyMemoryView_FromMemory( (char*) bitmap_glyph->bitmap.buffer, bitmap_glyph->bitmap.pitch * bitmap_glyph->bitmap.rows, PyBUF_READ)
                                       );

        PyObject* result = PyObject_CallObject( cb, args);
        Py_DECREF(args);
        if (result == NULL) {
                return NULL;
        }
    }

    FT_Stroker_Done(stroker);
    Py_INCREF(Py_None);
    return Py_None;
}



static PyObject* method_render_string(PyObject* self, PyObject* args) {

    PyObject* Cbitcache;
    PyObject* Cmanager;
    PyObject* string;
    PyObject* cb;
    FT_UInt width, height;
    long int faceId;

    if (!PyArg_ParseTuple(args, "OOliiOO", &Cmanager, &Cbitcache, &faceId, &width, &height, &string, &cb)) {
        return NULL;
    }

    FTC_Manager manager = FTC_Manager_FromCapsule(Cmanager);
    FTC_SBitCache bitcache = FTC_SBitCache_FromCapsule(Cbitcache);

    FT_Face face;
    FTC_Manager_LookupFace(manager, (FTC_FaceID) faceId, &face);

    FTC_ScalerRec scaler_rec = {
        .face_id = (FTC_FaceID) faceId,
        .width = width,
        .height = height,
        .pixel = 1,
        .x_res = 0,
        .y_res = 0,
    };

    Py_UCS4 current_char;
    FT_UInt char_index;
    FTC_Node node; // pass this in so glyph is cached, and we'll never Unref it - so its there forever
    FTC_SBit sbit;
    FT_ULong load_flags = FT_LOAD_DEFAULT;

    Py_ssize_t length = PyUnicode_GET_LENGTH(string);
    for (int i = 0 ; i < length; i++ ) {
        current_char = PyUnicode_READ_CHAR(string, i);
        char_index = FT_Get_Char_Index(face, current_char);

        if ( FTC_SBitCache_LookupScaler(bitcache, &scaler_rec, load_flags, char_index, &sbit, &node) != 0) {
            PyErr_SetString(PyExc_TypeError, "unable to lookup a glyph");
            return NULL;
        }

        PyObject* args = Py_BuildValue(
                                        "(iiiiiiiiiO)",
                                        sbit->width, sbit->height, sbit->left, sbit->top,
                                        sbit->format, sbit->max_grays,
                                        sbit->pitch,
                                        sbit->xadvance, sbit->yadvance,
                                        PyMemoryView_FromMemory( (char*) sbit->buffer, sbit->pitch * sbit->height, PyBUF_READ)
                                        );
        PyObject* result = PyObject_CallObject( cb, args);
        Py_DECREF(args);

        if (result == NULL) {
                return NULL;
        }
    }

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
    {"image_cache_new", method_imagecache_new, METH_VARARGS, "New Image Cache"},
    {"bit_cache_new", method_bitcache_new, METH_VARARGS, "New SBit Cache"},
    {"cmap_cache_new", method_cmapcache_new, METH_VARARGS, "New CMap Cache"},
    {"render_string", method_render_string, METH_VARARGS, "Render String"},
    {"render_string_stroker", method_render_string_stroker, METH_VARARGS, "Render String with Stroker"},
    {"blit_glyph", method_blit_glyph, METH_VARARGS, "Blit Glyph Bitmap into image"},

    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_freetype",
    "dunno",
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