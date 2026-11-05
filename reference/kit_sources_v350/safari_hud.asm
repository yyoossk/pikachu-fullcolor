; サファリゾーン：歩いて いる 間も、画面の 下に のこりの 歩数と ボールの 数を 出す
;「あと　４８２ほ　　ボール　２５こ」（画面の 下 2行。上の 行は 濁点用）
; ・ゲームボーイカラーだけ（場所の 名前（map_sign.asm）と 同じ しくみ：ウィンドウ（vBGMap1 の 上の 2行）に
;   かいて hWY を 128 に。文字は VRAM の バンク1 に 写す）。
; ・サファリゾーンの マップ（SAFARI_ZONE_EAST 〜 CERULEAN_CAVE_2F の 前。PrintSafariZoneSteps と 同じ）で、
;   ウィンドウが あいて いる（hWY が 144）とき に 出す。場所の 名前が 出て いる 間・話しかけた とき・
;   メニュー・戦闘 などは 出さない（それが おわると また 出る）。サファリゾーンを 出ると 消す。
; ・KitSafariHudTick：RunningShoesIdleCheck（フィールドで 歩いて いない とき 毎回）から。
;   KitSafariHudStep：SafariZoneCheckSteps（1歩 ごと。歩数を へらした あと）から。歩数の 3けた だけ かきなおす。

DEF KIT_HUD_WY     EQU SCREEN_HEIGHT_PX - 2 * TILE_WIDTH ; 128
DEF KIT_HUD_BUFFER EQUS "wTileMapBackup2" ; 2行 × 20（かく ときだけ 使う）
DEF KIT_HUD_PAL    EQU 7 ; the text boxes' palette in the overworld (color/map_colors.asm)
DEF KIT_HUD_STEPS_X EQU 5
DEF KIT_HUD_BALLS_X EQU 15

KitSafariHudTick::
	ldh a, [hOnCGB]
	and a
	ret z
	call KitHudInSafari
	jr c, .inSafari
	; not in the Safari Zone: hide it
	ldh a, [hWY]
	cp KIT_HUD_WY
	ret nz
	ld a, SCREEN_HEIGHT_PX
	ldh [hWY], a
	ret
.inSafari
	ldh a, [hWY]
	cp SCREEN_HEIGHT_PX
	ret nz ; shown, or the window is used by something else (the map sign too)
	; the whole bar
	ld hl, KIT_HUD_BUFFER
	ld bc, 2 * SCREEN_WIDTH
	ld a, '　'
	call FillMemory
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + 2
	ld de, KitHudText
	call PlaceString
	call KitHudPrintNumbers
	ld hl, KIT_HUD_BUFFER
	ld de, vBGMap1
	ld c, 2 * SCREEN_WIDTH
	call KitHudToWindow
	call KitHudInvalidateShadow
	ld a, KIT_HUD_WY
	ldh [hWY], a
	ret

KitSafariHudStep::
	ldh a, [hOnCGB]
	and a
	ret z
	ldh a, [hWY]
	cp KIT_HUD_WY
	ret nz
	call KitHudPrintNumbers
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + KIT_HUD_STEPS_X
	ld de, vBGMap1 + TILEMAP_WIDTH + KIT_HUD_STEPS_X
	ld c, 3
	jp KitHudToWindow

; carry: the current map is in the Safari Zone
KitHudInSafari:
	ld a, [wCurMap]
	cp SAFARI_ZONE_EAST
	ccf
	ret nc
	cp CERULEAN_CAVE_2F
	ret

; the steps (3 digits) and the balls (2 digits) into the buffer's 2nd row
KitHudPrintNumbers:
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + KIT_HUD_STEPS_X
	ld a, '　'
	ld [hli], a
	ld [hli], a
	ld [hl], a
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + KIT_HUD_BALLS_X
	ld [hli], a
	ld [hl], a
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + KIT_HUD_STEPS_X
	ld de, wSafariSteps
	lb bc, 2, 3
	call PrintNumber
	ld hl, KIT_HUD_BUFFER + SCREEN_WIDTH + KIT_HUD_BALLS_X
	ld de, wNumSafariBalls
	lb bc, 1, 2
	jp PrintNumber

KitHudText:
	db "あと　　　　ほ　　ボール　　　こ@"

; c tiles from hl (the buffer) to de (the window's tile map), with the text boxes' palette in
; VRAM bank 1; letters ($80-$ff) copied into VRAM bank 1 at the same tile number (the font is not
; in VRAM while walking), as in KitSignToWindow (map_sign.asm). One byte at a time when VRAM is free.
KitHudToWindow:
.tile
	ld a, [hli]
	push hl
	push bc
	push de
	ld b, a
	cp $80
	call nc, KitHudCopyGlyph
	pop de
	ld c, KIT_HUD_PAL
	ld a, b
	cp $80
	jr c, .bank0
	set B_OAM_BANK1, c
.bank0
	di
	call KitHudWaitHBlank
	ld a, b
	ld [de], a
	ld a, 1
	ldh [rVBK], a
	call KitHudWaitHBlank
	ld a, c
	ld [de], a
	xor a
	ldh [rVBK], a
	ei
	pop bc
	pop hl
	inc de
	ld a, e
	and TILEMAP_WIDTH - 1
	cp SCREEN_WIDTH
	jr nz, .sameRow
	ld a, e
	add TILEMAP_WIDTH - SCREEN_WIDTH
	ld e, a
	jr nc, .sameRow
	inc d
.sameRow
	dec c
	jr nz, .tile
	ret

; the map colors' copy of these attributes is no longer right (color/map_colors.asm)
; (WRAM bank 2: no call, push or pop while it is mapped: the stack is in the banked area)
KitHudInvalidateShadow:
	ld hl, W2_Shadow
	ld c, 2 * TILEMAP_WIDTH
	di
	ld a, 2
	ldh [rWBK], a
	ld a, $ff
.invalidate
	ld [hli], a
	dec c
	jr nz, .invalidate
	ld a, $fe
	ld [W2_PredPortion], a
	ld a, 1
	ldh [rWBK], a
	ei
	ret

; b = font tile ($80-$ff) → its picture (1bpp font, each byte twice) to VRAM bank 1 at that tile
KitHudCopyGlyph:
	push bc
	ld a, b
	sub $80
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, hl
	push hl
	ld bc, FontGraphics
	add hl, bc
	ld de, wBuffer
	ld bc, 8
	ld a, BANK(FontGraphics)
	call FarCopyData
	pop hl
	add hl, hl
	ld bc, vChars1
	add hl, bc
	ld d, h
	ld e, l
	ld hl, wBuffer
	ld c, 8
.byte
	ld a, [hli]
	ld b, a
	di
	ld a, 1
	ldh [rVBK], a
	call KitHudWaitHBlank
	ld a, b
	ld [de], a
	inc de
	ld [de], a
	inc de
	xor a
	ldh [rVBK], a
	ei
	dec c
	jr nz, .byte
	pop bc
	ret

; wait for the start of an hblank (or the vblank): VRAM can be written for a while
KitHudWaitHBlank:
	ldh a, [rLY]
	cp SCREEN_HEIGHT_PX
	jr nc, .vblank
.busy
	ldh a, [rSTAT]
	and STAT_BUSY
	jr z, .busy
.notBusy
	ldh a, [rSTAT]
	and STAT_BUSY
	jr nz, .notBusy
	ret
.vblank
	cp 152 ; not at the very end of the vblank
	jr nc, .busy
	ret
