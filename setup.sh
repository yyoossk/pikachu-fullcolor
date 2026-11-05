#!/bin/bash
# 作業の準備（作業場所が新しくなったら、最初に1回）
#   ./setup.sh
# 1. rgbds 1.0.1 と、元にしたディスアセンブル（Narishma-gb/pokeyellow-jp）を、このフォルダの となり（..）に取ってくる
# 2. ディスアセンブルをビルドして、元のピカチュウ v1.0〜v1.3 を orig/ に作る（ROM の吸い出しはいらない）
# 3. patches350/ の Ver.3.50 のパッチを v1.0 に当てて、土台の12種類を base/ に作る
# 4. エミュレーターのハーネス（sameboy-harness）をビルドする
set -e
H="$(cd "$(dirname "$0")" && pwd)"; P="$(dirname "$H")"
cd "$P"
if [ ! -x rgbds/rgbasm ]; then
  curl -sSL -o rgbds.tar.xz https://github.com/gbdev/rgbds/releases/download/v1.0.1/rgbds-linux-x86_64.tar.xz
  mkdir -p rgbds && tar -xf rgbds.tar.xz -C rgbds && rm rgbds.tar.xz
fi
export PATH="$P/rgbds:$PATH"
[ -d pokeyellow-jp ] || git clone -q https://github.com/Narishma-gb/pokeyellow-jp
(cd pokeyellow-jp && git checkout -q "$(cat "$H/PKJP_COMMIT")" && make -j"$(nproc)" >/dev/null && sha1sum -c roms.sha1 2>/dev/null | grep -v patch)
mkdir -p "$H/orig" "$H/base"
cp pokeyellow-jp/pokeyellow.gb "$H/orig/v10.gb"
for i in 1 2 3; do cp pokeyellow-jp/pokeyellow1$i.gb "$H/orig/v1$i.gb"; done
cd "$H"
for p in patches350/*.ips; do k=$(basename "$p" .ips); python3 tools/applyips.py orig/v10.gb "$p" "base/$k.gbc"; done
python3 tools/build.py | sed 's/^/base: /'
[ -x sameboy-harness/bin/gbrec ] || ./sameboy-harness/setup.sh build
echo "OK"
