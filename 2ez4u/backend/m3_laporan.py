import time

def get_key_val(item, key):
    if key == "harga":
        return item.harga
    if key == "oid":
        return item.oid
    if key in ("selesai", "t_selesai_detik"):
        return item.t_selesai_detik
    if key in ("masuk", "t_masuk_detik"):
        return item.t_masuk_detik
    if key == "prioritas":
        return item.prioritas
    if hasattr(item, key):
        return getattr(item, key)
    return 0


def insertion_sort(arr, key="harga"):
    n = len(arr)
    if n > 20000:
        return None, 0, 0, 0.0, "DITOLAK: batasnya 20.000 baris, pakai merge sort untuk data penuh"

    t0 = time.perf_counter()
    a = list(arr)
    comparisons = 0
    shifts = 0

    for i in range(1, n):
        cur = a[i]
        cur_k = get_key_val(cur, key)
        j = i - 1
        while j >= 0:
            comparisons += 1
            if get_key_val(a[j], key) > cur_k:
                a[j + 1] = a[j]
                shifts += 1
                j -= 1
            else:
                break
        a[j + 1] = cur
        shifts += 1

    durasi_ms = (time.perf_counter() - t0) * 1000
    return a, comparisons, shifts, durasi_ms, None


def merge_sort(arr, key="harga"):
    t0 = time.perf_counter()
    a = list(arr)
    comparisons = [0]
    shifts = [0]

    def _sort(lst):
        if len(lst) <= 1:
            return lst
        mid = len(lst) // 2
        left = _sort(lst[:mid])
        right = _sort(lst[mid:])
        return _merge(left, right)

    def _merge(left, right):
        res = []
        i = j = 0
        n_l, n_r = len(left), len(right)
        while i < n_l and j < n_r:
            comparisons[0] += 1
            if get_key_val(left[i], key) <= get_key_val(right[j], key):
                res.append(left[i])
                shifts[0] += 1
                i += 1
            else:
                res.append(right[j])
                shifts[0] += 1
                j += 1
        while i < n_l:
            res.append(left[i])
            shifts[0] += 1
            i += 1
        while j < n_r:
            res.append(right[j])
            shifts[0] += 1
            j += 1
        return res

    res = _sort(a)
    durasi_ms = (time.perf_counter() - t0) * 1000
    return res, comparisons[0], shifts[0], durasi_ms, None


def linear_search(arr, target_oid):
    t0 = time.perf_counter()
    comparisons = 0
    for idx, item in enumerate(arr):
        comparisons += 1
        if item.oid == target_oid:
            durasi_ms = (time.perf_counter() - t0) * 1000
            return idx, comparisons, durasi_ms

    durasi_ms = (time.perf_counter() - t0) * 1000
    return -1, comparisons, durasi_ms


def binary_search(arr, target_oid):
    t0 = time.perf_counter()
    comparisons = 0
    lo = 0
    hi = len(arr) - 1

    while lo <= hi:
        mid = (lo + hi) // 2
        comparisons += 1
        if arr[mid].oid == target_oid:
            durasi_ms = (time.perf_counter() - t0) * 1000
            return mid, comparisons, durasi_ms
        elif arr[mid].oid < target_oid:
            lo = mid + 1
        else:
            hi = mid - 1

    durasi_ms = (time.perf_counter() - t0) * 1000
    return -1, comparisons, durasi_ms
