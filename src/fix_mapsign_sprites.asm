; variants: v s f sf x sx xf sxf
; 場所の名前（画面の下の看板）が出ているあいだ、人などのスプライトが看板の上にかさならないようにする。
; PrepareOAMData の最後（つかわない OAM を消す所）を、バンク$3A のこの処理にかえて、
; 看板の行（画面のY 112〜）にかかるスプライトをかくしてから、元どおり消す。

DEF wMapSignTimer EQU $d6a4 ; キットの看板の、のこり時間（0 なら出ていない）
DEF MAP_SIGN_WY   EQU $70
DEF SIGN_HIDE_Y   EQU MAP_SIGN_WY + OAM_Y_OFS - 8 + 1 ; これ以上のYのスプライトは、看板にかかる
DEF HIDDEN_Y      EQU $a0

SECTION "MapSignSpritesHook", ROMX[$4996], BANK[$01]
	ld hl, MapSignOAMTail
	ld b, BANK(MapSignOAMTail)
	jp Bankswitch

SECTION "MapSignSprites", ROMX, BANK[$3a]
MapSignOAMTail:
	ldh a, [hWY]
	cp MAP_SIGN_WY
	jr nz, .clearUnused
	ld a, [wMapSignTimer]
	and a
	jr z, .clearUnused
	ldh a, [hOAMBufferOffset]
	and a
	jr z, .clearUnused
	ld c, a
	ld hl, wShadowOAM
.hideLoop
	ld a, [hl]
	cp SIGN_HIDE_Y
	jr c, .next
	ld [hl], HIDDEN_Y
.next
	ld a, l
	add 4
	ld l, a
	cp c
	jr c, .hideLoop

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
	ld b, HIDDEN_Y
.clearLoop
	ld [hl], b
	add hl, de
	cp l
	jr nz, .clearLoop
	ret
