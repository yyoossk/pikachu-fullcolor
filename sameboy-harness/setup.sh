#!/bin/bash
# SameBoy ハーネスのセットアップ（Linux x86_64）
#   ./setup.sh        … 同梱の bin/ が動くか確かめ、動かなければソースから作る
#   ./setup.sh build  … いつもソースから作り直す（SameBoy と、ブートROM用の rgbds を GitHub から取得）
set -e
H="$(cd "$(dirname "$0")" && pwd)"
SAMEBOY_COMMIT=c458e7c     # 作ったときの SameBoy（2026-10-04 の master）
RGBDS_TAG=v0.9.4
if [ "$1" != "build" ] && "$H/bin/gbrec" 2>&1 | grep -q "rom bootrom"; then echo "OK: bin/gbrec はそのまま動きます"; exit 0; fi
mkdir -p "$H/deps" && cd "$H/deps"
if ! command -v rgbasm >/dev/null; then
  [ -d rgbds ] || git clone -q https://github.com/gbdev/rgbds.git
  (cd rgbds && git checkout -q $RGBDS_TAG && make -j"$(nproc)" rgbasm rgblink rgbfix rgbgfx >/dev/null)
  export PATH="$H/deps/rgbds:$PATH"
fi
[ -d SameBoy ] || git clone -q https://github.com/LIJI32/SameBoy.git
cd SameBoy && git checkout -q $SAMEBOY_COMMIT
make tester -j"$(nproc)" >/dev/null 2>&1    # CONF=release にしない（LTO の .o は gcc でリンクできない）
cd "$H"; mkdir -p bin
for t in gbrec gblink; do
  gcc -O2 -std=gnu11 -DGB_INTERNAL -w -Ideps/SameBoy src/$t.c deps/SameBoy/build/obj/Core/*.o -lm -o bin/$t
done
cp deps/SameBoy/build/bin/tester/{cgb_boot,dmg_boot,sgb_boot,agb_boot}.bin bin/
echo "OK: bin/ を作りました"
