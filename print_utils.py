import numpy as _np

EPS = 1e-12

def format_num(x, eps=EPS):
    v = 0.0 if abs(x) < eps else x
    return f"{v:.2e}"

def format_array(arr, eps=EPS):
    try:
        return _np.array2string(_np.asarray(arr), formatter={'float_kind': lambda x: format_num(x, eps)})
    except Exception:
        return str(arr)
