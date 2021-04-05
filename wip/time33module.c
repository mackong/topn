#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *
time33_hash(PyObject *self, PyObject *args)
{
    const char *s;
    long hash = 5381L;

    if (!PyArg_ParseTuple(args, "s", &s))
        return NULL;

    while (*s) {
        hash += (hash << 5) + *s;
        s++;
    }

    return PyLong_FromLong(hash);
}

static PyMethodDef Time33Methods[] = {
    {"hash",  time33_hash, METH_VARARGS, "Hash a string in time33"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef time33module = {
    PyModuleDef_HEAD_INIT,
    "time33",
    NULL,
    -1,
    Time33Methods
};

PyMODINIT_FUNC
PyInit_time33(void)
{
    return PyModule_Create(&time33module);
}
