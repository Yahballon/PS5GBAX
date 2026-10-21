// (AI-assisted) Bounded 7z-to-RAM decoder using the 7-Zip SDK already vendored with mGBA.
// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace gba {
// Decodes exactly one .gba entry. No files are written to disk.
bool Unsevenzip(const std::vector<uint8_t>& archive, std::vector<uint8_t>& rom, std::string& error);
}
