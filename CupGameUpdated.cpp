#include <bits/stdc++.h>
using namespace std;

static const int BITS = 6;
static const uint64_t MASK = (1ULL << BITS) - 1;
static const int WORDS = 3; // supports n up to floor(192/6)=32

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
    for (int i = 0; i < n; ++i) set_cell(r, n - 1 - i, get_cell(s, i));
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

    // progress tracking
    uint64_t calls = 0;
    chrono::steady_clock::time_point t0 = chrono::steady_clock::now();
    chrono::steady_clock::time_point last = t0;
    uint64_t last_calls = 0;

    void maybe_report() {
        auto now = chrono::steady_clock::now();
        auto dt = chrono::duration_cast<chrono::milliseconds>(now - last).count();
        if (dt >= 1000) {
            double elapsed = chrono::duration<double>(now - t0).count();
            double cps = (calls - last_calls) / (dt / 1000.0);
            cerr << fixed << setprecision(2)
                 << "[t=" << elapsed << "s] "
                 << "memo=" << memo.size()
                 << " calls=" << calls
                 << " calls/s~" << cps
                 << "\n";
            cerr.flush();
            last = now;
            last_calls = calls;
        }
    }

    bool winning(State const& s) {
        ++calls;
        if ((calls & 0x3FFFF) == 0) maybe_report(); // every ~262k calls

        auto it = memo.find(s);
        if (it != memo.end()) return it->second;

        // Move ordering heuristic: try moves that create larger destination stacks first.
        // This often finds a winning move sooner and prunes the search.
        struct Move { int i, j; uint64_t k, dest; };
        vector<Move> cand;
        cand.reserve(16);

        for (int i = 0; i < n; ++i) {
            uint64_t k = get_cell(s, i);
            if (k == 0) continue;

            int j = i - (int)k;
            if (j >= 0) {
                uint64_t dest = get_cell(s, j);
                if (dest != 0) cand.push_back({i, j, k, dest});
            }
            j = i + (int)k;
            if (j < n) {
                uint64_t dest = get_cell(s, j);
                if (dest != 0) cand.push_back({i, j, k, dest});
            }
        }

        if (cand.empty()) {
            memo.emplace(s, false);
            return false;
        }

        sort(cand.begin(), cand.end(), [](const Move& a, const Move& b){
            return (a.dest + a.k) > (b.dest + b.k);
        });

        for (auto &mv : cand) {
            State ns = s;
            set_cell(ns, mv.i, 0);
            set_cell(ns, mv.j, mv.dest + mv.k);
            ns = canon(ns, n);
            if (!winning(ns)) {
                memo.emplace(s, true);
                return true;
            }
        }

        memo.emplace(s, false);
        return false;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n = 19;
    int maxN = (64 * WORDS) / BITS;
    if (n > maxN) {
        cerr << "n=" << n << " exceeds maxN=" << maxN << " for WORDS=" << WORDS << "\n";
        return 1;
    }

    cerr << "Starting solve for n=" << n
         << " (BITS=" << BITS << ", WORDS=" << WORDS << ")...\n";
    cerr.flush();

    Solver sol;
    sol.n = n;
    sol.memo.reserve(10'000'000); // may help avoid rehashing

    State start = canon(start_state(n), n);

    bool w = sol.winning(start);
    auto t1 = chrono::steady_clock::now();
    double elapsed = chrono::duration<double>(t1 - sol.t0).count();

    cout << "n=" << n << " => " << (w ? "First wins" : "Second wins")
         << " (states=" << sol.memo.size()
         << ", calls=" << sol.calls
         << ", time=" << fixed << setprecision(2) << elapsed << "s)\n";
}
