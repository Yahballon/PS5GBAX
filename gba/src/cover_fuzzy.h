// (AI-assisted) Conservative fuzzy matching for indexed Libretro GBA artwork.
// Approximate names are accepted only when the best distinct title is unambiguous.
// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <algorithm>
#include <cstddef>
#include <cstdlib>
#include <string>
#include <utility>
#include <vector>

namespace gba {

struct CoverFuzzyResult {
    std::string key;
    int score = -1;         // 0..1000, higher = closer
    int runner_up = -1;     // strongest DIFFERENT title, not another region
};

// Never confuse sequels: "Advance 2" must not match "Advance 3".
// Also avoids guessing an unnumbered original for a numbered sequel.
inline std::vector<std::string> CoverDigits(const std::string& s) {
    std::vector<std::string> groups;
    for (size_t i = 0; i < s.size();) {
        if (s[i] < '0' || s[i] > '9') { ++i; continue; }
        size_t end = i + 1;
        while (end < s.size() && s[end] >= '0' && s[end] <= '9') ++end;
        groups.push_back(s.substr(i, end - i));
        i = end;
    }
    return groups;
}

// Bounded Levenshtein, with early exit. No regex allocation and no
// comparison of full cover filenames with region/language metadata.
inline int CoverEditDistance(const std::string& a, const std::string& b, int limit) {
    if (std::abs(int(a.size()) - int(b.size())) > limit) return limit + 1;
    std::vector<int> previous(b.size() + 1), current(b.size() + 1);
    for (size_t j = 0; j <= b.size(); ++j) previous[j] = int(j);
    for (size_t i = 1; i <= a.size(); ++i) {
        current[0] = int(i);
        int min_row = current[0];
        for (size_t j = 1; j <= b.size(); ++j) {
            current[j] = std::min({previous[j] + 1, current[j - 1] + 1,
                                   previous[j - 1] + (a[i - 1] == b[j - 1] ? 0 : 1)});
            min_row = std::min(min_row, current[j]);
        }
        if (min_row > limit) return limit + 1;
        previous.swap(current);
    }
    return previous[b.size()];
}

inline int CoverFuzzyScore(const std::string& wanted, const std::string& candidate) {
    if (wanted.size() < 8 || candidate.size() < 8 ||
        wanted.size() > 110 || candidate.size() > 110)
        return -1;
    if (CoverDigits(wanted) != CoverDigits(candidate)) return -1;

    // Partial prefix match: helps truncated dump names, provided it is
    // sufficiently specific and no other distinct indexed title is close.
    // A prefix of only "Sonic Advance" is deliberately too generic.
    if (wanted.size() >= 14 && candidate.size() > wanted.size() &&
        candidate.compare(0, wanted.size(), wanted) == 0 &&
        candidate.size() <= wanted.size() * 2 + 4) {
        return 840 + int(80 * wanted.size() / candidate.size());
    }

    const int longest = int(std::max(wanted.size(), candidate.size()));
    const int limit = longest / 5; // up to 20% edits; mostly spelling/spacing
    const int distance = CoverEditDistance(wanted, candidate, limit);
    if (distance > limit) return -1;
    const int score = 1000 - (1000 * distance) / longest;
    return score >= 840 ? score : -1;
}

template<typename Entry>
CoverFuzzyResult CoverBestFuzzyKey(const std::string& wanted, const Entry* names, size_t count) {
    std::vector<std::pair<int, std::string>> candidates;
    std::string last_key;
    for (size_t i = 0; i < count; ++i) {
        // Multiple USA/Europe/Japan image files often share one title key.
        const std::string key = names[i].key;
        if (key == last_key) continue;
        last_key = key;
        const int score = CoverFuzzyScore(wanted, key);
        if (score < 840) continue;
        auto it = std::find_if(candidates.begin(), candidates.end(),
                               [&](const auto& candidate) { return candidate.second == key; });
        if (it == candidates.end()) candidates.emplace_back(score, key);
    }
    std::sort(candidates.begin(), candidates.end(), [](const auto& a, const auto& b) {
        return a.first != b.first ? a.first > b.first : a.second < b.second;
    });
    CoverFuzzyResult result;
    if (candidates.empty()) return result;
    result.score = candidates.front().first;
    result.runner_up = candidates.size() >= 2 ? candidates[1].first : -1;
    // Only choose when the next distinct *game title* is clearly worse.
    // Covers with different regions of the same game do not count as rivals.
    if (result.runner_up < 0 || result.score - result.runner_up >= 55)
        result.key = candidates.front().second;
    return result;
}
} // namespace gba
