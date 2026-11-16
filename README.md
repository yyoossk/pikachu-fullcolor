# ポケットモンスターピカチュウフルカラー（Ver.3.50 からの作業場所）

前のソースがなくなったので、**Ver.3.50 の ROM を土台にして、これからの直しや追加をパッチの asm で書く**作業場所です。
『金』の追加機能パッチ（goldkit）と同じやり方です。

## 準備
```
./setup.sh
```
- rgbds 1.0.1 と、元にしたディスアセンブル Narishma-gb/pokeyellow-jp（`PKJP_COMMIT` の版）を、このフォルダのとなりに取ってきます。
- 元のピカチュウ v1.0〜v1.3 を `orig/` に作ります。ROM の吸い出しはいりません。
- `patches350/` の Ver.3.50 のパッチを当てて、土台の12種類を `base/` に作ります。CRC が Ver.3.50 と同じになることも出します。
- エミュレーターのハーネス（`sameboy-harness/`）をビルドします。

ROM（`base/`・`orig/`・`build/`）はリポジトリに入れません。

## 版の名前
| 名前 | 版 | 名前 | 版 |
|---|---|---|---|
| v | 完全版 | s | 完全版・初代グラフィック版 |
| f | 完全版・60fps版 | sf | 完全版・初代グラフィック・60fps版 |
| x | 151匹そろう版 | sx | 151匹そろう版・初代グラフィック版 |
| xf | 151匹そろう版・60fps版 | sxf | 151匹そろう版・初代グラフィック・60fps版 |
| co | カラー化のみ | sco | カラー化のみ・初代グラフィック版 |
| cf | カラー化のみ・60fps版 | scf | カラー化のみ・初代グラフィック・60fps版 |

## ビルド
```
python3 tools/build.py          # 12種類 → build/<版>.gbc と build/<版>.sym
python3 tools/build.py v f      # 指定した版だけ
```
- `src/*.asm` を全部アセンブルして、`base/<版>.gbc` に当てます。`src/` が空なら、Ver.3.50 と同じ ROM になります。
- **入れる版の指定：** asm の1行目に `; variants: v f x xf s sf sx sxf` のように書きます。書かないと、カラー化のみ以外の8種類に入ります。
- **前もって読みこまれるもの：** asm には pokeyellow-jp の `includes.asm`（定数・マクロ・文字コード）が先に読みこまれます。
- **使えるラベル：** `syms/<版>.sym` にある元のピカチュウのラベルが使えます。`BANK()`・`farcall` も使えます。
- **版ごとの分けかた：** `IF DEF(V_60FPS)`・`IF DEF(V_SHODAI)`・`IF DEF(V_151)`・`IF DEF(V_COLORONLY)`・`IF DEF(V_V)` などで分けます。
- **SECTION の置き場所：**
  - `SECTION "名前", ROMX[$xxxx], BANK[$xx]`（場所を決めたもの）は、その場所に上書きします。元の命令を書きかえて、新しいコードへ飛ばすフックに使います。
  - 場所を決めないものは、その版のあき（`tools/freespace.py`）に自動で置きます。
  - `BANK[$xx]` だけ決めたものは、そのバンクのあきに置きます。

## ラベルの対応表（syms/）
`tools/mksyms.py` で、元のピカチュウのラベルが Ver.3.50 の ROM のどこにあるかを、中身の一致で探したものです。
- **ROM のラベル：** 8割ほど見つかります。改造で書きかわった所のラベルは、のっていないことがあります（その場合は ROM を読んで場所を決めます）。
- **改造で足した処理（金1.1の機能など）のラベル：** 元のピカチュウにはないので、のっていません。`reference/` のソースを手がかりに、ROM から探します。
- **RAM のラベル：** 元のままです。セーブデータの場所は変わっていません。ただ、改造で足した変数（`wKitStatusPalMode` など）のあとの WRAM はずれていることがあるので、使う前にエミュレーターで確かめます。
- `wCurMap`・`wTileMap`・`wBuffer`・`PlaceString`・`GetMonHeader`・`farcall` が正しく動くことは、エミュレーターで確かめてあります。

## リリース
```
python3 tools/mkips.py build/v.gbc ポケットモンスターピカチュウフルカラー_v1.0用.ips
```
元のピカチュウ v1.0〜v1.3 のどれに当てても同じ ROM になるパッチを作り、4つに当てて確かめます（4つの名前のファイルは中身が同じ）。

## エミュレーターで確かめる
`sameboy-harness/`（gbrec）を使います。`sameboy-harness/python/gr.py` の `GR` クラスで、ボタン・画面写真・メモリの読み書きができます。

## そのほか
- `reference/kit_sources_v350/`：Ver.3.50 で足した機能のソースを、作業の記録から取り出したものです。最初に書いた版なので、そのあとの手直しは入っていません。
- `patches350/`：Ver.3.50 のリリースのパッチ（v1.0用。v1.1〜v1.3 にも当たる）。

## サマービーチだけのゲーム（beach/）
151匹そろう版・60fps版（xf）から、ピカチュウのサマービーチだけを取り出したゲームです。
- 電源を入れると、すぐサマービーチ。おわったら（A ボタン）また はじめから。
- ハイスコアを出したら自動でセーブ（SRAM バンク1 の $BF00。ふつうのセーブとは別の場所）。
```
python3 tools/build.py xf
python3 tools/build_beach.py                 # → build/summer_beach.gbc
python3 tools/mkips.py build/summer_beach.gbc ピカチュウのサマービーチ.ips   # v1.0〜v1.3 のどれに当てても同じ
```
### 要らない部分を消して小さくする（128KB）
```
# 1) 遊んで、読まれた場所を記録（12通り）
for s in $(seq 1 12); do python3 tests/beach/cov.py build/summer_beach.gbc /tmp/cov/c$s.bin $s & done; wait
python3 -c "import numpy as np; c=np.zeros(0x100000,np.uint8)
for s in range(1,13): c|=np.fromfile(f'/tmp/cov/c{s}.bin',np.uint8)
np.save('/tmp/cov/c.npy',c)"
# 2) 詰め直す → build/summer_beach_small.gbc（.map.txt にバンクの置き場所）
python3 tools/shrink_beach.py /tmp/cov/c.npy
# 3) パッチ（EOF のあとに大きさ 3 バイト＝切りつめ。対応していない道具でも、先頭 128KB は同じで動く）
python3 tools/mkips.py build/summer_beach_small.gbc ピカチュウのサマービーチ.ips
```
- 残すもの：バンク0 まるごと、実際に読まれた所（前後 16 バイト）、実行された命令から飛び先をたどって届くプログラム。消した所は $FF。
- アドレスが重ならないバンクどうしを 1 つのバンクにまとめ、ld [$2000], a はすべて「論理バンク→実際のバンク」の表を引くルーチン経由にする。
- 確かめ方：tests/beach/README.md（小さい ROM で、消した所を一度も読まないこと・1MB 版と同じ画面になること）
