; バトルで わざを えらぶ とき、右下の わくの PP（今の 数）を、のこりが 少ないと 黄色、0 なら 赤で 出す
; （ゲームボーイカラーだけ）。少ない：今の PP × 4 ≦ 最大の PP（4分の1 いか）。
; ・色は BG パレット 7。野生の バトルでは つかまえた しるしの パレット（OwnedIconColors：白・黄・赤・黒。
;   黄は しるしでは 使って いない 色）。トレーナーとの バトルでは パレット 7 を ここで かく（ほかでは 使って いない）。
; ・数の 2ます（(14, 13)・(15, 13)）の 字を VRAM の バンク1 の タイル $5c・$5d に 色1（黄）か 色2（赤）で 写して、
;   その ますの タイルと 属性（バンク1・パレット 7）を 両方の BG マップに かく（wTileMap も $5c・$5d に）。
; ・HandleMenuInput の あと（SelectMenuItem の .select）に もとに もどす：数を かきなおして 属性を パレット 2 に。
;   カーソルを 動かすと PrintMenuItem が また 色を つける。
; KitPrintMenuItemPP：PrintMenuItem（core.asm）から farjp。KitPPColorOff：.select の HandleMenuInput の あと。

DEF KIT_PP_TILE  EQU $5c ; VRAM bank 1, $5c-$5d (bank 1's $5e-$5f: the HUD)
DEF KIT_PP_PAL   EQU 7
DEF KIT_PP_ATTR0 EQU 2   ; the battle's attribute of these cells (the player's Pokemon's palette)
DEF KIT_PP_X     EQU 14
DEF KIT_PP_Y     EQU 13

KitPrintMenuItemPP::
	farcall KitPrintMenuItem
	ldh a, [hOnCGB]
	and a
	ret z
	ld a, [wTileMap + KIT_PP_Y * SCREEN_WIDTH + 16]
	cp '／'
	ret nz ; a disabled move: no PP shown
	ld a, [wBattleMenuCurrentPP]
	ld c, 2 ; red
	and a
	jr z, .color
	add a
	add a
	ld hl, wMaxPP
	cp [hl]
	jr z, .low
	ret nc
.low
	ld c, 1 ; yellow
.color
	push bc
	ld a, [wIsInBattle]
	cp 2 ; a trainer battle: palette 7 is ours
	call z, KitPPWritePal7
	pop bc
	ld hl, wTileMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X
	ld b, KIT_PP_TILE
	ld de, KIT_PP_Y * TILEMAP_WIDTH + KIT_PP_X
.cell
	ld a, [hl]
	cp '　'
	jr z, .next
	push hl
	push bc
	push de
	call KitPPGlyph ; a = font tile, b = bank 1 tile, c = color
	pop de
	pop bc
	pop hl
	ld [hl], b
	ld a, b
	push bc
	ld b, BG_BANK1 | KIT_PP_PAL
	call KitPPWriteCell
	pop bc
.next
	inc hl
	inc de
	inc b
	ld a, b
	cp KIT_PP_TILE + 2
	jr nz, .cell
	ret

KitPPColorOff::
	ldh a, [hOnCGB]
	and a
	ret z
	ld a, [wTileMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X]
	cp KIT_PP_TILE
	jr z, .restore
	ld a, [wTileMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X + 1]
	cp KIT_PP_TILE + 1
	ret nz
.restore
	hlcoord KIT_PP_X, KIT_PP_Y
	ld a, '　'
	ld [hli], a
	ld [hld], a
	ld de, wBattleMenuCurrentPP
	lb bc, 1, 2
	call PrintNumber
	ld hl, wTileMap + KIT_PP_Y * SCREEN_WIDTH + KIT_PP_X
	ld de, KIT_PP_Y * TILEMAP_WIDTH + KIT_PP_X
	ld a, [hli]
	ld b, KIT_PP_ATTR0
	call KitPPWriteCell
	inc de
	ld a, [hl]
	ld b, KIT_PP_ATTR0
	jp KitPPWriteCell

; a = tile, b = attribute, de = the cell's offset in a BG map: both BG maps (VRAM bank 0: the tile, 1: the attribute)
KitPPWriteCell:
	push hl
	ld c, a
	ld hl, vBGMap0
	add hl, de
	call .one
	ld hl, vBGMap1
	add hl, de
	call .one
	pop hl
	ret
.one
	di
.wait1
	ldh a, [rSTAT]
	and %10 ; H-blank or V-blank
	jr nz, .wait1
	ld [hl], c
	ld a, 1
	ldh [rVBK], a
.wait2
	ldh a, [rSTAT]
	and %10
	jr nz, .wait2
	ld [hl], b
	xor a
	ldh [rVBK], a
	ei
	ret

; a = font tile ($80-$ff), b = VRAM bank 1 tile, c = color (1 or 2): the letter in that color
KitPPGlyph:
	push bc
	sub $80
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	ld de, FontGraphics
	add hl, de
	ld de, wBuffer
	ld bc, 8
	ld a, BANK(FontGraphics)
	call FarCopyData
	pop bc
	; the tile's address in VRAM bank 1 (vChars2: tiles $00-$7f)
	ld l, b
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	add hl, hl
	ld de, vChars2
	add hl, de
	ld de, wBuffer
	ld b, 8
.row
	ld a, [de]
	inc de
	push de
	ld d, a ; the row's pixels
	ld e, 0
	ld a, c
	cp 1
	jr z, .gotBytes
	ld e, d ; color 2: the high byte
	ld d, 0
.gotBytes
	di
	ld a, 1
	ldh [rVBK], a
.wait
	ldh a, [rSTAT]
	and %10
	jr nz, .wait
	ld a, d
	ld [hli], a
	ld a, e
	ld [hli], a
	xor a
	ldh [rVBK], a
	ei
	pop de
	dec b
	jr nz, .row
	ret

; trainer battles: BG palette 7 = the PP colors (the same as the owned icon's in wild battles)
KitPPWritePal7:
	ld a, $80 | (KIT_PP_PAL * PAL_SIZE)
	ldh [rBGPI], a
	ld hl, KitPPColors
	ld c, PAL_SIZE
.byte
	ldh a, [rSTAT]
	and %10
	jr nz, .byte
	ld a, [hli]
	ldh [rBGPD], a
	dec c
	jr nz, .byte
	ret

KitPPColors:
	RGB 31,31,31, 31,22,00, 31,02,02, 03,03,03 ; white, yellow, red, black
