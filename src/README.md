ここに、これからの直しや追加の asm を置きます（1行目に `; variants: ...`）。

- fix_hpbar_color.asm … 戦闘のHPバーの色が、HPが減っても緑のままになるのを直す
- map_sign.asm … 場所の名前の看板をクリスタルと同じ見た目・色にし、下から出入りさせる（看板の行の人などのスプライトもかくす）。枠の絵は gfx/map_sign_frame.inc
- fix_fanclub_relearner.asm … だいすきクラブの初訪問イベントで、ピカチュウが技思い出しおじさんをすりぬけるのを直す（おじさんを1マス右へ）
- fix_list_move_name.asm … 技思い出しおじさんで番号の大きい技（カブトプスの「きりさく」など）をえらぶとフリーズするのを直す（技の一覧で名前をとるバンクを技の名前のバンクに）
- tm_mart.asm … 殿堂入りのあと、タマムシデパート 2かいの わざマシンの店員が、一回しか手に入らない わざマシン（38本）も売る（元の 9本とあわせて番号の順に 47本。景品の 15・23・50 は入れない）
- fix_enemy_hud_frame.asm … 相手のHUDの枠の線がHPの数字で途切れるのを直す（自分側と同じく、数字の下に線）
- fix_run_pikachu.asm … ランニングシューズで走ると、つれ歩きのピカチュウが消えるのを直す（走ってもついてくる）
- dex_info_page.asm … ずかんのタイプのページに進化の条件を足し、その次に種族値のページを足す
- follow.asm … 連れ歩き（全ポケモン。赤緑青ピカチュウ連れ歩きキット）。手持ちの画面の SELECT でえらんだポケモン（赤い★）が後ろを歩く。最初のピカチュウは今までどおり。絵・下じき・色は gfx/follow/（tools/follow_data.py で reference/follow_kit から作る）。色は、下を向いているときは手持ちのアイコンの色、上・横を向いているときはキットの「歩き」の色（OBJ パレット6 を向きで入れかえる）。v f x xf だけ

テスト（tests/）: hpbar.py（HPバーの色）、fly.py / sign.py / sign2.py / sign3.py / sign4.py（看板）、fan.py / nav.py / fanev.py（だいすきクラブ）、hud.py / faint.py（相手のHUDの枠）、run.py / run2.py / run3.py（走る時のピカチュウ）、dex.py（ずかんのタイプのページ）、folmk.py / fol_*.py（連れ歩き。fol_lib.py が道具）
