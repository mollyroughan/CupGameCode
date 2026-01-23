#include <bits/stdc++.h>
using namespace std;

static const int BITS = 6;                       // stack sizes 0..63
static const uint64_t MASK = (1ULL << BITS) - 1; // 0x3F
static const int WORDS = 3;                      // 3*64 = 192 bits, supports n <= floor(192/6)=32

struct State {
    array<uint64_t, WORDS> w{};

    bool operator==(State const& o) const { return w == o.w; }

    bool operator<(State const& o) const {
        for (int i = WORDS - 1; i >= 0; --i) {
            if (w[i] != o.w[i]) return w[i] < o.w[i];
        }
        return false;
    }
};

struct StateHash {
    size_t operator()(State const& s) const noexcept {
        uint64_t x = 0x9e3779b97f4a7c15ULL;
        auto mix = [&](uint64_t v) {
            v += 0x9e3779b97f4a7c15ULL;
            v = (v ^ (v >> 30)) * 0xbf58476d1ce4e5b9ULL;
            v = (v ^ (v >> 27)) * 0x94d049bb133111ebULL;
            v ^= (v >> 31);
            x ^= v + 0x9e3779b97f4a7c15ULL + (x << 6) + (x >> 2);
        };
        for (int i = 0; i < WORDS; ++i) mix(s.w[i]);
        return (size_t)x;
    }
};

inline uint64_t get_cell(State const& s, int i) {
    int bit = i * BITS;
    int word = bit / 64;
    int off  = bit % 64;

    uint64_t lo = s.w[word] >> off;
    if (off <= 64 - BITS) {
        return lo & MASK;
    } else {
        // straddles into next word
        int hiBits = (off + BITS) - 64;
        uint64_t hi = (word + 1 < WORDS) ? (s.w[word + 1] & ((1ULL << hiBits) - 1)) : 0ULL;
        return ((hi << (64 - off)) | lo) & MASK;
    }
}

inline void set_cell(State& s, int i, uint64_t val) {
    int bit = i * BITS;
    int word = bit / 64;
    int off  = bit % 64;

    val &= MASK;

    if (off <= 64 - BITS) {
        uint64_t clearMask = ~(MASK << off);
        s.w[word] = (s.w[word] & clearMask) | (val << off);
    } else {
        int hiBits = (off + BITS) - 64;
        uint64_t lowBits = 64 - off;

        uint64_t lowMask  = ((1ULL << lowBits) - 1) << off;
        uint64_t highMask = (1ULL << hiBits) - 1;

        s.w[word] = (s.w[word] & ~lowMask) | ((val & ((1ULL << lowBits) - 1)) << off);
        if (word + 1 < WORDS) {
            s.w[word + 1] = (s.w[word + 1] & ~highMask) | (val >> lowBits);
        }
    }
}

State reflect_state(State const& s, int n) {
    State r;
    for (int i = 0; i < n; ++i) {
        set_cell(r, n - 1 - i, get_cell(s, i));
    }
    return r;
}

State canon(State const& s, int n) {
    State r = reflect_state(s, n);
    return (r < s) ? r : s;
}

State start_state(int n) {
    State s;
    for (int i = 0; i < n; ++i) set_cell(s, i, 1);
    return s;
}

struct Solver {
    int n;
    unordered_map<State, bool, StateHash> memo;

    bool winning(State const& s) {
        auto it = memo.find(s);
        if (it != memo.end()) return it->second;

        // Try moves; winning iff any move goes to a losing state.
        for (int i = 0; i < n; ++i) {
            uint64_t k = get_cell(s, i);
            if (k == 0) continue;

            // left
            int j = i - (int)k;
            if (j >= 0) {
                uint64_t dest = get_cell(s, j);
                if (dest != 0) {
                    State ns = s;
                    set_cell(ns, i, 0);
                    set_cell(ns, j, dest + k);
                    ns = canon(ns, n);
                    if (!winning(ns)) {
                        memo.emplace(s, true);
                        return true;
                    }
                }
            }

            // right
            j = i + (int)k;
            if (j < n) {
                uint64_t dest = get_cell(s, j);
                if (dest != 0) {
                    State ns = s;
                    set_cell(ns, i, 0);
                    set_cell(ns, j, dest + k);
                    ns = canon(ns, n);
                    if (!winning(ns)) {
                        memo.emplace(s, true);
                        return true;
                    }
                }
            }
        }

        memo.emplace(s, false);
        return false;
    }
};

int main() {
    int n = 25;
    int maxN = (64 * WORDS) / BITS;
    if (n > maxN) {
        cerr << "n=" << n << " exceeds maxN=" << maxN
             << " for WORDS=" << WORDS << " and BITS=" << BITS << "\n";
        return 1;
    }

    Solver sol;
    sol.n = n;
    sol.memo.reserve(5'000'000); // optional

    State start = canon(start_state(n), n);
    bool w = sol.winning(start);

    cout << "n=" << n << " => " << (w ? "First wins" : "Second wins")
         << " (states explored: " << sol.memo.size() << ")\n";
}
