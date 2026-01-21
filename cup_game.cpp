#include <bits/stdc++.h>
using namespace std;

// Pack each cell in 'bits' bits inside uint64_t.
// Works well for n <= floor(64 / bits). For bits=6, n<=10 in 64-bit,
// so we’ll use unsigned __int128 for more room, or store in two uint64s.
// Simpler: use std::vector<uint8_t> as key with hashing? Slower.
// Best practical: use boost::multiprecision::cpp_int, but hashing is heavier.
//
// Here: we'll use uint64_t but allow bits=4 and n<=16, OR you can switch to __int128.

static const int BITS = 6;
static const uint64_t MASK = (1ULL << BITS) - 1;

inline uint64_t get_cell(uint64_t s, int i) {
    return (s >> (i * BITS)) & MASK;
}
inline uint64_t set_cell(uint64_t s, int i, uint64_t v) {
    uint64_t shift = (uint64_t)i * BITS;
    s &= ~(MASK << shift);
    s |= (v & MASK) << shift;
    return s;
}

uint64_t reflect_state(uint64_t s, int n) {
    uint64_t r = 0;
    for (int i = 0; i < n; i++) {
        uint64_t v = get_cell(s, i);
        r = set_cell(r, n - 1 - i, v);
    }
    return r;
}
uint64_t canon(uint64_t s, int n) {
    uint64_t r = reflect_state(s, n);
    return min(s, r);
}

struct Hasher {
    size_t operator()(uint64_t x) const noexcept {
        // splitmix64
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return (size_t)(x ^ (x >> 31));
    }
};

struct Solver {
    int n;
    unordered_map<uint64_t, bool, Hasher> memo;

    bool winning(uint64_t s) {
        auto it = memo.find(s);
        if (it != memo.end()) return it->second;

        for (int i = 0; i < n; i++) {
            uint64_t k = get_cell(s, i);
            if (k == 0) continue;

            int j = i - (int)k;
            if (j >= 0) {
                uint64_t dest = get_cell(s, j);
                if (dest != 0) {
                    uint64_t ns = s;
                    ns = set_cell(ns, i, 0);
                    ns = set_cell(ns, j, dest + k);
                    ns = canon(ns, n);
                    if (!winning(ns)) {
                        memo[s] = true;
                        return true;
                    }
                }
            }
            j = i + (int)k;
            if (j < n) {
                uint64_t dest = get_cell(s, j);
                if (dest != 0) {
                    uint64_t ns = s;
                    ns = set_cell(ns, i, 0);
                    ns = set_cell(ns, j, dest + k);
                    ns = canon(ns, n);
                    if (!winning(ns)) {
                        memo[s] = true;
                        return true;
                    }
                }
            }
        }

        memo[s] = false;
        return false;
    }
};

uint64_t start_state(int n) {
    uint64_t s = 0;
    for (int i = 0; i < n; i++) {
        s |= (1ULL << (i * BITS));
    }
    return s;
}

int main() {
    int N = 20;
    for (int n = 1; n <= N; n++) {
        // NOTE: with BITS=6 in uint64, max n is floor(64/6)=10.
        // If you want n>10, either reduce BITS or switch to __int128 / two-word packing.
        if (n > (int)(64 / BITS)) {
            cerr << "n=" << n << " exceeds packing limit for uint64 with BITS=" << BITS << "\n";
            break;
        }

        Solver sol;
        sol.n = n;
        sol.memo.reserve(1 << 20);

        uint64_t s = canon(start_state(n), n);
        bool w = sol.winning(s);
        cout << n << " " << (w ? "First" : "Second") << " (states " << sol.memo.size() << ")\n";
    }
}
