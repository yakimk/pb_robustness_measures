from fractions import Fraction
from math import comb
from pb_robustness_measures.rules.greedyAV import greedy_av

from fractions import Fraction
from math import comb
from functools import lru_cache

@lru_cache(maxsize=None)
def get_ways_tuple(s, max_c):
    if max_c < 0:
        return tuple()
    ways = [0] * (max_c + 1)
    ways[0] = 1
    for c in range(1, max_c + 1):
        ways[c] = ways[c - 1] * (s + c - 1) // c
    return tuple(ways)

def convolve_truncate(a, b, maxdeg):
    """
    Truncated convolution of lists a and b up to degree maxdeg inclusive.
    """
    n = maxdeg + 1
    c = [0] * n
    nz_a = [i for i, v in enumerate(a) if v != 0]
    nz_b = [j for j, v in enumerate(b) if v != 0]
    for i in nz_a:
        ai = a[i]
        bj_list = nz_b
        for j in bj_list:
            t = i + j
            if t > maxdeg:
                break
            c[t] += ai * b[j]
    return c

def multiply_polys_tree(polys, maxdeg):
    """
    Multiply list `polys` (each a list of ints) truncated to degree maxdeg.
    Uses balanced pairwise multiplication to reduce work compared to sequential multiply.
    Returns list length maxdeg+1.
    """
    if not polys:
        return [1] + [0] * maxdeg
    # copy (and ensure internal lengths at least maxdeg+1)
    cur = [p[:maxdeg + 1] if len(p) > maxdeg + 1 else p[:] + [0] * (maxdeg + 1 - len(p)) for p in polys]
    while len(cur) > 1:
        nxt = []
        it = iter(cur)
        for a in it:
            try:
                b = next(it)
            except StopIteration:
                nxt.append(a[:maxdeg + 1])
            else:
                nxt.append(convolve_truncate(a, b, maxdeg))
        cur = nxt
    return cur[0][:maxdeg + 1]

def count_with_supporters_fast(n, s_list, m, K_set):
    k = len(K_set)
    if k == 0:
        return 0
    if k == n:
        return 0

    r = n - k
    M_max = m // k - 1
    if M_max < 0:
        return 0

    # Precompute (memoized) ways polynomials for each unique s up to degree m
    # Represent ways_i as tuple for immutability and cache friendliness
    unique_s = sorted(set(s_list))
    ways_by_s = {s: get_ways_tuple(s, m) for s in unique_s}
    # Map project -> ways tuple
    ways = [ways_by_s[s_list[i]] for i in range(n)]

    total = 0

    # Precompute lists of loser indices and winner indices
    losers = [j for j in range(n) if j not in K_set]
    winners = [i for i in range(n) if i in K_set]

    for M in range(M_max + 1):
        T_min = M
        T_max = min(r * M, m - k * (M + 1))
        if T_max < T_min:
            continue

        # Build polynomials for losers:
        # each loser poly is ways_j truncated to c <= M and degree limited to T_max
        polys_non_M = []
        polys_non_Mminus = []
        for j in losers:
            w = ways[j]  # tuple of length m+1
            # Tj_M (coeffs 0..T_max) keeping only c<=M
            Tj_M = [w[c] if c <= M and c <= T_max else 0 for c in range(T_max + 1)]
            polys_non_M.append(Tj_M)
            if M == 0:
                # all zeros for <=M-1
                polys_non_Mminus.append([0] * (T_max + 1))
            else:
                Tj_Mm1 = [w[c] if c <= M - 1 and c <= T_max else 0 for c in range(T_max + 1)]
                polys_non_Mminus.append(Tj_Mm1)

        # Multiply loser polynomials with balanced product tree
        poly_non_M = multiply_polys_tree(polys_non_M, T_max)
        poly_non_Mminus = multiply_polys_tree(polys_non_Mminus, T_max)
        # poly_diff = poly_non_M - poly_non_Mminus (componentwise)
        poly_diff = [poly_non_M[t] - poly_non_Mminus[t] for t in range(T_max + 1)]

        # Build winners
        polys_winners = []
        for i in winners:
            w = ways[i]
            Ri = [w[c] if c >= (M + 1) else 0 for c in range(m + 1)]
            polys_winners.append(Ri)

        # mult truncated polys to deg m
        polyK = multiply_polys_tree(polys_winners, m)

        for T in range(T_min, T_max + 1):
            S = m - T
            total += polyK[S] * poly_diff[T]

    return total


#wrapper
def plurality_sampling_robustness_measure(
    instance,
    profile,
    target=None,
    samples: int = 100,
):
    projects = list(instance)
    idx = {p: i for i, p in enumerate(projects)}

    if target is None:
        allocation = greedy_av(instance, profile)
        winners = set(allocation)
        K_set = {idx[p] for p in winners if p in idx}
    else:
        if target not in idx:
            raise ValueError("target project not in instance")
        K_set = {idx[target]}

    s_list = [int(profile.approval_score(p)) for p in projects]
    m = int(samples)
    if m < 0:
        raise ValueError("Number of samples must be non-negative")

    S = sum(s_list)
    if S == 0:
        return Fraction(0, 1)

    total_unordered_multisets = comb(S + m - 1, m)
    count_valid_multisets = count_with_supporters_fast(len(s_list), s_list, m, K_set)
    return Fraction(count_valid_multisets, total_unordered_multisets)
