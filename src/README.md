ここに、これからの直しや追加の asm を置きます（1行目に `; variants: ...`）。

- fix_hpbar_color.asm … 戦闘のHPバーの色が、HPが減っても緑のままになるのを直す
- fix_mapsign_sprites.asm … 場所の名前（看板）の上に人などのスプライトが重なるのを直す
- fix_fanclub_relearner.asm … だいすきクラブの初訪問イベントで、ピカチュウが技思い出しおじさんをすりぬけるのを直す（おじさんを1マス右へ）
- fix_enemy_hud_frame.asm … 相手のHUDの枠の線がHPの数字で途切れるのを直す（自分側と同じく、数字の下に線）
- fix_run_pikachu.asm … ランニングシューズで走ると、つれ歩きのピカチュウが消えるのを直す（走ってもついてくる）

テスト（tests/）: hpbar.py（HPバーの色）、fly.py（空を飛ぶでタマムシへ・看板）、fan.py / nav.py / fanev.py（だいすきクラブ）、hud.py / faint.py（相手のHUDの枠）、run.py / run2.py / run3.py（走る時のピカチュウ）
