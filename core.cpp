// src/core.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <vector>
#include <string>
#include <cmath>
#include <unordered_map>
#include <algorithm>
#include <cstdint>

#include <immintrin.h> // AVX2

namespace py = pybind11;

/*
========================================================
CONFIGURAÇÃO GLOBAL
========================================================
*/
using QuantT = int8_t;
constexpr float QUANT_SCALE = 127.0f;

/*
========================================================
ESTRUTURAS
========================================================
*/
struct Verdict {
    bool is_conflict;
    std::string winner_source;
    float intensity;
    std::unordered_map<std::string, float> source_scores;
    std::string explanation;
    std::unordered_map<std::string, bool> manipulation_flags;
};

/*
========================================================
QUANTIZAÇÃO
========================================================
*/
inline std::vector<QuantT> quantize(const std::vector<float>& v) {
    std::vector<QuantT> q(v.size());
    for (size_t i = 0; i < v.size(); ++i) {
        float x = std::max(-1.0f, std::min(1.0f, v[i]));
        q[i] = static_cast<QuantT>(std::round(x * QUANT_SCALE));
    }
    return q;
}

/*
========================================================
DOT PRODUCT INT8 + AVX2
========================================================
*/
inline int32_t dot_product_int8_avx2(
    const std::vector<QuantT>& a,
    const std::vector<QuantT>& b)
{
    const size_t n = a.size();
    size_t i = 0;

    __m256i acc = _mm256_setzero_si256();

    for (; i + 31 < n; i += 32) {
        __m256i va = _mm256_loadu_si256((__m256i const*)(a.data() + i));
        __m256i vb = _mm256_loadu_si256((__m256i const*)(b.data() + i));

        __m256i madd = _mm256_maddubs_epi16(va, vb);
        __m256i sum32 = _mm256_madd_epi16(madd, _mm256_set1_epi16(1));

        acc = _mm256_add_epi32(acc, sum32);
    }

    alignas(32) int32_t buffer[8];
    _mm256_store_si256((__m256i*)buffer, acc);

    int32_t sum = buffer[0] + buffer[1] + buffer[2] + buffer[3]
                + buffer[4] + buffer[5] + buffer[6] + buffer[7];

    // tail
    for (; i < n; ++i)
        sum += static_cast<int32_t>(a[i]) * static_cast<int32_t>(b[i]);

    return sum;
}

/*
========================================================
NORMA L2 (INT8)
========================================================
*/
inline float l2_norm_int8(const std::vector<QuantT>& v) {
    int32_t sum = 0;
    for (QuantT x : v)
        sum += x * x;
    return std::sqrt(static_cast<float>(sum));
}

/*
========================================================
COSINE SIMILARITY INT8
========================================================
*/
inline float cosine_similarity_int8(
    const std::vector<QuantT>& a,
    const std::vector<QuantT>& b)
{
    const float denom = l2_norm_int8(a) * l2_norm_int8(b);
    if (denom == 0.0f) return 0.0f;

    float dot = static_cast<float>(dot_product_int8_avx2(a, b));
    return dot / denom;
}

/*
========================================================
ENGINE PRINCIPAL
========================================================
*/
class HoraculoEngine {
public:
    HoraculoEngine(float copy_threshold = 0.92f)
        : copy_threshold_(copy_threshold) {}

    std::vector<Verdict> analyze_batch(
        const std::vector<std::vector<float>>& embeddings,
        const std::vector<std::string>& sources)
    {
        const size_t n = embeddings.size();
        std::vector<Verdict> results(n);

        // Quantiza tudo uma vez
        std::vector<std::vector<QuantT>> q_embeddings;
        q_embeddings.reserve(n);
        for (const auto& e : embeddings)
            q_embeddings.push_back(quantize(e));

        for (size_t i = 0; i < n; ++i) {
            Verdict v{};
            v.is_conflict = false;
            v.intensity = 0.0f;
            v.winner_source = sources[i];

            for (size_t j = 0; j < n; ++j) {
                if (i == j) continue;

                float sim = cosine_similarity_int8(
                    q_embeddings[i],
                    q_embeddings[j]
                );

                v.source_scores[sources[j]] = sim;

                if (sim >= copy_threshold_) {
                    v.is_conflict = true;
                    v.intensity = std::max(v.intensity, sim);
                }
            }

            v.explanation = v.is_conflict
                ? "INT8 AVX2 semantic overlap detected."
                : "No significant semantic conflict detected.";

            results[i] = std::move(v);
        }

        return results;
    }

private:
    float copy_threshold_;
};

/*
========================================================
PYTHON BINDINGS
========================================================
*/
PYBIND11_MODULE(core, m) {
    py::class_<Verdict>(m, "Verdict")
        .def_readonly("is_conflict", &Verdict::is_conflict)
        .def_readonly("winner_source", &Verdict::winner_source)
        .def_readonly("intensity", &Verdict::intensity)
        .def_readonly("source_scores", &Verdict::source_scores)
        .def_readonly("explanation", &Verdict::explanation)
        .def_readonly("manipulation_flags", &Verdict::manipulation_flags);

    py::class_<HoraculoEngine>(m, "HoraculoEngine")
        .def(py::init<float>(),
             py::arg("copy_threshold") = 0.92f)
        .def("analyze_batch",
             &HoraculoEngine::analyze_batch,
             py::call_guard<py::gil_scoped_release>());

    m.doc() = "Horaculo V2 core engine — INT8 + AVX2 ultra optimized";
}
