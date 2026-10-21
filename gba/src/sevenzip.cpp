// (AI-assisted) Safe in-memory 7z loader for GBA. Uses mGBA's bundled public-domain LZMA SDK.
// SPDX-License-Identifier: GPL-3.0-or-later
#include "sevenzip.h"
#include "third-party/lzma/7z.h"
#include "third-party/lzma/7zCrc.h"
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>

namespace gba {
namespace {
constexpr size_t kMaxRom = 32u << 20;
constexpr uint64_t kMaxSolidBlock = 64u << 20;
constexpr size_t kMaxMainAlloc = 160u << 20;
constexpr size_t kMaxTempAlloc = 64u << 20;
constexpr uint8_t kSignature[] = {0x37, 0x7a, 0xbc, 0xaf, 0x27, 0x1c};

// 7z needs a seekable stream. ReadRom has already read local/USB/NFS input,
// so presenting the same bounded memory buffer avoids temporary files.
struct MemoryStream {
    ILookInStream vt{};
    const uint8_t* bytes = nullptr;
    size_t length = 0;
    size_t at = 0;

    explicit MemoryStream(const std::vector<uint8_t>& data) : bytes(data.data()), length(data.size()) {
        vt.Look = Look; vt.Skip = Skip; vt.Read = Read; vt.Seek = Seek;
    }
    static MemoryStream* Self(const ILookInStream* p) {
        return reinterpret_cast<MemoryStream*>(const_cast<ILookInStream*>(p));
    }
    static SRes Look(const ILookInStream* p, const void** out, size_t* count) {
        auto* s = Self(p);
        *count = std::min(*count, s->length - s->at);
        *out = s->bytes + s->at;
        return SZ_OK;
    }
    static SRes Skip(const ILookInStream* p, size_t count) {
        auto* s = Self(p);
        if (count > s->length - s->at) return SZ_ERROR_INPUT_EOF;
        s->at += count;
        return SZ_OK;
    }
    static SRes Read(const ILookInStream* p, void* out, size_t* count) {
        auto* s = Self(p);
        *count = std::min(*count, s->length - s->at);
        if (*count) std::memcpy(out, s->bytes + s->at, *count);
        s->at += *count;
        return SZ_OK;
    }
    static SRes Seek(const ILookInStream* p, Int64* position, ESzSeek origin) {
        auto* s = Self(p);
        const int64_t base = origin == SZ_SEEK_SET ? 0 :
            origin == SZ_SEEK_CUR ? static_cast<int64_t>(s->at) :
            origin == SZ_SEEK_END ? static_cast<int64_t>(s->length) : -1;
        if (base < 0 || *position < -base ||
            *position > static_cast<int64_t>(s->length) - base)
            return SZ_ERROR_READ;
        s->at = static_cast<size_t>(base + *position);
        *position = static_cast<Int64>(s->at);
        return SZ_OK;
    }
};

// A damaged archive can advertise a huge dictionary or metadata allocation.
// Account for all allocations, including ones made during SzArEx_Open.
struct BudgetAllocator {
    ISzAlloc vt{};
    size_t used = 0;
    size_t maximum = 0;
    struct alignas(std::max_align_t) Header { size_t bytes; };

    explicit BudgetAllocator(size_t limit) : maximum(limit) {
        vt.Alloc = Allocate; vt.Free = Release;
    }
    static BudgetAllocator* Self(ISzAllocPtr p) {
        return reinterpret_cast<BudgetAllocator*>(const_cast<ISzAlloc*>(p));
    }
    static void* Allocate(ISzAllocPtr p, size_t count) {
        auto* a = Self(p);
        if (!count) count = 1;
        if (count > a->maximum - a->used ||
            count > std::numeric_limits<size_t>::max() - sizeof(Header))
            return nullptr;
        auto* ptr = static_cast<Header*>(std::malloc(sizeof(Header) + count));
        if (!ptr) return nullptr;
        ptr->bytes = count;
        a->used += count;
        return ptr + 1;
    }
    static void Release(ISzAllocPtr p, void* address) {
        if (!address) return;
        auto* a = Self(p);
        auto* ptr = static_cast<Header*>(address) - 1;
        a->used -= ptr->bytes;
        std::free(ptr);
    }
};

bool IsGbaFilename(const CSzArEx& archive, UInt32 index) {
    const size_t size = SzArEx_GetFileNameUtf16(&archive, index, nullptr);
    if (size < 5 || size > 4096) return false; // includes terminating 0
    // Check suffix directly in UTF-16: no allocation or path extraction needed.
    // Read the actual UTF-16 text; no paths are written to disk.
    std::vector<UInt16> name(size);
    SzArEx_GetFileNameUtf16(&archive, index, name.data());
    if (name[size - 1] != 0) return false;
    const auto lower = [](UInt16 ch) { return ch >= 'A' && ch <= 'Z' ? ch + 32 : int(ch); };
    return name[size - 5] == '.' && lower(name[size - 4]) == 'g' &&
           lower(name[size - 3]) == 'b' && lower(name[size - 2]) == 'a';
}

const char* DecodeError(SRes error) {
    switch (error) {
    case SZ_ERROR_UNSUPPORTED: return "Unsupported or encrypted 7z compression";
    case SZ_ERROR_CRC: return "7z checksum failed";
    case SZ_ERROR_MEM: return "7z memory limit exceeded";
    case SZ_ERROR_INPUT_EOF: return "Truncated 7z archive";
    default: return "Invalid or corrupted 7z archive";
    }
}
} // namespace

bool Unsevenzip(const std::vector<uint8_t>& archive, std::vector<uint8_t>& rom, std::string& error) {
    rom.clear();
    if (archive.size() < 32 ||
        std::memcmp(archive.data(), kSignature, sizeof(kSignature)) != 0) {
        error = "Invalid 7z signature";
        return false;
    }
    MemoryStream stream(archive);
    BudgetAllocator main(kMaxMainAlloc), temporary(kMaxTempAlloc);
    CSzArEx db;
    SzArEx_Init(&db);
    CrcGenerateTable();
    SRes result = SzArEx_Open(&db, &stream.vt, &main.vt, &temporary.vt);
    if (result != SZ_OK) {
        error = DecodeError(result);
        SzArEx_Free(&db, &main.vt);
        return false;
    }

    UInt32 chosen = db.NumFiles;
    unsigned matches = 0;
    for (UInt32 i = 0; i < db.NumFiles; ++i) {
        if (SzArEx_IsDir(&db, i) || !IsGbaFilename(db, i)) continue;
        chosen = i;
        ++matches;
        if (matches > 1) break;
    }

    if (matches != 1) {
        error = matches ? "7z contains multiple GBA ROMs - use one per archive" :
                          "7z contains no GBA ROM";
        SzArEx_Free(&db, &main.vt);
        return false;
    }

    const UInt64 rom_size = SzArEx_GetFileSize(&db, chosen);
    if (rom_size < 192 || rom_size > kMaxRom) {
        error = "7z ROM is outside the 192-byte to 32-MiB limit";
        SzArEx_Free(&db, &main.vt);
        return false;
    }
    const UInt32 folder = db.FileToFolder[chosen];
    if (folder >= db.db.NumFolders ||
        SzAr_GetFolderUnpackSize(&db.db, folder) > kMaxSolidBlock) {
        error = "7z solid folder exceeds the 64-MiB safety limit";
        SzArEx_Free(&db, &main.vt);
        return false;
    }

    UInt32 block_index = 0xFFFFFFFF;
    Byte* buffer = nullptr;
    size_t buffer_size = 0, offset = 0, decoded_size = 0;
    result = SzArEx_Extract(&db, &stream.vt, chosen, &block_index,
                           &buffer, &buffer_size, &offset, &decoded_size,
                           &main.vt, &temporary.vt);
    if (result == SZ_OK && decoded_size == rom_size &&
        offset <= buffer_size && decoded_size <= buffer_size - offset) {
        rom.assign(buffer + offset, buffer + offset + decoded_size);
    } else {
        error = result == SZ_OK ? "7z decoded size mismatch" : DecodeError(result);
    }
    BudgetAllocator::Release(&main.vt, buffer);
    SzArEx_Free(&db, &main.vt);
    if (rom.empty()) return false;
    error.clear();
    return true;
}

} // namespace gba
