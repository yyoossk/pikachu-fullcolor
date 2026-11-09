; variants: v s f sf x sx xf sxf
; ずかんの タイプの ページ（キットの dex_types）に、進化の 条件を 足し、そのあとに 種族値の ページを 足す。
;   1ページめ: 説明（今までどおり）  ▼ → A
;   2ページめ: 下の わく = 「タイプ１／ほのお」「タイプ２／ひこう」（今までどおり）
;              右上（たかさ・おもさの 所）= 「しんか」と その 条件
;                （レベル16・かみなりのいし・つうしんこうかん・なし。イーブイのように いくつも ある時は 3行に）
;              ▼ → A（B なら とじる）
;   3ページめ: 下の わく = 種族値
;                たいりょく ○○○  こうげき ○○○
;                ぼうぎょ   ○○○  すばやさ ○○○
;                とくしゅ   ○○○  ごうけい ○○○
;              A か B で とじる
; 進化の 条件は ROM の EvosMovesPointerTable（0E:75E8）から 読むので、151匹そろう版の レベル37進化も そのまま出る。

IF DEF(V_60FPS)
DEF KDS EQU $bf ; 60fps版は キットの ずかんの 処理が $BF うしろ
ELSE
DEF KDS EQU 0
ENDC
DEF KIT_DEX_TYPES_HOOK EQU $6f49 + KDS ; ld hl, coord 2,11 / ld de, KitDexTypeText / call PlaceString / ld hl, coord 7,11 / predef PrintMonType
DEF KitDexWaitAB       EQU $6f5f + KDS ; A か B を まつ（a = hJoy5 & (A|B)）
DEF KitDexTypeText     EQU $6f69 + KDS ; 「タイプ１／」「タイプ２／」
DEF EVOS_MOVES_PTRS    EQU $75e8 ; 0E:75E8 EvosMovesPointerTable
; TypeNames は PrintType_ の すぐ うしろ（PrintType_ + $0F。初代グラフィック版は バンク$26）

SECTION "DexInfoPageHook", ROMX[KIT_DEX_TYPES_HOOK], BANK[$30]
	call DexInfoPages
	ds 14, 0

SECTION "DexInfoPage", ROMX, BANK[$30]
DexInfoPages:
; 2ページめ: タイプ（今までどおり）と 進化
	hlcoord 2, 11
	ld de, KitDexTypeText
	call PlaceString
	hlcoord 7, 11
	ld a, $4b ; PrintMonTypePredef（wMonHeader も 読まれる）
	call Predef
	call .Evolution
	ld a, '▼'
	ldcoord_a 18, 16
	ld c, 10
	call DelayFrames
	call KitDexWaitAB
	bit B_PAD_B, a
	jr z, .page3
	pop hl ; B: キットの 待ちを とばして とじる
	ret
.page3
; 3ページめ: 種族値（このあと キットが A か B を まって とじる）
	hlcoord 1, 10
	lb bc, 7, 18
	call ClearScreenArea
	jp .Stats

; ---- 種族値
.Stats:
	hlcoord 1, 11
	ld de, .HPText
	ld bc, wMonHBaseHP
	call .Stat
	hlcoord 11, 11
	ld de, .AtkText
	ld bc, wMonHBaseAttack
	call .StatRight
	hlcoord 1, 13
	ld de, .DefText
	ld bc, wMonHBaseDefense
	call .Stat
	hlcoord 11, 13
	ld de, .SpdText
	ld bc, wMonHBaseSpeed
	call .StatRight
	hlcoord 1, 15
	ld de, .SpcText
	ld bc, wMonHBaseSpecial
	call .Stat
	; ごうけい（2バイト）
	ld hl, wMonHBaseHP
	ld b, 5
	xor a
	ld d, a
	ld e, a
.sum
	ld a, [hli]
	add e
	ld e, a
	jr nc, .noCarry
	inc d
.noCarry
	dec b
	jr nz, .sum
	ld hl, wBuffer
	ld a, d
	ld [hli], a
	ld [hl], e
	hlcoord 11, 15
	ld de, .TotalText
	call PlaceString
	hlcoord 16, 15
	ld de, wBuffer
	lb bc, 2, 3
	jp PrintNumber

; de = ラベル、bc = 値、hl = 置く所。数字（3けた、右よせ）は
; 左の 列は ラベルの 6マスあと（1〜9）、右の 列は 5マスあと（11〜18）
.StatRight:
	ld a, 5
	jr .stat
.Stat:
	ld a, 6
.stat
	push af
	push hl
	push bc
	call PlaceString
	pop de
	pop hl
	pop af
	ld c, a
	ld b, 0
	add hl, bc
	lb bc, 1, 3
	jp PrintNumber

.HPText:    db "たいりょく@"
.AtkText:   db "こうげき@"
.DefText:   db "ぼうぎょ@"
.SpdText:   db "すばやさ@"
.SpcText:   db "とくしゅ@"
.TotalText: db "ごうけい@"

; ---- 進化
.Evolution:
	; 右上（たかさ・おもさ）を けす
	hlcoord 9, 3
	lb bc, 6, 10
	call ClearScreenArea
	; 進化の データ（最大 3つ × 4バイト ＋ 0）を wBuffer に
	ld a, [wCurSpecies]
	dec a
	ld l, a
	ld h, 0
	add hl, hl
	ld de, EVOS_MOVES_PTRS
	add hl, de
	ld de, wBuffer
	ld bc, 2
	ld a, BANK(EvolutionAfterBattle)
	call FarCopyData
	ld hl, wBuffer
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld de, wBuffer
	ld bc, 13
	ld a, BANK(EvolutionAfterBattle)
	call FarCopyData
	; いくつ あるか
	ld hl, wBuffer
	ld c, 0
.count
	ld a, [hl]
	and a
	jr z, .counted
	inc c
	cp EVOLVE_ITEM
	ld de, 4
	jr z, .skip
	dec de
.skip
	add hl, de
	jr .count
.counted
	ld a, c
	cp 2
	jr nc, .many
	; 0こ・1こ: 「しんか」の 下に 条件
	push bc
	hlcoord 9, 6
	ld de, .EvoText
	call PlaceString
	pop bc
	ld a, c
	and a
	jr nz, .one
	hlcoord 9, 8
	ld de, .NoneText
	jp PlaceString
.one
	hlcoord 9, 8
	ld de, wBuffer
	jp .Condition
.many
	; いくつも（イーブイ）: 4・6・8行めに 1つずつ
	hlcoord 9, 4
	ld de, wBuffer
	ld b, 3
.manyLoop
	ld a, [de]
	and a
	ret z
	push bc
	push hl
	call .Condition ; de = 次の データ
	pop hl
	ld bc, 2 * SCREEN_WIDTH
	add hl, bc
	pop bc
	dec b
	jr nz, .manyLoop
	ret

; de = 進化の データ1つ、hl = 置く所。de = 次の データ
.Condition:
	ld a, [de]
	inc de
	cp EVOLVE_LEVEL
	jr z, .level
	cp EVOLVE_ITEM
	jr z, .item
	; つうしんこうかん
	inc de ; レベル
	inc de ; しんか後
	push de
	ld de, .TradeText
	call PlaceString
	pop de
	ret
.level
	push de
	push hl
	ld de, .LevelText
	call PlaceString
	ld h, b
	ld l, c
	pop af ; すてる
	pop de
	push de
	lb bc, LEFT_ALIGN | 1, 3
	call PrintNumber
	pop de
	inc de ; レベル
	inc de ; しんか後
	ret
.item
	ld a, [de]
	inc de
	inc de ; レベル
	inc de ; しんか後
	push de
	push hl
	ld b, a
	ld a, [wNamedObjectIndex]
	push af
	ld a, b
	ld [wNamedObjectIndex], a
	call GetItemName
	pop af
	ld [wNamedObjectIndex], a
	pop hl
	call PlaceString
	pop de
	ret

.EvoText:   db "しんか@"
.NoneText:  db "なし@"
.LevelText: db "レベル@"
.TradeText: db "つうしんこうかん@"
