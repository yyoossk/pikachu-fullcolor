; ゲームコーナーの 景品交換所：わざマシンに わざの 名前も 出す
; ・一覧：「わざマシン２３」の 下の 行に「りゅうのいかり」（名前の 行は 4・6・8、わざは 5・7・9行め）
; ・確認：「わざマシン２３　りゅうのいかりで　いいんだね？」
; (GetPrizeMenuId and HandlePrizeChoice, engine/events/prize_menu.asm)

; the three TM prizes: item names at (2, 4/6/8), move names at (3, 5/7/9)
KitPrizeTMNames:
	ld hl, wPrize1
	decoord 2, 4
	ld c, 3
.loop
	push bc
	push hl
	push de
	ld a, [hl]
	ld [wNamedObjectIndex], a
	call GetItemName
	pop hl ; coord
	push hl
	call PlaceString
	pop hl
	push hl
	ld bc, SCREEN_WIDTH + 1
	add hl, bc
	push hl
	call KitPrizeGetMoveName
	pop hl
	call PlaceString
	pop hl
	ld bc, 2 * SCREEN_WIDTH
	add hl, bc
	ld d, h
	ld e, l
	pop hl
	inc hl
	pop bc
	dec c
	jr nz, .loop
	ret

; [wNamedObjectIndex] = TM item → wNameBuffer = "わざマシン２３　りゅうのいかり"
; ([wNamedObjectIndex] stays the item, for GiveItem)
KitPrizeTMName:
	call GetItemName
	ld hl, wNameBuffer
	ld de, wStringBuffer
	ld bc, NAME_BUFFER_LENGTH
	call CopyData
	call KitPrizeGetMoveName ; wNameBuffer = the move
	ld hl, wStringBuffer
.findEnd
	ld a, [hli]
	cp '@'
	jr nz, .findEnd
	dec hl
	ld [hl], '　'
	inc hl
	ld de, wNameBuffer
.copy
	ld a, [de]
	inc de
	ld [hli], a
	cp '@'
	jr nz, .copy
	ld hl, wStringBuffer
	ld de, wNameBuffer
	ld bc, NAME_BUFFER_LENGTH
	jp CopyData

; [wNamedObjectIndex] = TM item → de = wNameBuffer = the move's name ([wNamedObjectIndex] kept)
KitPrizeGetMoveName:
	ld a, [wNamedObjectIndex]
	push af
	sub TM01 - 1 ; TM number
	ld [wTempTMHM], a
	farcall TMToMove
	ld a, [wTempTMHM]
	ld [wNamedObjectIndex], a
	call GetMoveName
	pop af
	ld [wNamedObjectIndex], a
	ld de, wNameBuffer
	ret
