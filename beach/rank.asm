; はじめの画面（タイトルと説明）の左上に、これまでのスコアの上位 5 つを高い順に出す
;  ・SRAM バンク1 の $BF08〜: "SR" + スコア 5 つ（2 バイト BCD、下の桁が先） + チェック 1 バイト
;  ・前のセーブ（ハイスコアだけ）があれば、それを 1 位にする
;  ・さいごまで遊んで結果が出た回だけ記録（とちゅうで SELECT・ゲームオーバーは記録しない）
;  ・文字の絵は、つぎの回の前（画面が出ている間）に HDMA で VRAM $9200 へ。画面の文字は、はじめの画面の
;    1 コマめの待ちの前に wTileMap へ書く。どちらも次のコマを待つ前にすむので、波のならび（乱数）は変わらない

DEF sBeachRank   EQU $bf08
DEF RANK_TILE    EQU $20 ; 0〜9 が $20〜$29、ー が $2a、ハイスコア が $2b〜$2f
DEF RANK_BAR     EQU RANK_TILE + 10
DEF RANK_HEADER  EQU RANK_TILE + 11
DEF RANK_BLANK   EQU $ff ; はじめの画面の 白いタイル

; はじめの画面：自動の BG 転送を入れたあとの 1 つめの DelayFrame のかわり
SECTION "BeachRankIntroHook", ROMX[$5016], BANK[$3e]
	call BeachIntroDrawRank

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
	ld a, 16 - 1
	jr nc, .go ; 画面が消えているときは いっぺんに
	or $80     ; 出ているときは 1 行の すきまごとに 16 バイト
.go
	ldh [rHDMA5], a
.wait
	ldh a, [rHDMA5]
	inc a
	jr nz, .wait
	pop af
	ldh [rVBK], a
	ret

; はじめの画面の左上（6×6）に ランキングを書いて、DelayFrame へ
BeachIntroDrawRank:
	; タイトル（上の 6 行の 6〜18 列）を 1 列 右へずらして、ランキングとの間をあける
	ld hl, wTileMap + 18
	ld c, 6
.shift_row
	push hl
	ld b, 13
.shift
	ld a, [hli]
	ld [hld], a
	dec hl
	dec b
	jr nz, .shift
	inc hl
	ld [hl], RANK_BLANK
	pop hl
	ld de, SCREEN_WIDTH
	add hl, de
	dec c
	jr nz, .shift_row
	call BeachEnableSRAM
	ld hl, wTileMap
	ld a, RANK_HEADER
	ld b, 5
.header
	ld [hli], a
	inc a
	dec b
	jr nz, .header
	ld de, sBeachRank + 2
	ld hl, wTileMap + SCREEN_WIDTH
	ld b, RANK_TILE + 1
.entry
	push hl
	ld a, b
	ld [hli], a
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
	call BeachDisableSRAM
	jp DelayFrame

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
