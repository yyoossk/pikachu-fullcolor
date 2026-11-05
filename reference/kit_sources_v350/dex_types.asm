; ずかんの 説明の ページ：つかまえた ポケモンなら、右下に「▼」を 出して、A で タイプの ページ
;（説明の ところに「タイプ１／でんき」「タイプ２／ひこう」。殿堂入りの 画面と 同じ PrintMonType）。
; もう いちど A か B で とじる。B なら 最初から とじる。つかまえて いない ポケモンは 今までどおり。
; (ShowPokedexDataInternal: instead of its wait for A or B; wCurSpecies is the Pokemon)

KitDexWaitButton:
	; owned: the description is shown (the first letter of its first line)
	ld a, [wTileMap + 11 * SCREEN_WIDTH + 1]
	cp '　'
	jr z, KitDexWaitAB
	ld a, '▼'
	ldcoord_a 18, 16
	call KitDexWaitAB
	bit B_PAD_B, a
	ret nz
	; the types page
	hlcoord 1, 10
	lb bc, 7, 18
	call ClearScreenArea
	hlcoord 2, 11
	ld de, KitDexTypeText
	call PlaceString
	hlcoord 7, 11
	predef PrintMonType
	ld c, 10
	call DelayFrames
KitDexWaitAB:
	call JoypadLowSensitivity
	ldh a, [hJoy5]
	and PAD_A | PAD_B
	jr z, KitDexWaitAB
	ret

KitDexTypeText:
	db   "タイプ１／"
	next "タイプ２／@"
