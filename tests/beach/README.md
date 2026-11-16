サマービーチだけの ROM（build/summer_beach.gbc）を、ピカチュウフルカラー（build/xf.gbc）の海の家から始めるサマービーチと並べて確かめる試験。
- mkstate.py … xf で海の家のおじさんに話しかけて、サマービーチが始まった状態（/tmp/cmp/talk.st）を作る（最初に1回）
- cmp.py SEED フレーム数 出力 [--align] … 同じ操作で両方を動かして録画（--align で乱数・DIV・入力の位相をそろえる）。sbs.py で横に並べた画像
- full.py a|b 出力 SEED … 1回を結果の画面まで通して、場面ごとの画面写真
- cry.py a|b … 結果の画面でピカチュウの声が鳴るか
- pals.py … 場面ごとの GBC パレット
- misc.py gameover|ffsav|notbest|rounds|reset|select … ゲームオーバー・まっさらな SRAM・ベストでない時・5回続けて・ソフトリセット・SELECT
