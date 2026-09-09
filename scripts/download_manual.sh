#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
destination="$root/data/source/ffiec-bsa-aml-examination-manual.pdf"
url="https://archive.fdic.gov/view/fdic/4074/fdic_4074_DS3.pdf"
expected="1f056b56712e552c95e67792e45cd789a0f6f4c91d28d29819085922f71887a1"
mkdir -p "$(dirname "$destination")"
curl --fail --location --retry 3 "$url" --output "$destination"
actual="$(shasum -a 256 "$destination" | awk '{print $1}')"
if [[ "$actual" != "$expected" ]]; then
  echo "Checksum mismatch: expected $expected, received $actual" >&2
  exit 1
fi
echo "Verified FFIEC manual: $destination"
