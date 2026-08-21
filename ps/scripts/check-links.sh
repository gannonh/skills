#!/usr/bin/env bash
# Assert every relative path referenced from SKILL.md and references/ resolves.
# Run from anywhere; resolves against the skill root.
set -uo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

miss=0; ok=0
while IFS= read -r line; do
  src="${line%%:*}"; target="${line#*:}"
  case "$target" in http*|\#*) continue;; esac
  base="$(dirname "$src")"
  if [ -e "$base/$target" ] || [ -e "$target" ]; then
    ok=$((ok+1))
  else
    printf 'MISSING  %-46s -> %s\n' "$src" "$target"; miss=$((miss+1))
  fi
done < <(
  grep -rHoE '\((\.{0,2}/)?[A-Za-z0-9_./-]+\.(md|sh|ts|tsv|json))' --include='*.md' --exclude-dir=node_modules . \
    | sed -E 's/\(([^)]*)\)$/\1/' | sed 's/:(/:/'
  grep -rHoE '`(references|scripts)/[A-Za-z0-9_./-]+`' --include='*.md' --exclude-dir=node_modules . \
    | tr -d '`' 
)

echo "---"
echo "resolved: $ok   missing: $miss"
[ "$miss" -eq 0 ] || exit 1
