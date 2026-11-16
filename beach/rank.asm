; タイトル（はじめの画面）の箱の中を「スタート」「スコア」のメニューにする（十字キーの上下でえらび、A か START で決める）
;  ・スタート：すぐゲームへ（えらぶまでは、ピカチュウが右へ泳ぐのをくりかえして待つ）
;  ・スコア：箱を下へ広げて、これまでのスコアの上位 5 つを 1 位から出す（A・B・START・SELECT でメニューにもどる。
;    開いている間はピカチュウを止めて消す）
;  ・SRAM バンク1 の $BF08〜: "SR" + スコア 5 つ（2 バイト BCD、下の桁が先） + チェック 1 バイト
;  ・前のセーブ（ハイスコアだけ）があれば、それを 1 位にする
;  ・さいごまで遊んで結果が出た回だけ記録（とちゅうで SELECT・ゲームオーバーは記録しない）
;  ・文字の絵は、つぎの回の前（画面が出ている間）に HDMA で VRAM $9200 へ
;  ・ゲームが始まるのは スタートをえらんだとき なので、波のならびは えらんだときで変わる（もとのゲームで
;    おじいさんに話しかけたときと同じ）

DEF sBeachRank   EQU $bf08
DEF RANK_TILE    EQU $20 ; 0〜9 が $20〜$29、ー $2a、ス $2b、コ $2c、ア $2d、タ $2e、ト $2f、▶ $30
DEF RANK_BAR     EQU RANK_TILE + 10
DEF T_SU         EQU RANK_TILE + 11
DEF T_KO         EQU RANK_TILE + 12
DEF T_A          EQU RANK_TILE + 13
DEF T_TA         EQU RANK_TILE + 14
DEF T_TO         EQU RANK_TILE + 15
DEF T_CURSOR     EQU RANK_TILE + 16
DEF RANK_BLANK   EQU $ff ; はじめの画面の 白いタイル
DEF MENU_COL     EQU 7   ; ▶ の列（文字はその右）
DEF BEACH_CURSOR     EQU 6 ; wd492 の このビット：▶ が「スコア」
DEF BEACH_SCORE_OPEN EQU 7 ; wd492 の このビット：スコアの箱を開いている
DEF Joypad EQU $01ab

; はじめの画面：自動の BG 転送を入れたあとの 1 つめの DelayFrame のかわり
SECTION "BeachRankIntroHook", ROMX[$5016], BANK[$3e]
	call BeachIntroDrawLabel

; はじめの画面の 毎コマ：RunObjectAnimations のかわり
SECTION "BeachRankIntroLoop", ROMX[$5048], BANK[$3e]
	call BeachIntroFrame

SECTION "BeachRank", ROMX[$6000], BANK[$3e]
; 起動したとき。ランキングがまだなければ作る（前のハイスコアを 1 位に）
BeachRankInit::
	call BeachEnableSRAM
	ld a, [sBeachRank]
	cp $53
	jr nz, .new
	ld a, [sBeachRank + 1]
	cp $52
	jr nz, .new
	call BeachRankChecksum
	cp [hl]
	jr z, .done
.new
	ld hl, sBeachRank
	ld a, $53
	ld [hli], a
	ld a, $52
	ld [hli], a
	ld a, [wSurfingMinigameHiScore]
	ld [hli], a
	ld a, [wSurfingMinigameHiScore + 1]
	ld [hli], a
	xor a
	ld b, 8
.zero
	ld [hli], a
	dec b
	jr nz, .zero
	call BeachRankChecksum
	ld [hl], a
.done
	jp BeachDisableSRAM

; a = スコア 10 バイトの合計の反転、hl = チェックの場所
BeachRankChecksum:
	ld hl, sBeachRank + 2
	ld b, 10
	xor a
.loop
	add [hl]
	inc hl
	dec b
	jr nz, .loop
	cpl
	ret

; 1 回おわったあと。結果が出ていれば、その合計スコアをランキングに入れる
BeachRankRecord::
	ld a, [wSurfingMinigameRoutineNumber]
	and $7f
	cp $a
	jr z, .done_game
	cp $b
	ret nz
.done_game
	ld a, [wSurfingMinigameTotalScore]
	ld e, a
	ld a, [wSurfingMinigameTotalScore + 1]
	ld d, a
	or e
	ret z
	call BeachEnableSRAM
	; 上から順に、持っているスコア（de）のほうが高ければ入れかえて、はみ出たほうを下へ持っていく
	ld hl, sBeachRank + 2
	ld b, 5
.slot
	inc hl
	ld a, [hld]
	cp d
	jr c, .swap
	jr nz, .next
	ld a, [hl]
	cp e
	jr nc, .next
.swap
	ld a, [hl]
	ld c, a
	ld [hl], e
	inc hl
	ld e, c
	ld a, [hl]
	ld c, a
	ld [hl], d
	inc hl
	ld d, c
	jr .cont
.next
	inc hl
	inc hl
.cont
	dec b
	jr nz, .slot
	call BeachRankChecksum
	ld [hl], a
	jp BeachDisableSRAM

; 文字の絵を VRAM $9200 へ（DelayFrame のすぐあと、画面が出ているときに呼ぶ）
BeachRankLoadTiles::
	ldh a, [rVBK]
	push af
	xor a
	ldh [rVBK], a
	ld a, HIGH(BeachRankFont)
	ldh [rHDMA1], a
	ld a, LOW(BeachRankFont)
	ldh [rHDMA2], a
	ld a, $92
	ldh [rHDMA3], a
	xor a
	ldh [rHDMA4], a
	ldh a, [rLCDC]
	add a
	ld a, 17 - 1
	jr nc, .go ; 画面が消えているときは いっぺんに
	or $80     ; 出ているときは 1 行の すきまごとに 16 バイト（17 回）
.go
	ldh [rHDMA5], a
.wait
	ldh a, [rHDMA5]
	inc a
	jr nz, .wait
	pop af
	ldh [rVBK], a
	ret

; 箱の中をメニューにして、DelayFrame へ
BeachIntroDrawLabel:
	call BeachDrawMenu
	jp DelayFrame

; 箱の中（7〜9 行・2〜17 列）をけして、「スタート」「スコア」と ▶ を書く
BeachDrawMenu:
	ld hl, wTileMap + SCREEN_WIDTH * 7 + 2
	ld c, 3
.clear_row
	ld b, 16
	ld a, RANK_BLANK
.clear
	ld [hli], a
	dec b
	jr nz, .clear
	ld de, SCREEN_WIDTH - 16
	add hl, de
	dec c
	jr nz, .clear_row
	ld hl, wTileMap + SCREEN_WIDTH * 7 + MENU_COL + 1
	ld a, T_SU
	ld [hli], a
	ld a, T_TA
	ld [hli], a
	ld a, RANK_BAR
	ld [hli], a
	ld [hl], T_TO
	ld hl, wTileMap + SCREEN_WIDTH * 9 + MENU_COL + 1
	ld a, T_SU
	ld [hli], a
	ld a, T_KO
	ld [hli], a
	ld [hl], T_A
	; fallthrough
BeachDrawCursor:
	ld hl, wTileMap + SCREEN_WIDTH * 7 + MENU_COL
	ld de, wTileMap + SCREEN_WIDTH * 9 + MENU_COL
	ld a, [wd492]
	bit BEACH_CURSOR, a
	jr z, .put
	push hl
	ld h, d
	ld l, e
	pop de
.put
	ld [hl], T_CURSOR
	ld a, RANK_BLANK
	ld [de], a
	ret

; はじめの画面の 毎コマ（RunObjectAnimations のかわり）
BeachIntroFrame:
	call Joypad
	ld hl, wd492
	bit BEACH_SCORE_OPEN, [hl]
	jr nz, .open
	ldh a, [hJoyPressed]
	ld b, a
	and PAD_UP | PAD_DOWN
	jr z, .no_move
	ld a, [hl]
	xor 1 << BEACH_CURSOR
	ld [hl], a
	push bc
	call BeachDrawCursor
	pop bc
	ld hl, wd492
.no_move
	ld a, b
	and PAD_A | PAD_START
	jr z, .animate
	bit BEACH_CURSOR, [hl]
	jr nz, .score
	; スタート：つぎにループの頭へもどったときに、はじめの画面がおわる
	ld a, 1
	ld [wSurfingMinigameIntroAnimationFinished], a
	ret
.score
	set BEACH_SCORE_OPEN, [hl]
	call ClearSprites
	jp BeachDrawScoreBox
.open
	ldh a, [hJoyPressed]
	and PAD_A | PAD_B | PAD_START | PAD_SELECT
	ret z
	res BEACH_SCORE_OPEN, [hl]
	call DrawSurfingPikachuMinigameIntroBackground
	call BeachDrawMenu
.animate
	call RunObjectAnimations
	ld a, [wSurfingMinigameIntroAnimationFinished]
	and a
	ret z
	; ピカチュウが右はしまで泳いだ → まだえらんでいないので、はじめの場所からもう一度
	xor a
	ld [wSurfingMinigameIntroAnimationFinished], a
	ld a, $c
	lb de, $74, $58 ; はじめと同じ場所から
	jp SpawnAnimatedObject

; 説明の箱を 下へ広げて（6〜12 行・1〜18 列）、中に 1 位から 5 位までを書く
BeachDrawScoreBox:
	ld hl, wTileMap + SCREEN_WIDTH * 6 + 1
	lb de, $00, $01
	ld a, $05
	call .Row
	ld c, 5
.middle
	push bc
	lb de, $04, $04
	ld a, RANK_BLANK
	call .Row
	pop bc
	dec c
	jr nz, .middle
	lb de, $02, $03
	ld a, $05
	call .Row
	call BeachEnableSRAM
	ld de, sBeachRank + 2
	ld hl, wTileMap + SCREEN_WIDTH * 7 + 6
	ld b, RANK_TILE + 1
.entry
	push hl
	ld a, b
	ld [hli], a
	inc hl
	inc hl
	ld a, [de]
	ld c, a
	inc de
	ld a, [de]
	inc de
	push de
	ld d, a
	or c
	jr nz, .number
	ld a, RANK_BAR
	ld [hli], a
	ld [hli], a
	ld [hli], a
	ld [hl], a
	jr .next
.number
	ld e, 0
	ld a, d
	swap a
	call .Digit
	ld a, d
	call .Digit
	ld a, c
	swap a
	call .Digit
	ld e, 1
	ld a, c
	call .Digit
.next
	pop de
	pop hl
	ld a, l
	add SCREEN_WIDTH
	ld l, a
	adc h
	sub l
	ld h, a
	inc b
	ld a, b
	cp RANK_TILE + 6
	jr nz, .entry
	jp BeachDisableSRAM

; 1 行：d（左はし）、a × 16、e（右はし）。hl は次の行の 同じ列へ
.Row:
	ld [hl], d
	inc hl
	ld b, 16
.fill
	ld [hli], a
	dec b
	jr nz, .fill
	ld [hl], e
	ld bc, SCREEN_WIDTH - 17
	add hl, bc
	ret

; a の下 4 ビットを 1 けた書く（上の 0 は白、e が 0 でないあとは 0 も書く）
.Digit:
	and $0f
	jr nz, .show
	inc e
	dec e
	jr nz, .show
	ld [hl], RANK_BLANK
	inc hl
	ret
.show
	ld e, 1
	add RANK_TILE
	ld [hli], a
	ret

SECTION "BeachRankFont", ROMX[$6200], BANK[$3e]
BeachRankFont:
INCLUDE "rank_font.inc"
