; ボックスを選ぶ画面（ボックスをかえる）: 左上の わくを 2行 ふやして、カーソルの ある
; ボックスの ポケモンの 数を「なかみ　１２／３０」のように 出す（カーソルを 動かすと かわる）。
; 一覧の 名前は 元の 行の まま（2・4・…・16行め。上の 行は 濁点用）。
; (DisplayChangeBoxMenu calls KitBoxCounts after GetMonCountsForAllBoxes;
;  ChangeBox calls KitBoxMenuInput instead of HandleMenuInput: e = the keys)
KitBoxCounts:
	hlcoord 18, 2
	ld de, wBoxMonCounts
	ld bc, SCREEN_WIDTH * 2
	ld a, NUM_BOXES
.loop
	push af
	ld a, [de]
	and a ; is the box empty?
	jr z, .noBall
	ld [hl], $78 ; pokeball tile next to the box name
.noBall
	add hl, bc
	inc de
	pop af
	dec a
	jr nz, .loop
	hlcoord 1, 4
	ld de, KitBoxCountText
	jp PlaceString

KitBoxMenuInput:
.loop
	call KitBoxDrawCount
	ld a, PAD_A | PAD_B | PAD_UP | PAD_DOWN
	ld [wMenuWatchedKeys], a
	call HandleMenuInput
	ld e, a
	and PAD_A | PAD_B
	jr z, .loop
	ld a, PAD_A | PAD_B
	ld [wMenuWatchedKeys], a
	ret

; the count of the box at the cursor at (5, 4): "１２／３０"
KitBoxDrawCount:
	ld a, [wCurrentMenuItem]
	ld e, a
	ld d, 0
	ld hl, wBoxMonCounts
	add hl, de
	ld d, h
	ld e, l
	hlcoord 5, 4
	ld a, '　'
	ld [hli], a
	ld [hld], a
	lb bc, 1, 2
	call PrintNumber
	ld a, '／'
	ld [hli], a
	ld a, '０' + MONS_PER_BOX / 10
	ld [hli], a
	ld [hl], '０' + MONS_PER_BOX % 10
	ret

KitBoxCountText:
	db "なかみ@"
