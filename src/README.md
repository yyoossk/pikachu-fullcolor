ここに、これからの直しや追加の asm を置きます（1行目に `; variants: ...`）。

- fix_hpbar_color.asm … 戦闘のHPバーの色が、HPが減っても緑のままになるのを直す
- fix_mapsign_sprites.asm … 場所の名前（看板）の上に人などのスプライトが重なるのを直す
- fix_fanclub_relearner.asm … だいすきクラブの初訪問イベントで、ピカチュウが技思い出しおじさんをすりぬけるのを直す（おじさんを1マス右へ）

テスト（tests/）: hpbar.py（HPバーの色）、fly.py（空を飛ぶでタマムシへ・看板）、fan.py / nav.py / fanev.py（だいすきクラブ）
