; フレンドリィショップで 買う とき：カーソルの ある 道具の 説明を 画面の 下に 出す（金・銀と 同じ。
; 説明は リュックの 画面と 同じ：MartPrintDescription（bag_screen.asm の BagPrintItemDescription））。
; カーソルを 動かす たびに 説明を かきかえる ため、PRICEDITEMLISTMENU の リストでは 上下も
; wMenuWatchedKeys に 入れる。HandleMenuInput が 上下で もどると、DisplayListMenuIDLoop は 上下を
; スクロールと して あつかうので、カーソルが 動いた ときは 先に wListScrollOffset を 逆に ずらして おく
;（DisplayListMenuIDLoop の .checkOtherKeys が もどす）。カーソルが 動いて いない（いちばん 上・下で 押した）
; ときは 今までどおり スクロール する。
; (this file is in the same bank as ListMenuIconsShow / ListMenuIconsHide: engine/gfx/gsc_party_icons.asm)

; at the start of ListMenuIconsShow (each time the list is drawn)
KitMartListShow:
	ld a, [wListMenuID]
	cp PRICEDITEMLISTMENU
	ret nz
	ld a, PAD_A | PAD_B | PAD_SELECT | PAD_UP | PAD_DOWN
	ld [wMenuWatchedKeys], a
	farcall MartPrintDescription
	ret

; at the start of ListMenuIconsHide (e = the keys HandleMenuInput returned; keep e)
KitMartListKeys:
	ld a, [wListMenuID]
	cp PRICEDITEMLISTMENU
	ret nz
	ld a, [wCurrentMenuItem]
	ld b, a
	ld a, [wLastMenuItem] ; (PlaceMenuCursor: the cursor before the key)
	cp b
	ret z ; not moved
	ld hl, wListScrollOffset
	bit B_PAD_DOWN, e
	jr nz, .down
	bit B_PAD_UP, e
	ret z
	; up: .checkOtherKeys decrements the scroll if it is not 0
	ld a, [hl]
	and a
	ret z
	inc [hl]
	ret
.down
	; down: .checkOtherKeys increments the scroll if scroll + 3 <= the count
	ld a, [hl]
	add 2
	ld b, a
	ld a, [wListCount]
	cp b
	ret c ; scroll + 2 > the count: it will not increment
	dec [hl]
	ret
