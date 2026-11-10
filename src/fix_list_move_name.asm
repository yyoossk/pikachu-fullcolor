; variants: v s f sf x sx xf sxf
; 技思い出しおじさんで、手持ちのポケモンの技の一覧（MOVESLISTMENU）から技をえらぶと、
; 番号の大きい技（カブトプスの「きりさく」など）でフリーズするのを直す。
;   DisplayListMenuIDLoop は、えらんだものの名前を GetName でとるとき、名前の表のバンクを
;   いつも「道具の名前」のバンク（BANK(ItemNames) = 1）にしていた。技の名前（MoveNames）は
;   バンク4 にあるので、技の一覧ではちがうバンクのデータを名前としてさがしてしまい、
;   終わりの印（$50）のない長い「名前」を CopyToStringBuffer が写しつづけてメモリをこわしていた。
;   技の一覧のときは BANK(MoveNames)、ほかは今までどおり BANK(ItemNames) にする。

; DisplayListMenuIDLoop.skipGettingQuantity（$2C5E〜$2C6D）
;  元: ld a, [wCurItem] / ld [wNameListIndex], a / ld a, BANK(ItemNames) / ld [wPredefBank], a
;      call GetName / jr .storeChosenEntry
SECTION "ListMenuNameHook", ROM0[$2c5e]
	ld b, BANK(ListMenuGetName)
	ld hl, ListMenuGetName
	call Bankswitch
	jr @ + 2 + ($2c83 - ($2c5e + 10)) ; .storeChosenEntry
	ds 6, 0 ; もう使わない
	assert @ == $2c6e ; .pokemonList

SECTION "ListMenuGetName", ROMX
ListMenuGetName:
	ld a, [wCurItem]
	ld [wNameListIndex], a
	ld a, [wListMenuID]
	cp MOVESLISTMENU
	ld a, BANK(MoveNames)
	jr z, .gotBank
	ld a, BANK(ItemNames)
.gotBank
	ld [wPredefBank], a
	jp GetName
