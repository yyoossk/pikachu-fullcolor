; わざを 忘れさせる 画面（どの わざを わすれさせたい？）：カーソルの ある わざの タイプ・いりょく・めいちゅうを
; 右上の わくに 出す（バトルの わざの 枠と 同じ。いりょくが 0・1 の わざは「ー」）。
; (LearnMove's list: instead of HandleMenuInput; e = the keys. The moves are in wMoves.)

DEF KIT_FMI_X EQU 10
DEF KIT_FMI_Y EQU 2

KitForgetMenuInput:
	hlcoord KIT_FMI_X, KIT_FMI_Y
	lb bc, 4, 8
	call TextBoxBorder
.loop
	call KitForgetDrawInfo
	ld a, PAD_A | PAD_B | PAD_UP | PAD_DOWN
	ld [wMenuWatchedKeys], a
	call HandleMenuInput
	ld e, a
	and PAD_A | PAD_B
	jr z, .loop
	ld a, PAD_A | PAD_B
	ld [wMenuWatchedKeys], a
	ret

KitForgetDrawInfo:
	hlcoord KIT_FMI_X + 1, KIT_FMI_Y + 1
	lb bc, 4, 8
	call ClearScreenArea
	; the move's data (Moves) → wBuffer
	ld a, [wCurrentMenuItem]
	ld e, a
	ld d, 0
	ld hl, wMoves
	add hl, de
	ld a, [hl]
	and a
	ret z
	dec a
	ld hl, Moves
	ld bc, MOVE_LENGTH
	call AddNTimes
	ld de, wBuffer
	ld bc, MOVE_LENGTH
	ld a, BANK(Moves)
	call FarCopyData
	; the type (PrintMoveType reads wPlayerMoveType: keep the battle's value)
	ld a, [wPlayerMoveType]
	push af
	ld a, [wBuffer + MOVE_TYPE]
	ld [wPlayerMoveType], a
	hlcoord KIT_FMI_X + 1, KIT_FMI_Y + 2
	predef PrintMoveType
	pop af
	ld [wPlayerMoveType], a
	hlcoord KIT_FMI_X + 1, KIT_FMI_Y + 3
	ld de, KitFmiPowerText
	call PlaceString
	hlcoord KIT_FMI_X + 1, KIT_FMI_Y + 4
	ld de, KitFmiAccuracyText
	call PlaceString
	ld a, [wBuffer + MOVE_POWER]
	cp 2
	jr nc, .power
	ld a, 'ー'
	ldcoord_a KIT_FMI_X + 8, KIT_FMI_Y + 3
	jr .accuracy
.power
	hlcoord KIT_FMI_X + 6, KIT_FMI_Y + 3
	ld de, wBuffer + MOVE_POWER
	lb bc, 1, 3
	call PrintNumber
.accuracy
	ld a, [wBuffer + MOVE_ACC]
	call KitFmiPercent
	ld [wBuffer + MOVE_LENGTH], a
	hlcoord KIT_FMI_X + 6, KIT_FMI_Y + 4
	ld de, wBuffer + MOVE_LENGTH
	lb bc, 1, 3
	jp PrintNumber

; a = 命中（0〜255）→ a = ％（×100÷255 を 四捨五入。KitAccuracyPercent と 同じ）
KitFmiPercent:
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	push hl ; ×4
	add hl, hl
	add hl, hl
	add hl, hl
	push hl ; ×32
	add hl, hl ; ×64
	pop de
	add hl, de
	pop de
	add hl, de
	ld de, 127
	add hl, de
	ld c, 0
	ld de, -255
.div
	ld a, h
	and a
	jr nz, .sub
	ld a, l
	cp 255
	jr c, .done
.sub
	add hl, de
	inc c
	jr .div
.done
	ld a, c
	ret

KitFmiPowerText:
	db "いりょく@"
KitFmiAccuracyText:
	db "めいちゅう@"
