; variants: v s f sf x sx xf sxf
; ずかんの タイプの ページ（キットの dex_types）に、種族値と 進化の 条件も 出す。
;   下の わく:  2行め（11行め） タイプ      「でんき」「くさ／どく」
;               4行め（13行め） たい ○○ こう ○○ ぼう ○○
;               6行め（15行め） すば ○○ とく ○○ けい ○○○
;   右上（たかさ・おもさの 所。このページだけ かわる）:
;               しんか ／ レベル16・かみなりのいし・つうしんこうかん・なし
;               （イーブイのように 進化が いくつも ある時は、条件を 3行に ならべる）
; 進化の 条件は ROM の EvosMovesPointerTable（0E:75E8）から 読むので、151匹そろう版の レベル37進化も そのまま出る。

IF DEF(V_60FPS)
DEF KIT_DEX_TYPES_HOOK EQU $6f49 + $bf
ELSE
DEF KIT_DEX_TYPES_HOOK EQU $6f49
ENDC
; TypeNames は PrintType_ の すぐ うしろ（PrintType_ + $0F。初代グラフィック版は バンク$26）
DEF EVOS_MOVES_PTRS   EQU $75e8 ; 0E:75E8 EvosMovesPointerTable

; キットの「タイプ１／ タイプ２／」と PrintMonType の かわり（17バイト）
SECTION "DexInfoPageHook", ROMX[KIT_DEX_TYPES_HOOK], BANK[$30]
	call DexInfoPage
	ds 14, 0

SECTION "DexInfoPage", ROMX, BANK[$30]
DexInfoPage:
	call GetMonHeader ; wCurSpecies → wMonHeader
	call .Types
	call .Stats
	jp .Evolution

; ---- タイプ
.Types:
	ld a, [wMonHType1]
	hlcoord 2, 11
	call .PrintType
	ld h, b
	ld l, c
.trim ; 名前のうしろの 空白を つめる
	dec hl
	ld a, [hl]
	cp '　'
	jr z, .trim
	inc hl
	ld a, [wMonHType1]
	ld b, a
	ld a, [wMonHType2]
	cp b
	ret z
	ld [hl], '／'
	inc hl
	ld a, [wMonHType2]
	; fallthrough
; a = タイプ、hl = 置く所。bc = 次の所
.PrintType:
	push hl
	ld l, a
	ld h, 0
	add hl, hl
	ld de, PrintType_ + $0f ; TypeNames
	add hl, de
	ld de, wBuffer
	ld bc, 2
	ld a, BANK(PrintType_)
	call FarCopyData
	ld hl, wBuffer
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld de, wBuffer
	ld bc, 8
	ld a, BANK(PrintType_)
	call FarCopyData
	pop hl
	ld de, wBuffer
	jp PlaceString

; ---- 種族値
.Stats:
	hlcoord 2, 13
	ld de, .HPText
	ld bc, wMonHBaseHP
	call .Stat
	ld de, .AtkText
	ld bc, wMonHBaseAttack
	call .Stat
	ld de, .DefText
	ld bc, wMonHBaseDefense
	call .Stat
	hlcoord 2, 15
	ld de, .SpdText
	ld bc, wMonHBaseSpeed
	call .Stat
	ld de, .SpcText
	ld bc, wMonHBaseSpecial
	call .Stat
	; けい（合計、2バイト）
	push hl
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
	pop hl
	ld de, .TotalText
	call PlaceString
	ld h, b
	ld l, c
	ld de, wBuffer
	lb bc, 2, 3
	jp PrintNumber

; de = ラベル、bc = 値、hl = 置く所。hl = 次の所（1マスあけて）
.Stat:
	push bc
	call PlaceString
	ld h, b
	ld l, c
	pop de
	lb bc, 1, 3
	call PrintNumber
	inc hl
	ret

.HPText:    db "たい@"
.AtkText:   db "こう@"
.DefText:   db "ぼう@"
.SpdText:   db "すば@"
.SpcText:   db "とく@"
.TotalText: db "けい@"

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
