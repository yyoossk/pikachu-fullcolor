; ゲームコーナーのカウンター：コインを「５０まい（１０００円）」か「５００まい（１００００円）」で買える
; (Gold/Silver's Celadon Game Corner; B cancels; called from GameCornerClerkText)
KitGameCornerClerk:
	farcall GameCornerDrawCoinBox
	ld hl, KitCoinsAskText
	call PrintText
	call SaveScreenTilesToBuffer1
	hlcoord 12, 7
	lb bc, 3, 6
	call TextBoxBorder
	hlcoord 14, 8
	ld de, KitCoinsMenuText
	call PlaceString
	farcall MapColorsRepredict ; CGB map colors: the menu box appears at once
	ld a, 8
	ld [wTopMenuItemY], a
	ld a, 13
	ld [wTopMenuItemX], a
	xor a
	ld [wCurrentMenuItem], a
	ld [wLastMenuItem], a
	ld [wMenuWatchMovingOutOfBounds], a
	inc a
	ld [wMaxMenuItem], a
	ld a, PAD_A | PAD_B
	ld [wMenuWatchedKeys], a
	ld hl, wStatusFlags5
	res BIT_NO_TEXT_DELAY, [hl]
	call HandleMenuInput
	push af
	ld c, 15
	call DelayFrames
	call LoadScreenTilesFromBuffer1AndRepredict
	pop af
	ld hl, KitCoinsDeclinedText
	bit B_PAD_B, a
	jr nz, .print
	ld a, [wCurrentMenuItem]
	ld e, a ; 0: 50 coins, 1: 500 coins
	; Can only get more coins if you
	; - have the Coin Case
	ld b, COIN_CASE
	push de
	call IsItemInBag
	pop de
	ld hl, KitCoinsNoCaseText
	jr z, .print
	; - have room in the Coin Case (up to 9990 / 9500 coins)
	ld a, $99
	ldh [hCoins], a
	ld a, $90
	ldh [hCoins + 1], a
	ld a, e
	and a
	jr z, .gotRoom
	ld a, $95
	ldh [hCoins], a
	xor a
	ldh [hCoins + 1], a
.gotRoom
	push de
	call HasEnoughCoins
	pop de
	ld hl, KitCoinsCaseFullText
	jr nc, .print
	; - have the money (1000 / 10000 yen)
	push de
	call .setPrice
	call HasEnoughMoney
	pop de
	ld hl, KitCoinsCantAffordText
	jr c, .print
	push de
	call .setPrice
	ld hl, hMoney + 2
	ld de, wPlayerMoney + 2
	ld c, 3
	predef SubBCDPredef
	pop de
	; receive the coins
	xor a
	ldh [hUnusedCoinsByte], a
	ld a, e
	and a
	ld a, $00
	ld b, $50
	ld hl, KitCoinsThanks50Text
	jr z, .gotCoins
	ld a, $05
	ld b, $00
	ld hl, KitCoinsThanks500Text
.gotCoins
	ldh [hCoins], a
	ld a, b
	ldh [hCoins + 1], a
	push hl
	ld de, wPlayerCoins + 1
	ld hl, hCoins + 1
	ld c, 2
	predef AddBCDPredef
	ld a, SFX_PURCHASE
	call PlaySoundWaitForCurrent
	farcall GameCornerDrawCoinBox
	pop hl
.print
	jp PrintText

.setPrice
; hMoney = 1000 (e = 0) or 10000 (e = 1) yen, BCD
	xor a
	ldh [hMoney + 2], a
	ld a, e
	and a
	ld a, $10
	ld b, $00
	jr z, .gotPrice
	xor a
	ld b, $01
.gotPrice
	ldh [hMoney + 1], a
	ld a, b
	ldh [hMoney], a
	ret

KitCoinsMenuText:
	db   "５０まい"
	next "５００まい@"

KitCoinsAskText:
	text "いらっしゃいませ！"
	line "ロケット　ゲーム　コーナーです"

	para "ゲームよう　コイン　ですか？"

	para "５０まい　１０００円"
	line "５００まい　１００００円　です！"

	para "なんまい　かいますか？"
	done

KitCoinsThanks50Text:
	text "はい！　まいど　あり！"
	line "コイン　５０まい　どうぞ！"
	done

KitCoinsThanks500Text:
	text "はい！　まいど　あり！"
	line "コイン　５００まい　どうぞ！"
	done

KitCoinsDeclinedText:
	text "<⋯>　いりませんか！"
	line "それでは　また　どうぞ！"
	done

KitCoinsCantAffordText:
	text "おかね　たりないよ！"
	done

KitCoinsCaseFullText:
	text "おっと<⋯>！"
	line "コインケースが　まんたんだ！"
	done

KitCoinsNoCaseText:
	text "あれ？　コインを　いれる"
	line "コインケースが　ないよ！"
	done
