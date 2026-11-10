; variants: v s f sf x sx xf sxf
; 場所の名前（町や道路に入った時に画面の下に出る看板）を、クリスタルと同じ見た目・色にする。
;   ・枠: クリスタルの看板の枠（src/gfx/map_sign_frame.inc、VRAMバンク1のタイル $51〜$5D）
;   ・色: クリスタルの看板の色（うすい黄色 31,31,16 ／ 茶色 14,9,0 ／ 黒）。BGパレット7の色1・2を、
;         看板が出ているあいだだけかえる（文字の窓は色0・3しか使わないので、かわらない）
;   ・名前: 真ん中によせる
;   ・出入り: 下からスッと出て、時間がたつとスッと引っこむ（1フレーム2ドット）
;   ・看板の行にかかる人などのスプライトはかくす（看板の今の高さに合わせる）
; キットの看板の処理（バンク$3A）はそのまま使い、何か所かをかえる。

IF DEF(V_60FPS)
DEF KS EQU $20 ; 60fps版は、キットの看板の処理が $20 うしろにある
ELSE
DEF KS EQU 0
ENDC
DEF KitSignFrame     EQU $75ae + KS ; 毎フレームの処理（ldh a, [hGBC] / and a / ret z ...）
DEF KitSignBorder    EQU $7657 + KS ; ld hl, $cd7c / ld bc, $0212 / call TextBoxBorder
DEF KitSignNamePos   EQU $7670 + KS ; ld hl, $cda6（名前の位置）
DEF KitSignCopyCall  EQU $7679 + KS ; call KitSignCopy
DEF KitSignCopy      EQU $76d3 + KS ; バッファ → ウインドウ（$9C00）へ
DEF KitSignAttr      EQU $76e8 + KS ; ld c, 7 / ld a, b / cp $80 / jr c, +2 / set 3, c
DEF KitSignGlyphPut  EQU $7760 + KS ; ld a, b / ld [de], a / inc de / ld [de], a / inc de

DEF hIsGBC          EQU $fffe
DEF wMapSignTimer   EQU $d6a4 ; キットの看板の、のこり時間（0 なら出ていない）
DEF wSignBuffer     EQU $cd7c ; キットの看板の 20×4 のバッファ
DEF wSignName       EQU $cd68 ; 名前（$50 でおわり）
DEF MAP_SIGN_WY     EQU $70
DEF HIDDEN_WY       EQU $90
DEF SLIDE_STEP      EQU 2
DEF SIGN_TILE       EQU $50   ; 枠のタイル n（1〜13）は SIGN_TILE + n（VRAMバンク1）
DEF SIGN_FILL       EQU SIGN_TILE + 13
DEF SIGN_ATTR       EQU $0f   ; パレット7・VRAMバンク1

; WRAMバンク7（ほかで使っていない）
DEF SIGN_WRAM_BANK  EQU 7
DEF wSignMagic      EQU $d000 ; 2バイト $A5,$5A のとき、下の値がつかえる
DEF wSignWY         EQU $d002 ; 今の看板の高さ（HIDDEN_WY なら出ていない）
DEF wSignPalSaved   EQU $d003 ; 1 なら、下にパレット7の元の色1・2がある
DEF wSignPalOrig    EQU $d004 ; 4バイト

; パレットのバッファ（WRAMバンク2）
DEF wBGPalsBase     EQU $d000 ; もとの色
DEF wBGPalsCur      EQU $d040 ; いまの色（BGP をかけたもの）
DEF PAL7_COLOR1     EQU 7 * 8 + 2

; ---------------------------------------------------------------- フック
SECTION "MapSignHookFrame", ROMX[KitSignFrame], BANK[$3a]
	call MapSignEveryFrame ; ldh a, [hGBC] / and a のかわり（そのあとの ret z はそのまま）

SECTION "MapSignHookBorder", ROMX[KitSignBorder], BANK[$3a]
	ds 9, 0 ; 白黒の枠は書かない（あとで MapSignShow がクリスタルの枠にする）

SECTION "MapSignHookNamePos", ROMX[KitSignNamePos], BANK[$3a]
	call MapSignCenterName ; ld hl, $cda6 のかわり

SECTION "MapSignHookCopy", ROMX[KitSignCopyCall], BANK[$3a]
	call MapSignShow

SECTION "MapSignHookAttr", ROMX[KitSignAttr], BANK[$3a]
	ld c, SIGN_ATTR ; どのタイルもバンク1・パレット7
	ds 7, 0

SECTION "MapSignHookGlyph", ROMX[KitSignGlyphPut], BANK[$3a]
	call MapSignGlyphPut ; 文字の地を色1（看板の色）にする
	ds 2, 0

; PrepareOAMData の最後（VBlank の中）。看板の出入りと、スプライトをかくす
SECTION "MapSignSpritesHook", ROMX[$4996], BANK[$01]
IF DEF(V_SHODAI)
	ld hl, MapSignOAMTail
	ld b, BANK(MapSignOAMTail)
ELSE
	ld hl, FwOAMTail ; 連れ歩きの白い下じき（follow.asm）のあと、MapSignOAMTail へ
	ld b, BANK(FwOAMTail)
ENDC
	jp Bankswitch

; ---------------------------------------------------------------- 本体
SECTION "MapSignCrystal", ROMX, BANK[$3a]

MapSignFrameGFX:
INCLUDE "gfx/map_sign_frame.inc"
MapSignFrameGFXEnd:

; 名前を真ん中に（クリスタルと同じ: (20 - 文字数) / 2）。hl = 置く場所
MapSignCenterName:
	ld hl, wSignName
	ld c, 0
.count
	ld a, [hli]
	cp $50 ; おわり
	jr z, .counted
	inc c
	jr .count
.counted
	ld a, SCREEN_WIDTH
	sub c
	jr nc, .ok
	xor a
.ok
	srl a
	ld c, a
	ld b, 0
	ld hl, wSignBuffer + 2 * SCREEN_WIDTH
	add hl, bc
	ret

; 文字の1行をVRAMに（地を色1、字を色3）。b = 字の1bpp、de = VRAM
MapSignGlyphPut:
	ld a, $ff
	ld [de], a
	inc de
	ld a, b
	ld [de], a
	inc de
	ret

; 看板を出す: 枠のタイルを読みこみ、バッファに枠を書き、色をかえて、キットの処理でウインドウへ
MapSignShow:
	call MapSignLoadFrameGFX
	call MapSignPlaceFrame
	call MapSignSetPalette
	di
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	ld a, $a5
	ld [wSignMagic], a
	ld a, $5a
	ld [wSignMagic + 1], a
	ld a, HIDDEN_WY ; 下から出てくる
	ld [wSignWY], a
	ld a, 1
	ldh [rSVBK], a
	ei
	jp KitSignCopy ; （最後にパレットを全部送りなおすようにもなる）

MapSignLoadFrameGFX:
	ld hl, MapSignFrameGFX
	ld de, $9000 + (SIGN_TILE + 1) * 16
	ld c, MapSignFrameGFXEnd - MapSignFrameGFX
.loop
	ld a, [hli]
	ld b, a
	di
	ld a, 1
	ldh [rVBK], a
	call MapSignWaitVRAM
	ld a, b
	ld [de], a
	xor a
	ldh [rVBK], a
	ei
	inc de
	dec c
	jr nz, .loop
	ret

; LY がVBlankでなければ、HBlankのはじまりまで待つ（キットと同じ）
MapSignWaitVRAM:
	ldh a, [rLY]
	cp $90
	jr c, .wait
	cp 152
	ret c
.wait
	ldh a, [rSTAT]
	and $02
	jr z, .wait
.wait2
	ldh a, [rSTAT]
	and $02
	jr nz, .wait2
	ret

; バッファ（20×4）にクリスタルの枠を書く。空白（$7F）は看板の中のタイルに
MapSignPlaceFrame:
	ld hl, wSignBuffer
	ld [hl], SIGN_TILE + 1
	inc hl
	ld a, SIGN_TILE + 2
	call .TopBottom
	ld [hl], SIGN_TILE + 4
	ld hl, wSignBuffer + 1 * SCREEN_WIDTH
	ld [hl], SIGN_TILE + 5
	ld hl, wSignBuffer + 1 * SCREEN_WIDTH + SCREEN_WIDTH - 1
	ld [hl], SIGN_TILE + 11
	ld hl, wSignBuffer + 2 * SCREEN_WIDTH
	ld [hl], SIGN_TILE + 6
	ld hl, wSignBuffer + 2 * SCREEN_WIDTH + SCREEN_WIDTH - 1
	ld [hl], SIGN_TILE + 12
	ld hl, wSignBuffer + 3 * SCREEN_WIDTH
	ld [hl], SIGN_TILE + 7
	inc hl
	ld a, SIGN_TILE + 8
	call .TopBottom
	ld [hl], SIGN_TILE + 10
; 中の空白
	ld hl, wSignBuffer
	ld c, 4 * SCREEN_WIDTH
.fill
	ld a, [hl]
	cp $7f ; 空白
	jr nz, .next
	ld [hl], SIGN_FILL
.next
	inc hl
	dec c
	jr nz, .fill
	ret

; a, a, a+1, a+1 のくりかえしではなく、クリスタルと同じ (a+1)×2, a×2, ... を18マス
.TopBottom:
	ld c, (SCREEN_WIDTH - 2) / 4 + 1
	jr .enter
.cont
	ld [hli], a
	ld [hli], a
.enter
	inc a
	ld [hli], a
	ld [hli], a
	dec a
	dec c
	jr nz, .cont
	ret

DEF SIGN_COLOR1 EQU 31 | 31 << 5 | 16 << 10 ; うすい黄色
DEF SIGN_COLOR2 EQU 14 | 9 << 5 | 0 << 10   ; 茶色

; ※ スタックは $DFxx（WRAMのバンクがかわる所）にあるので、
;    WRAMバンクを1以外にしているあいだは、call / push / pop を使わない。

; hl に看板の色1・2を書く
MACRO put_sign_colors
	ld a, LOW(SIGN_COLOR1)
	ld [hli], a
	ld a, HIGH(SIGN_COLOR1)
	ld [hli], a
	ld a, LOW(SIGN_COLOR2)
	ld [hli], a
	ld [hl], HIGH(SIGN_COLOR2)
ENDM

; hl の4バイトを bcde に
MACRO load_bcde
	ld a, [hli]
	ld b, a
	ld a, [hli]
	ld c, a
	ld a, [hli]
	ld d, a
	ld e, [hl]
ENDM

; z: bcde が看板の色（a はこわれる）
MACRO bcde_is_sign_colors
	ld a, b
	cp LOW(SIGN_COLOR1)
	jr nz, .\@
	ld a, c
	cp HIGH(SIGN_COLOR1)
	jr nz, .\@
	ld a, d
	cp LOW(SIGN_COLOR2)
	jr nz, .\@
	ld a, e
	cp HIGH(SIGN_COLOR2)
.\@
ENDM

; パレット7の色1・2を看板の色に（元の色をとっておく）
MapSignSetPalette:
	di
	ld a, 2
	ldh [rSVBK], a
	ld hl, wBGPalsBase + PAL7_COLOR1
	load_bcde
	ld hl, wBGPalsBase + PAL7_COLOR1
	put_sign_colors
	ld hl, wBGPalsCur + PAL7_COLOR1
	put_sign_colors
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
; もう看板の色になっていたら（続けて出た時）、元の色はそのまま
	bcde_is_sign_colors
	jr z, .done
	ld hl, wSignPalOrig
	ld a, b
	ld [hli], a
	ld a, c
	ld [hli], a
	ld a, d
	ld [hli], a
	ld [hl], e
	ld a, 1
	ld [wSignPalSaved], a
.done
	ld a, 1
	ldh [rSVBK], a
	ei
	jp MapSignUploadPals

; 毎フレーム（キットの看板の処理のはじめ）。看板が引っこんだら、パレットを元にもどす
MapSignEveryFrame:
	ldh a, [hIsGBC]
	and a
	ret z
	di
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	ld a, [wSignPalSaved]
	dec a
	jr nz, .done ; とっておいた色がない
; まだ看板が出ている（出入りの途中も）なら、まだもどさない
	ld a, [wSignMagic]
	cp $a5
	jr nz, .hidden
	ld a, [wSignMagic + 1]
	cp $5a
	jr nz, .hidden
	ld a, [wSignWY]
	cp HIDDEN_WY
	jr c, .done
.hidden
	xor a
	ld [wSignPalSaved], a
; マップがかわってパレットが読みなおされていたら、もどさない
	ld a, 2
	ldh [rSVBK], a
	ld hl, wBGPalsBase + PAL7_COLOR1
	load_bcde
	bcde_is_sign_colors
	jr nz, .done
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	ld hl, wSignPalOrig
	load_bcde
	ld a, 2
	ldh [rSVBK], a
	ld hl, wBGPalsBase + PAL7_COLOR1
	ld a, b
	ld [hli], a
	ld a, c
	ld [hli], a
	ld a, d
	ld [hli], a
	ld [hl], e
	ld hl, wBGPalsCur + PAL7_COLOR1
	ld a, b
	ld [hli], a
	ld a, c
	ld [hli], a
	ld a, d
	ld [hli], a
	ld [hl], e
	ld a, 1
	ldh [rSVBK], a
	ei
	call MapSignUploadPals
	jr .ret
.done
	ld a, 1
	ldh [rSVBK], a
	ei
.ret
	ldh a, [hIsGBC]
	and a
	ret

; パレットのバッファ（$D000）から、パレットを作りなおして送る（カラー化の処理 3B:6156）
MapSignUploadPals:
	ld hl, $6156
	ld b, $3b
	jp Bankswitch

; PrepareOAMData の最後（VBlank の中、バンク1からとんでくる）
MapSignOAMTail::
	ldh a, [rSVBK]
	ld e, a ; 元のWRAMバンク（スタックは使えない）
	ld a, SIGN_WRAM_BANK
	ldh [rSVBK], a
	ld b, HIDDEN_WY
	ld a, [wSignMagic]
	cp $a5
	jr nz, .off
	ld a, [wSignMagic + 1]
	cp $5a
	jr nz, .off
	ld a, [wSignWY]
	ld b, a
	ldh a, [hWY]
	cp MAP_SIGN_WY
	jr z, .shown
	cp HIDDEN_WY
	jr nz, .cancel ; ほかの窓（話す時など）が使っている
.goingDown
	ld a, b
	cp HIDDEN_WY
	jr nc, .off ; まだ出はじめていない（キットが出す前）
; 引っこむ
	add SLIDE_STEP
	cp HIDDEN_WY
	jr c, .setWY
	jr .cancel
.shown
	ld a, [wMapSignTimer]
	and a
	jr z, .goingDown
; 出てくる
	ld a, b
	sub SLIDE_STEP
	cp MAP_SIGN_WY
	jr nc, .setWY
	ld a, MAP_SIGN_WY
.setWY
	ld [wSignWY], a
	ldh [rWY], a
	ld b, a
	jr .off
.cancel
	ld a, HIDDEN_WY
	ld [wSignWY], a
	ld b, a
	xor a
	ld [wSignMagic], a
.off
	ld a, e
	ldh [rSVBK], a
	ld a, b
	cp HIDDEN_WY
	call c, MapSignHideSprites

; ここから元の PrepareOAMData の最後と同じ
.clearUnused
	ld a, [wMovementFlags]
	bit BIT_LEDGE_OR_FISHING, a
	ld c, LOW(wShadowOAMEnd)
	jr z, .clear
	ld c, LOW(wShadowOAMSprite36)
.clear
	ldh a, [hOAMBufferOffset]
	cp c
	ret nc
	ld l, a
	ld h, HIGH(wShadowOAM)
	ld a, c
	ld de, 4
	ld b, $a0
.clearLoop
	ld [hl], b
	add hl, de
	cp l
	jr nz, .clearLoop
	ret

; b = 看板の高さ。看板の行にかかるスプライトをかくす
MapSignHideSprites:
	ld a, b
	add OAM_Y_OFS - 8 + 1
	ld b, a
	ldh a, [hOAMBufferOffset]
	and a
	ret z
	ld c, a
	ld hl, wShadowOAM
.loop
	ld a, [hl]
	cp b
	jr c, .next
	ld [hl], $a0 ; 画面の外
.next
	ld a, l
	add 4
	ld l, a
	cp c
	jr c, .loop
	ret

