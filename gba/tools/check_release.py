"""(AI-assisted) Check source-release hygiene without a PS5 SDK or compiler."""

import ast
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    errors = []
    # Include tracked files and new files that would be included by git add.
    output = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
        cwd=ROOT,
    )
    paths = sorted(set(output.decode('utf-8').split('\0')) - {''})
    private_extensions = {'.gba', '.gb', '.gbc', '.nds', '.sav', '.srm', '.pem', '.key'}
    for name in paths:
        path = ROOT / name
        if not path.is_file():
            errors.append(f'Missing source file: {name}')
            continue
        if path.stat().st_size >= 100 * 1024 * 1024:
            errors.append(f'File exceeds GitHub regular-file size limit: {name}')
        if path.suffix.lower() in private_extensions or path.name.startswith('.env'):
            errors.append(f'Private or user-data file in source candidates: {name}')
        if name.startswith(('gba/build', 'dist/')):
            errors.append(f'Generated output in source candidates: {name}')
        if name.startswith('gba/tools/') and path.suffix == '.py':
            try:
                ast.parse(path.read_text(encoding='utf-8'), filename=name)
            except (SyntaxError, UnicodeError) as exc:
                errors.append(f'Invalid Python source {name}: {exc}')

    required = [
        'LICENSE', 'COPYING.GPLv3', 'THIRD_PARTY_NOTICES.md',
        'gba/third_party/mgba/LICENSE', 'gba/third_party/mgba/UPSTREAM_REVISION.txt',
        'gba/sce_sys/icon0.png', 'gba/sce_sys/param.json', 'INSTALL.md',
        'BUILDING.md', 'TESTING.md', 'RELEASE_NOTES.md', 'RELEASING.md',
    ]
    for name in required:
        if name not in paths:
            errors.append(f'Required release source excluded or missing: {name}')

    for path in ROOT.glob('*.md'):
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8-sig')):
            if '://' in target or target.startswith(('#', 'mailto:')):
                continue
            target = target.split('#', 1)[0]
            if target and not (path.parent / target).exists():
                errors.append(f'Broken local link in {path.name}: {target}')

    try:
        status = json.loads((ROOT / 'VERIFICATION.json').read_text(encoding='utf-8'))
        if not isinstance(status.get('console_tested'), bool):
            errors.append('Console verification status must be an explicit boolean')
        revision = (ROOT / 'gba/third_party/mgba/UPSTREAM_REVISION.txt').read_text().strip()
        if status.get('core_revision') != revision:
            errors.append('Core revision differs from VERIFICATION.json')
    except (ValueError, OSError) as exc:
        errors.append(f'Invalid verification metadata: {exc}')

    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS source release checks: {len(paths)} candidate files (AI-assisted)')
    print('Native build, package integrity and PS5 hardware testing remain separate checks.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
