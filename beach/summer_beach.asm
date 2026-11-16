; ピカチュウのサマービーチ（151匹そろう版・60fps版 xf から、サマービーチだけを取り出したゲーム）
;  ・電源を入れると、ゲームフリークのオープニング・タイトルをとばして、すぐサマービーチがはじまる
;  ・おわったら（A ボタン）、またサマービーチの はじめの画面から
;  ・ハイスコアを出したら、自動でセーブ（SRAM バンク1 の おわりの方。ふつうのセーブデータとは 別の場所）
;  ・はじめの画面で SELECT を押すと、これまでのスコアの上位 5 つ（rank.asm）
;  ・SELECT で、今のプレイをやめて はじめからやり直す
;  ・なみのりピカチュウ（さいしょのピカチュウ・なみのり おぼえ）が手持ちにいることにして、ピカチュウの声も出す
;  python3 tools/build_beach.py で build/summer_beach.gbc を作る（土台は build/xf.gbc）

DEF BEACH_SAVE_BANK EQU 1
DEF sBeachSave      EQU $bf00 ; "SB" + ハイスコア 2 バイト（BCD） + チェック 1 バイト

; Init の さいご（predef PlayIntro → タイトル）のかわりに、サマービーチへ
SECTION "BeachBootHook", ROM0[$1dc1]
	ld b, BANK(SummerBeachMain)
	ld hl, SummerBeachMain
	jp Bankswitch

; SELECT で 今のプレイをやめて、さいしょからやり直す（もとは 2回目からしか きかない）
; 毎コマの かかる時間を もとと同じにして（11 サイクル）、波のならび（乱数）を変えない
SECTION "BeachSelectRestart", ROMX[$40a7], BANK[$3e]
	ldh a, [hJoyPressed]
	and PAD_SELECT
	nop
	nop
	ret

DEF SurfingPikachuMinigame_BlankPals EQU $521b ; ハックでは 名前がない所

SECTION "BeachMain", ROMX[$7ee0], BANK[$3e]
SummerBeachMain:
	; 手持ち: さいしょのピカチュウ（なみのり）1匹。おや・ID は 0 どうしなので、主人公のピカチュウになる
	ld a, 1
	ld [wPartyCount], a
	ld a, STARTER_PIKACHU
	ld [wPartySpecies], a
	ld a, $ff
	ld [wPartySpecies + 1], a
	ld a, STARTER_PIKACHU
	ld [wPartyMon1Species], a
	ld a, SURF
	ld [wPartyMon1Moves], a
	call BeachLoadHiScore
	call BeachRankInit
.round
	xor a
	ld [wd492], a ; SELECT は BeachSelectRestart で いつでも やり直し
	call SurfingPikachuMinigame_BlankPals
	call DelayFrame
	call BeachRankLoadTiles ; ランキングの文字の絵
	call DelayFrame
	call DelayFrame
	xor a
	ldh [hTileAnimations], a
	ld a, $ff
	ld [wUpdateSpritesEnabled], a
	xor a
	ldh [rIF], a
	ld a, $f
	ldh [rIE], a
	ld a, $8
	ldh [rSTAT], a
	ld a, $98
	ldh [hAutoBGTransferDest + 1], a
	call SurfingPikachuMinigameIntro
	call SurfingPikachuLoop
	call BeachSaveIfHigher
	call BeachRankRecord
	; つぎの回の前に、画面のわりこみ（波のゆれ）を止めて、画面をけす
	xor a
	ldh [hLCDCPointer], a
	ldh [hSCX], a
	ldh [hSCY], a
	call DelayFrame
	jr .round

; SRAM のハイスコアを読む（なければ 0 のまま）
BeachLoadHiScore:
	call BeachEnableSRAM
	ld hl, sBeachSave
	ld a, [hli]
	cp $53
	jr nz, .none
	ld a, [hli]
	cp $42
	jr nz, .none
	ld a, [hli]
	ld e, a
	ld a, [hli]
	ld d, a
	add e
	cpl
	cp [hl]
	jr nz, .none
	ld a, e
	ld [wSurfingMinigameHiScore], a
	ld a, d
	ld [wSurfingMinigameHiScore + 1], a
.none
	jr BeachDisableSRAM

; ハイスコアが SRAM のものとちがえば（ハイスコアを出したら）セーブ
BeachSaveIfHigher:
	call BeachEnableSRAM
	ld hl, sBeachSave + 2
	ld a, [wSurfingMinigameHiScore]
	cp [hl]
	jr nz, .save
	inc hl
	ld a, [wSurfingMinigameHiScore + 1]
	cp [hl]
	jr z, BeachDisableSRAM
.save
	ld hl, sBeachSave
	ld a, $53
	ld [hli], a
	ld a, $42
	ld [hli], a
	ld a, [wSurfingMinigameHiScore]
	ld e, a
	ld [hli], a
	ld a, [wSurfingMinigameHiScore + 1]
	ld [hli], a
	add e
	cpl
	ld [hl], a
	; fallthrough
BeachDisableSRAM::
	xor a
	ld [rRAMB], a
	ld [rRAMG], a
	ret

BeachEnableSRAM::
	ld a, RAMG_SRAM_ENABLE
	ld [rRAMG], a
	ld a, BEACH_SAVE_BANK
	ld [rRAMB], a
	ret

