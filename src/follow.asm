; variants: v f x xf
; 連れ歩き（全ポケモン）: 赤緑青ピカチュウ連れ歩きキットを、ピカチュウ版の連れ歩き（ピカチュウ）のしくみで入れる。
;  ・手持ちの画面で SELECT をおしたポケモン（★。はじめは先頭）が、主人公の後ろを歩く。もう一度 SELECT でだれも歩かない。
;  ・連れ歩くのが最初のピカチュウなら、今までどおり（絵・色・声・表情・なつき度の反応など）。
;  ・ほかのポケモンなら、ピカチュウのスプライトの VRAM にそのポケモンの絵（キットの24タイル）を読み、
;    色はピカチュウの OBJ パレット（6本目）に書く。白い下じき（VRAMバンク1）をうしろに重ねる。
;    話しかけると、ふりむいて鳴き（PlayCry）、気持ちのアイコンを出して、キットの会話文案の会話をする。
;
; しくみ（ピカチュウ版の作り）:
;  ・wd471 の bit 7 は「最初のピカチュウがいる」→「連れ歩くのが最初のピカチュウで、ひんしでない」にする。
;    （ピカチュウのイベントの処理は bit 7 を見ているので、ほかのポケモンのときははたらかない）
;  ・あいている bit 4 =「連れ歩くポケモンがいて、ひんしでない」（出す・ついて歩く道のりを足す・動かすイベント）
;    bit 3 =「連れ歩くのが最初のピカチュウ以外」（キットの絵と色）
;  ・どのポケモンを連れ歩くか（セーブされる）: wFwMode 0 = 先頭、1 = 下の ID（おや ID・個体値）のポケモン、$FF = だれも
;    ならびかえ・あずけるなどで場所がかわっても、ID でさがす（いなくなったら先頭にもどる）

; ---------------------------------------------------------------- RAM
; セーブされる所のあき（元のゲームで使っていない）
DEF wFwMode     EQU $d3f5
DEF wFwID       EQU $d3f6 ; 3バイト: おや ID（2）・個体値の1バイトめ
DEF wFwID3      EQU $d3f3 ; 個体値の2バイトめ
; WRAMバンク7（看板と同じ。セーブされない）
DEF FW_WRAM_BANK EQU 7
DEF wFwVramDex  EQU $d010 ; VRAM に読んである絵（ずかん番号。0 = ピカチュウ）
DEF wFwPalDex   EQU $d011 ; OBJ パレット6に書いてある色（0 = ピカチュウ）
DEF wFwKitDex   EQU $d012 ; 今の連れ歩き（キットの絵のとき ずかん番号。0 = ピカチュウ・いない）
DEF wFwPalFace  EQU $d013 ; OBJ パレット6に書いてある色の向き（0 = 正面の色、1 = 後ろ・横の色）

DEF FW_GFX_BANK  EQU $2a ; 絵: 1バンクに 42匹
DEF FW_MASK_BANK EQU $2e ; 下じき: 1バンクに 85匹（下のビットだけ 192バイト）
DEF FW_MASKCOPY  EQU $7fc0 ; 下じきのバンクの中の、VRAMバンク1に書く処理
DEF FW_STAR_TILE EQU $24 ; ★のタイル（VRAMバンク1）
DEF FW_UNDERLAY_TILE EQU $0c ; 下じきのタイル（VRAMバンク1 の $0C〜$23）
DEF FW_SIGN_ADDR EQU $8000 + $25 * 16 ; 下じきのしるし（VRAMバンク1 のタイル $25 の最初の2バイト）

IF DEF(V_60FPS)
DEF FW_KS        EQU $20
DEF FW_TRYPIKA   EQU $42d3
ELSE
DEF FW_KS        EQU 0
DEF FW_TRYPIKA   EQU $4214
ENDC

; WRAMバンク7 を読む・書く（スタックは $DFxx なので、そのあいだ call / push / pop はしない）
MACRO fw_b7_read ; \1 = レジスタ, \2 = アドレス
	di
	ld a, FW_WRAM_BANK
	ldh [rSVBK], a
	ld a, [\2]
	ld \1, a
	ld a, 1
	ldh [rSVBK], a
	ei
ENDM
MACRO fw_b7_write ; \1 = アドレス, \2 = レジスタ
	di
	ld a, FW_WRAM_BANK
	ldh [rSVBK], a
	ld a, \2
	ld [\1], a
	ld a, 1
	ldh [rSVBK], a
	ei
ENDM

; ================================================================ フック
; 毎フレーム（IsSurfingPikachuInParty.checkForStarter）: IsStarterPikachuAliveInOurParty のかわりに
SECTION "FwHookFlags", ROM0[$3483]
	ld hl, FwUpdateFlags ; ld b, $3f はそのまま

; ShouldPikachuSpawn: 連れ歩くポケモンがいて、ひんしでなければ出す
SECTION "FwHookSpawn", ROMX[$44eb], BANK[$3f]
	call FwFollowerAliveCarry

; Func_fcc23（ついて歩く道のりを足すか）: bit 7 → bit 4
SECTION "FwHookFollowBit", ROMX[$4c43], BANK[$3f]
	bit 4, a

; TryApplyPikachuMovementData（イベントで主人公といっしょに動く）: bit 7 → bit 4
SECTION "FwHookTryMoveBit", ROMX[FW_TRYPIKA], BANK[$30]
	bit 4, a

; キットの走りおわり（出しなおすか）: bit 7 → bit 4、最初のピカチュウ → 連れ歩くポケモン
SECTION "FwHookRunBit", ROMX[$6f33 + FW_KS], BANK[$3a]
	bit 4, a
SECTION "FwHookRunAlive", ROMX[$6f42 + FW_KS], BANK[$3a]
	ld hl, FwFollowerAliveCarry

; ポケモンセンター（ジョーイさんのところへ歩く・ボールにもどる）
SECTION "FwHookCenter1", ROMX[$709c], BANK[$01]
	ld hl, FwFollowerAliveCarry
SECTION "FwHookCenter2", ROMX[$70d7], BANK[$01]
	ld hl, FwFollowerAliveCarry
SECTION "FwHookCenter3", ROMX[$7115], BANK[$01]
	ld hl, FwFollowerAliveCarry
SECTION "FwHookCenter4", ROMX[$7137], BANK[$01]
	ld hl, FwFollowerAliveCarry

; げんきのかけら・ふしぎなアメ: 連れ歩くポケモンなら、主人公の所から出す
SECTION "FwHookRespawn", ROMX[$406d], BANK[$0b]
	ld hl, FwIsWhichMonFollower

; マップの人の絵を読むとき、ピカチュウの所（VRAMの2つめ）にキットの絵を（ReadSpriteSheetData のかわりに FwHomeSheet）
SECTION "FwHookStill", ROMX[$410b], BANK[$05]
	call FwHomeSheet
SECTION "FwHookWalk", ROMX[$4116], BANK[$05]
	call FwHomeSheet

; LoadPikachuSpriteIntoVRAM（ポケモンセンターなど）: 絵のもと
SECTION "FwHookPikaSprite", ROMX[$58d0], BANK[$3f]
	call FwPikaSrc
	ds 3, 0

; 話しかけたとき（TalkToPikachu）
SECTION "FwHookTalk", ROMX[$5024], BANK[$3f]
	call FwTalkHook

; パレットを作りなおすとき（カラー化の処理 3B:6156）: OBJ パレット6を連れ歩きの色に
SECTION "FwHookOBPal", ROMX[$616f], BANK[$3b]
	call FwOBPal
	nop

; 手持ちの画面: HandlePartyMenuInput のはじめ（SELECT を受けつける・★）
SECTION "FwHookPartyPre", ROM0[$1206]
	call FwTrampolinePartyPre
	nop
	nop
; 手持ちの画面: ボタンをおしたあと（SELECT なら連れ歩きをえらぶ）
SECTION "FwHookPartyChoose", ROM0[$1229]
	ld hl, FwPartyChoose ; ld b, $3f はそのまま

; ホームのあき（RST のあと）: バンクをまたぐ入り口
SECTION "FwTrampolinePartyPre", ROM0[$0001]
FwTrampolinePartyPre:
	ld hl, FwPartyMenuPre
	ld b, BANK(FwPartyMenuPre)
	jr FwJpBankswitch
SECTION "FwJpBankswitch", ROM0[$0043]
FwJpBankswitch:
	jp Bankswitch

; ホームのあき（RST のあと、7バイトずつ）: 人の絵を読む（バンク5 の LoadStill/WalkingTilePattern から）
; FwSheet が carry なら de = 絵、h = バンクで 12タイル。nc なら元の ReadSpriteSheetData
SECTION "FwHomeSheet1", ROM0[$0009]
FwHomeSheet:
	ld hl, FwSheet
	ld b, BANK(FwSheet)
	jr FwHomeSheet2
SECTION "FwHomeSheet2", ROM0[$0011]
FwHomeSheet2:
	call Bankswitch
	jr c, FwHomeSheet3
	jr FwHomeSheet4
SECTION "FwHomeSheet3", ROM0[$0019]
FwHomeSheet3:
	ld b, h
	ld c, 12
	ret
SECTION "FwHomeSheet4", ROM0[$0021]
FwHomeSheet4:
	jp ReadSpriteSheetData

; ================================================================ バンク$3F（ピカチュウの処理のバンク）
SECTION "FwMain", ROMX, BANK[$3f]

; 連れ歩くポケモンの場所
; 出力: c = いない。nc なら a = 手持ちの番号（0〜5）、hl = wPartyMon1 + a*44
FwGetFollower::
	ld a, [wPartyCount]
	and a
	jr z, .none
	ld a, [wFwMode]
	cp $ff
	jr z, .none
	and a
	jr z, .first
	ld hl, wPartyMon1OTID
	ld c, 0
.loop
	ld a, [wPartyCount]
	cp c
	jr z, .notFound
	push hl
	ld a, [wFwID]
	cp [hl]
	jr nz, .next
	inc hl
	ld a, [wFwID + 1]
	cp [hl]
	jr nz, .next
	ld de, (wPartyMon1DVs - wPartyMon1OTID) - 1
	add hl, de
	ld a, [wFwID + 2]
	cp [hl]
	jr nz, .next
	inc hl
	ld a, [wFwID3]
	cp [hl]
	jr z, .found
.next
	pop hl
	ld de, wPartyMon2 - wPartyMon1
	add hl, de
	inc c
	jr .loop
.found
	pop hl
	jr .slot
.notFound
	xor a ; いなくなった: 先頭にもどす
	ld [wFwMode], a
.first
	ld c, 0
.slot
	ld a, c
	ld hl, wPartyMon1
	ld de, wPartyMon2 - wPartyMon1
	and a
	jr z, .done
.mul
	add hl, de
	dec c
	jr nz, .mul
.done
	and a ; nc
	ret
.none
	scf
	ret

; c = 手持ちの番号、hl = そのポケモン → carry: 最初のピカチュウ（hl・c はそのまま）
FwIsStarterPika:
	ld a, [hl]
	cp STARTER_PIKACHU
	jr nz, .no
	push hl
	push bc
	ld de, wPartyMon1OTID - wPartyMon1
	add hl, de
	ld a, [wPlayerID]
	cp [hl]
	jr nz, .nop
	inc hl
	ld a, [wPlayerID + 1]
	cp [hl]
	jr nz, .nop
	ld a, c
	add a
	add c
	add a ; *6
	ld e, a
	ld d, 0
	ld hl, wPartyMonOT
	add hl, de
	ld de, wPlayerName
	ld b, NAME_LENGTH - 1
.name
	ld a, [de]
	inc de
	cp [hl]
	inc hl
	jr nz, .nop
	dec b
	jr nz, .name
	pop bc
	pop hl
	scf
	ret
.nop
	pop bc
	pop hl
.no
	and a
	ret

; 連れ歩きのようす
; 出力: d = wd471 の bit 3・4、a = キットの絵のときずかん番号（1〜151。0 = ちがう）、
;       carry = 最初のピカチュウで、ひんしでない
FwFollowerInfo::
	ld d, 0
	call FwGetFollower
	jr c, .none
	ld c, a
	push hl
	inc hl
	ld a, [hli]
	or [hl]
	pop hl
	jr z, .fainted
	set 4, d
.fainted
	push de
	call FwIsStarterPika
	pop de
	jr c, .starter
	ld a, [wCurMap] ; 海の家のピカチュウ（人）は、ピカチュウの絵のままにしたいので、連れ歩かない
	cp SUMMER_BEACH_HOUSE
	jr z, .none
	ld a, [hl]
	dec a
	ld c, a
	ld b, 0
	ld hl, FwDexTable
	add hl, bc
	ld a, [hl]
	inc a
	jr z, .none
	set 3, d
	and a
	ret
.starter
	xor a
	bit 4, d
	ret z
	scf
	ret
.none
	ld d, 0
	xor a
	ret

; carry: 連れ歩くポケモンがいて、ひんしでない（ShouldPikachuSpawn など、IsStarterPikachuAliveInOurParty のかわり）
FwFollowerAliveCarry::
	call FwFollowerInfo
	bit 4, d
	ret z
	scf
	ret

; carry: wWhichPokemon が連れ歩くポケモン（IsThisPartyMonStarterPikachu のかわり。げんきのかけらなど）
FwIsWhichMonFollower::
	call FwGetFollower
	ret c
	ld b, a
	ld a, [wWhichPokemon]
	cp b
	jr z, .yes
	and a
	ret
.yes
	scf
	ret

; 毎フレーム: wd471 の bit 3・4 を作り、絵と色がちがっていたら読みなおす。
; carry: 最初のピカチュウを連れ歩いている（よび出し元が bit 7 を立てる）
FwUpdateFlags::
	call FwFollowerInfo
	push af ; carry
	ld e, a
	ld hl, wd471
	ld a, [hl]
	and ~((1 << 3) | (1 << 4))
	or d
	ld [hl], a
	fw_b7_write wFwKitDex, e
; 絵（文字を出していないときだけ）
	ld a, [wFontLoaded]
	bit BIT_FONT_LOADED, a
	jr nz, .pal
	ld a, [wSpriteSet]
	cp SPRITE_PIKACHU
	jr nz, .pal
	fw_b7_read c, wFwVramDex
	ld a, e
	cp c
	jr z, .pal
	push de
	ldh a, [hVRAMSlot]
	push af
	xor a
	ldh [hVRAMSlot], a
	callfar LoadStillTilePattern
	xor a
	ldh [hVRAMSlot], a
	callfar LoadWalkingTilePattern
	pop af
	ldh [hVRAMSlot], a
	pop de
.pal
; 色（歩いているときだけ連れ歩きの色。自転車・なみのりはピカチュウの色：なみのりピカチュウ）
	ld a, [wWalkBikeSurfState]
	and a
	jr z, .walk
	ld e, 0
.walk
	ld d, 0 ; 色の向き（FwOBPal と同じ決めかた）
	ld a, e
	and a
	jr z, .face
	ld a, [wSpritePikachuStateData1FacingDirection]
	and a
	jr z, .face
	inc d
.face
	fw_b7_read c, wFwPalDex
	ld a, e
	cp c
	jr nz, .rebuild
	fw_b7_read c, wFwPalFace
	ld a, d
	cp c
	jr z, .done
.rebuild
	ld hl, $6156 ; パレットを作りなおして送る（FwOBPal が色を書く）
	ld b, $3b
	call Bankswitch
.done
	pop af
	ret

; マップの人の絵を読む（バンク5の ReadSpriteSheetData のまえ）
; スタック: +0 Bankswitch へもどる +2 バンク +4 FwHomeSheet2 +6 よんだ所（LoadStillTilePattern なら止まりの絵）
; 出力: carry なら de = 絵、h = バンク（12タイル）。nc なら元のまま
; 止まりの絵のときだけ、下じきも読む
FwSheet::
	ldh a, [hVRAMSlot]
	and a
	ret nz
	ld a, [wSpriteSet]
	cp SPRITE_PIKACHU
	jr nz, .no
	ld hl, sp + 6
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld de, -(LoadStillTilePattern + 9) ; call FwHomeSheet のあと
	add hl, de
	ld a, h
	or l
	sub 1 ; carry: 止まりの絵
	sbc a ; a = $ff: 止まりの絵
	push af
	call FwFollowerInfo
	ld c, a
	pop af
	and a
	jr z, .gfx
	fw_b7_write wFwVramDex, c
	ld a, c
	and a
	jr z, .gfx
	push bc
	call FwUnderlayLoaded
	call nz, FwLoadUnderlay
	pop bc
.gfx
	ld a, c
	and a
	ret z ; nc: ピカチュウ
	dec a
	call FwGfxPtr
	scf
	ret
.no
	and a
	ret

; a = ずかん番号−1 → de = 絵、h = バンク
FwGfxPtr:
	ld h, FW_GFX_BANK
.div
	cp 42
	jr c, .got
	sub 42
	inc h
	jr .div
.got
	push hl
	ld l, a
	add a
	add l ; *3
	ld l, a
	ld h, 0
REPT 7
	add hl, hl
ENDR
	ld a, h
	add HIGH($4000)
	ld d, a
	ld e, l
	pop hl
	ret

; z: c（ずかん番号）の下じきが、もう VRAMバンク1 にある（しるしのタイルの2バイトが c, ~c）
; マップのつながりなどで、同じ下じきを読みなおして重くならないように
FwUnderlayLoaded:
	ld hl, FW_SIGN_ADDR
	di
	ld a, 1
	ldh [rVBK], a
	call FwWaitVRAM
	ld a, [hli]
	ld e, [hl]
	ld d, a
	xor a
	ldh [rVBK], a
	ei
	ld a, d
	cp c
	ret nz
	ld a, c
	cpl
	cp e
	ret

; c = ずかん番号 → 白い下じきを VRAMバンク1 の $80C0〜（24タイル）に。しるしも書く
FwLoadUnderlay:
	push bc
	call .copy
	pop bc
	ld hl, FW_SIGN_ADDR
	di
	ld a, 1
	ldh [rVBK], a
	call FwWaitVRAM
	ld a, c
	ld [hli], a
	cpl
	ld [hl], a
	xor a
	ldh [rVBK], a
	ei
	ret
.copy
	ld a, c
	dec a
	ld b, FW_MASK_BANK
.div
	cp 85
	jr c, .got
	sub 85
	inc b
	jr .div
.got
	ld l, a
	add a
	add l ; *3
	ld l, a
	ld h, 0
REPT 6
	add hl, hl
ENDR
	ld a, h
	add HIGH($4000)
	ld d, a
	ld e, l
	ld hl, FW_MASKCOPY
	jp Bankswitch

; LoadPikachuSpriteIntoVRAM の絵のもと（de = 絵、b = バンク、c = 12）
FwPikaSrc:
	ld a, [wd471]
	bit 3, a
	jr z, .pika
	call FwFollowerInfo
	and a
	jr z, .pika
	dec a
	call FwGfxPtr
	ld b, h
	ld c, 12
	ret
.pika
	ld de, PikachuSprite
	lb bc, BANK(PikachuSprite), 12
	ret

; 話しかけたとき: 最初のピカチュウなら今までどおり。ほかは FwTalk
FwTalkHook:
	call FwFollowerInfo
	jp c, MapSpecificPikachuExpression
	ld a, d
	and 1 << 3
	jp z, MapSpecificPikachuExpression
	pop hl ; TalkToPikachu にはもどらない
	ld hl, FwTalk
	ld b, BANK(FwTalk)
	jp Bankswitch

; FwTalk から: 連れ歩くポケモンの番号を e に（carry = いない）
FwGetFollowerE::
	call FwGetFollower
	ld e, a
	ret

; ---------------------------------------------------------------- 手持ちの画面
; HandlePartyMenuInput のはじめ（元の ld a, 1 / ld [wMenuWrappingEnabled], a のかわり）
; スタック: +0 Bankswitch へもどる +2 Bankswitch がとっておいたバンク +4 $1209
;           +6 DisplayPartyMenu の push af +8 HandlePartyMenuInput をよんだ所
FwPartyMenuPre:
	ld a, 1
	ld [wMenuWrappingEnabled], a
	ld a, [wIsInBattle]
	and a
	ret nz
	ld a, [wBankswitchHomeSavedROMBank]
	cp BANK(StartMenu_Pokemon)
	ret nz
	ld hl, sp + 9
	ld a, [hld]
	cp HIGH(StartMenu_Pokemon)
	ret c
	cp HIGH(StartMenu_Pokemon) + 4
	ret nc
	ld hl, wMenuWatchedKeys
	set B_PAD_SELECT, [hl]
	jp FwDrawStar

; HandlePartyMenuInput: ボタンをおしたあと（IsThisPartyMonStarterPikachu のかわり）
; スタック: +0 Bankswitch へもどる +2 バンク +4 $1231 +6 おしたボタン（push af） +8 …
FwPartyChoose:
	ld hl, sp + 7
	bit B_PAD_SELECT, [hl]
	jp z, IsThisPartyMonStarterPikachu
	ld a, [wMenuItemToSwap]
	and a
	call z, FwToggle
; HandlePartyMenuInput をはじめからやりなおす（おしたボタンの push af をすてる）
	pop hl
	pop hl ; h = もどすバンク
	pop de
	pop de
	ld de, HandlePartyMenuInput
	push de
	push hl
	jp Bankswitch + 12 ; pop bc / バンクをもどす / ret

; SELECT: wWhichPokemon を連れ歩く（もう連れ歩いていれば、だれも連れ歩かない）
FwToggle:
	call FwGetFollower
	ld c, a
	ld a, [wWhichPokemon]
	jr c, .set
	cp c
	jr nz, .set
	ld a, $ff
	ld [wFwMode], a
	jr .done
.set
	ld hl, wPartyMon1OTID
	ld bc, wPartyMon2 - wPartyMon1
	call AddNTimes
	ld a, [hli]
	ld [wFwID], a
	ld a, [hl]
	ld [wFwID + 1], a
	ld de, (wPartyMon1DVs - wPartyMon1OTID) - 1
	add hl, de
	ld a, [hli]
	ld [wFwID + 2], a
	ld a, [hl]
	ld [wFwID3], a
	ld a, 1
	ld [wFwMode], a
	ld a, 3 ; 主人公の所から出す（げんきのかけらと同じ）
	ld [wPikachuSpawnState], a
.done
	ld a, $90 ; SFX_PRESS_AB（ボタンの音）
	call PlaySound
	jp FwDrawStar

; 連れ歩くポケモンに赤い ★（スプライト。手持ちの各行の左上）
FwDrawStar:
; タイル（VRAMバンク1）
	ld de, FwStarGFX
	ld hl, $8000 + FW_STAR_TILE * 16
	ld c, 8
.tile
	ld a, [de]
	inc de
	ld b, a
	di
	ld a, 1
	ldh [rVBK], a
	call FwWaitVRAM
	ld a, b
	ld [hli], a
	xor a
	ld [hli], a
	ldh [rVBK], a
	ei
	dec c
	jr nz, .tile
; パレット（OBJ 7）
	ld hl, FwStarPal
	ld c, 8
	di
	call FwWaitVRAM
	ld a, $80 | (7 * 8)
	ldh [rOBPI], a
.pal
	call FwWaitVRAM
	ld a, [hli]
	ldh [rOBPD], a
	dec c
	jr nz, .pal
	ei
; OAM（いちばん最後）
	call FwGetFollower
	ld hl, wShadowOAM + 39 * 4
	jr c, .hide
	swap a
	add 16
	ld [hli], a
	ld a, 8
	ld [hli], a
	ld a, FW_STAR_TILE
	ld [hli], a
	ld [hl], OAM_BANK1 | 7
	ret
.hide
	ld [hl], 0
	ret

; LY がVBlankでなければ、HBlankのはじまりまで待つ（画面が消えていれば待たない）
FwWaitVRAM:
	ldh a, [rLCDC]
	bit B_LCDC_ENABLE, a
	ret z
	ldh a, [rLY]
	cp $90
	jr c, .wait
	cp 152
	ret c
.wait
	ldh a, [rSTAT]
	and $02
	jr z, .wait
.wait2
	ldh a, [rSTAT]
	and $02
	jr nz, .wait2
	ret

FwStarGFX:
	db %00010000
	db %00010000
	db %11111110
	db %01111100
	db %00111000
	db %01101100
	db %01000100
	db %00000000
FwStarPal:
	dw $7fff, $001f, $001f, $0000

; ---------------------------------------------------------------- OAM（VBlank の中）
; PrepareOAMData の最後: 連れ歩き（キットの絵）の4枚のうしろに、白い下じきの4枚を足す。そのあと看板の処理へ
FwOAMTail::
	ld a, [wd471]
	and (1 << 3) | (1 << 4)
	cp (1 << 3) | (1 << 4)
	jr nz, .done
	ld c, $a0
	ld a, [wMovementFlags]
	bit BIT_LEDGE_OR_FISHING, a ; 段差のかげ・つりざおが最後の4枚を使う
	jr z, .limit
	ld c, $90
.limit
	ldh a, [hOAMBufferOffset]
	cp 16
	jr c, .done
	ld e, a
	add 16 - 1
	cp c
	jr nc, .done
	ld a, e
	sub 16
	ld l, a
	ld h, HIGH(wShadowOAM) ; hl = 最後の4枚（連れ歩きは最後のスロット）
	ld d, h
	inc hl
	inc hl
	ld a, [hli]
	and $7f
	sub $0c
	cp 12
	ld a, [hld]
	dec hl
	dec hl
	jr nc, .done
	and 7
	cp 6
	jr nz, .done
	ld b, 4
.copy
	ld a, [hli]
	ld [de], a
	inc e
	ld a, [hli]
	ld [de], a
	inc e
	ld a, [hli]
	cp $80
	jr c, .still
	sub $8c - ($0c + 12)
.still
	ld [de], a
	inc e
	ld a, [hli]
	and OAM_PRIO | OAM_YFLIP | OAM_XFLIP
	or OAM_BANK1 ; パレット0（色1が白）
	ld [de], a
	inc e
	dec b
	jr nz, .copy
	ld a, e
	ldh [hOAMBufferOffset], a
.done
	ld hl, MapSignOAMTail
	ld b, BANK(MapSignOAMTail)
	jp Bankswitch

; 内部の番号 → ずかん番号−1（$FF = いない）
FwDexTable:
	INCBIN "gfx/follow/dex.bin"

; ================================================================ バンク$3B（パレット）
SECTION "FwPal", ROMX, BANK[$3b]
; 色をひとつ: h の下2ビット（BGP）で 白・色1（bc）・色2（de）・黒。h は2ビットずらす
MACRO fw_put_color
	ld a, h
	and 3
	jr z, .white\@
	dec a
	jr z, .c1\@
	dec a
	jr z, .c2\@
	xor a
	ld [\1], a
	ld [\1 + 1], a
	jr .end\@
.white\@
	ld a, $ff
	ld [\1], a
	ld a, $7f
	ld [\1 + 1], a
	jr .end\@
.c1\@
	ld a, b
	ld [\1], a
	ld a, c
	ld [\1 + 1], a
	jr .end\@
.c2\@
	ld a, d
	ld [\1], a
	ld a, e
	ld [\1 + 1], a
.end\@
	srl h
	srl h
ENDM

; 3B:6156 の中、OBJ パレットを作ったあと（元の ld a, $80 / ldh [rBGPI], a のかわり）
; 連れ歩きがキットの絵で、歩いているなら、OBJ パレット6（$D330、WRAMバンク2）をその色に
FwOBPal:
	fw_b7_read l, wFwKitDex
	ld a, [wWalkBikeSurfState]
	and a
	jr z, .walk
	ld l, 0
.walk
; 色の向き: 連れ歩きが下を向いているときは正面の色（手持ちのアイコンの色）、
; 上・横を向いているときは後ろ・横の色（キットの「歩き」の色。キットの後ろ・横の絵はこの色で描いてある）
	ld h, 0
	ld a, l
	and a
	jr z, .gotFace
	ld a, [wSpritePikachuStateData1FacingDirection]
	and a
	jr z, .gotFace
	inc h
.gotFace
	fw_b7_write wFwPalFace, h
	ld a, l
	and a
	jp z, .save
	dec a
	push hl
	ld de, FwPals
	bit 0, h
	jr z, .front
	ld de, FwPalsBack
.front
	ld l, a
	ld h, 0
	add hl, hl
	add hl, hl
	add hl, de
	ld a, [hli]
	ld b, a
	ld a, [hli]
	ld c, a
	ld a, [hli]
	ld d, a
	ld e, [hl]
	pop hl
	ldh a, [rBGP]
	ld h, a
	di
	ld a, 2
	ldh [rSVBK], a
	fw_put_color $d330
	fw_put_color $d332
	fw_put_color $d334
	fw_put_color $d336
	ld a, 1
	ldh [rSVBK], a
	ei
.save
	fw_b7_write wFwPalDex, l
	ld a, $80
	ldh [rBGPI], a
	ret


FwPals:
	INCBIN "gfx/follow/pals.bin"
FwPalsBack:
	INCBIN "gfx/follow/palsback.bin"

; ================================================================ 絵・下じき
SECTION "FwGfx0", ROMX[$4000], BANK[FW_GFX_BANK]
	INCBIN "gfx/follow/gfx.bin", 0, 42 * 384
SECTION "FwGfx1", ROMX[$4000], BANK[FW_GFX_BANK + 1]
	INCBIN "gfx/follow/gfx.bin", 42 * 384, 42 * 384
SECTION "FwGfx2", ROMX[$4000], BANK[FW_GFX_BANK + 2]
	INCBIN "gfx/follow/gfx.bin", 84 * 384, 42 * 384
SECTION "FwGfx3", ROMX[$4000], BANK[FW_GFX_BANK + 3]
	INCBIN "gfx/follow/gfx.bin", 126 * 384, 25 * 384

; 下じきを VRAMバンク1 の $80C0〜 に（1バイトごとに、下のビット・0）。de = 下じき（192バイト）
MACRO fw_mask_copy
	ld hl, $8000 + FW_UNDERLAY_TILE * 16
	ld c, 192
.loop\@
	ld a, [de]
	inc de
	ld b, a
	di
	ld a, 1
	ldh [rVBK], a
	ldh a, [rLCDC]
	bit B_LCDC_ENABLE, a
	jr z, .write\@
	ldh a, [rLY]
	cp $90
	jr c, .wait\@
	cp 152
	jr c, .write\@
.wait\@
	ldh a, [rSTAT]
	and $02
	jr z, .wait\@
.wait2\@
	ldh a, [rSTAT]
	and $02
	jr nz, .wait2\@
.write\@
	ld a, b
	ld [hli], a
	xor a
	ld [hli], a
	ldh [rVBK], a
	ei
	dec c
	jr nz, .loop\@
	ret
ENDM

SECTION "FwMask0", ROMX[$4000], BANK[FW_MASK_BANK]
	INCBIN "gfx/follow/mask1bpp.bin", 0, 85 * 192
SECTION "FwMaskCopy0", ROMX[FW_MASKCOPY], BANK[FW_MASK_BANK]
FwMaskCopy0:
	fw_mask_copy
SECTION "FwMask1", ROMX[$4000], BANK[FW_MASK_BANK + 1]
	INCBIN "gfx/follow/mask1bpp.bin", 85 * 192, 66 * 192
SECTION "FwMaskCopy1", ROMX[FW_MASKCOPY], BANK[FW_MASK_BANK + 1]
FwMaskCopy1:
	fw_mask_copy

; ================================================================ 話しかけたとき（最初のピカチュウ以外）
SECTION "FwTalk", ROMX, BANK[$26]
; DisplayPikachuEmotion（文字の窓はまだない）から。ふりむいて、鳴いて、気持ちのアイコンを出して、話す
FwTalk::
	ld hl, FwGetFollowerE
	ld b, BANK(FwGetFollowerE)
	call Bankswitch
	ret c
	ld a, e
	ld [wWhichPokemon], a
	call GetPartyMonName2 ; ニックネーム → wNameBuffer
	ld a, [wWhichPokemon]
	ld hl, wPartySpecies
	ld c, a
	ld b, 0
	add hl, bc
	ld a, [hl]
	ld [wCurSpecies], a
; ふりむく
	ld a, [wSpritePlayerStateData1FacingDirection]
	xor SPRITE_FACING_UP
	ld [wSpritePikachuStateData1FacingDirection], a
	call UpdateSprites
	call DelayFrame
; 鳴く
	ld a, [wCurSpecies]
	call PlayCry
; 会話をえらぶ（hl = 文、a = アイコン、carry = どうぐを見つけた）
	call FwTalkPick
	push af
	push hl
	ld [wWhichEmotionBubble], a
	ld a, PIKACHU_SPRITE_INDEX
	ld [wEmotionBubbleSpriteIndex], a
	callfar EmotionBubble
	pop hl
	pop af
	jr c, .item
	jp PrintText
.item
	call PrintText
	call YesNoChoice
	ld a, [wCurrentMenuItem]
	and a
	ret nz
	lb bc, NUGGET, 1
	call GiveItem
	ld hl, FwT_GotItem
	jr c, .got
	ld hl, FwT_BagFull
.got
	jp PrintText

; 会話をえらぶ。出力: hl = 文、a = アイコン、carry = どうぐを見つけた（はい・いいえ をきく）
FwTalkPick:
	ld a, [wWhichPokemon]
	ld hl, wPartyMon1Status
	ld bc, wPartyMon2 - wPartyMon1
	call AddNTimes
; 1. 状態異常
	ld a, [hli]
	ld b, a
	and SLP_MASK
	ld de, FwT_Sleep
	ld c, ZZZ_BUBBLE
	jp nz, .status
	bit PSN, b
	ld de, FwT_Poison
	ld c, SKULL_BUBBLE
	jp nz, .status
	bit BRN, b
	ld de, FwT_Burn
	ld c, EXCLAMATION_BUBBLE
	jp nz, .status
	bit FRZ, b
	ld de, FwT_Freeze
	jp nz, .status
	bit PAR, b
	ld de, FwT_Paralyze
	ld c, BOLT_BUBBLE
	jr nz, .status
; 2. カントー（ポケモン・タイプと場所）
	ld a, [hli]
	ld d, a ; タイプ1
	ld e, [hl] ; タイプ2
	ld hl, FwKantoTable
.rule
	ld a, [hli]
	cp $ff
	jr z, .normal
	and a
	ld a, [hli]
	ld b, a
	ld a, [hli]
	ld c, a
	jr nz, .type
	ld a, [wCurSpecies]
	cp b
	jr z, .maps
	cp c
	jr z, .maps
	jr .skipMaps
.type
	ld a, d
	cp b
	jr z, .maps
	ld a, e
	cp b
	jr z, .maps
.skipMaps
	ld a, [hli]
	inc a
	jr nz, .skipMaps
	jr .skipTexts
.maps
	ld a, [wCurMap]
	ld b, a
.mapLoop
	ld a, [hli]
	cp $ff
	jr z, .skipTexts
	cp b
	jr nz, .mapLoop
.mapEnd
	ld a, [hli]
	inc a
	jr nz, .mapEnd
; 当たり: 文の数 n、そのあと (アイコン, 文) が n こ。ランダムに1つ
	ld a, [hli]
	ld c, a
	call Random
.mod
	sub c
	jr nc, .mod
	add c
	ld c, a
	add a
	add c ; *3
	ld c, a
	ld b, 0
	add hl, bc
	ld a, [hli]
	ld c, a
	ld a, [hli]
	ld h, [hl]
	ld l, a
	ld a, c
	and a
	ret
.skipTexts
	ld a, [hli]
	ld c, a
	add a
	add c ; *3
	ld c, a
	ld b, 0
	add hl, bc
	jr .rule
; 4. ふつう（たまに どうぐを見つける）
.normal
	call Random
	and $0f
	jr z, .find
	ld hl, FwT_Normal
	ld a, SMILE_BUBBLE
	and a
	ret
.find
	ld hl, FwT_Find
	ld a, EXCLAMATION_BUBBLE
	scf
	ret
.status
	ld h, d
	ld l, e
	ld a, c
	and a
	ret

; db 0（ポケモン）, ポケモン, ポケモン または db 1（タイプ）, タイプ, 0
; db マップ…, $FF
; db 文の数 / (db アイコン, dw 文) …
MACRO fw_rule_mon
	db 0, \1, \2
ENDM
MACRO fw_rule_type
	db 1, \1, 0
ENDM
FwKantoTable:
	fw_rule_mon BULBASAUR, BULBASAUR
	db ROUTE_1, $ff
	db 2
	db SMILE_BUBBLE
	dw FwT_Bulbasaur1
	db SMILE_BUBBLE
	dw FwT_Bulbasaur2
	fw_rule_mon CHARMANDER, CHARMANDER
	db ROUTE_2, $ff
	db 1
	db SMILE_BUBBLE
	dw FwT_Charmander
	fw_rule_mon PIKACHU, RAICHU
	db ROUTE_2, POWER_PLANT, $ff
	db 2
	db HEART_BUBBLE
	dw FwT_Pikachu1
	db HEART_BUBBLE
	dw FwT_Pikachu2
	fw_rule_mon SQUIRTLE, SQUIRTLE
	db ROUTE_3, $ff
	db 1
	db EXCLAMATION_BUBBLE
	dw FwT_Squirtle
	fw_rule_mon CLEFAIRY, CLEFABLE
	db MT_MOON_1F, MT_MOON_B1F, MT_MOON_B2F, $ff
	db 2
	db SMILE_BUBBLE
	dw FwT_Clefairy1
	db HEART_BUBBLE
	dw FwT_Clefairy2
	fw_rule_mon ONIX, ONIX
	db ROCK_TUNNEL_1F, ROCK_TUNNEL_B1F, $ff
	db 1
	db SMILE_BUBBLE
	dw FwT_Onix
	fw_rule_type ROCK
	db ROCK_TUNNEL_1F, ROCK_TUNNEL_B1F, $ff
	db 4
	db SMILE_BUBBLE
	dw FwT_Rock1
	db SMILE_BUBBLE
	dw FwT_Rock2
	db SMILE_BUBBLE
	dw FwT_Rock3
	db SMILE_BUBBLE
	dw FwT_Rock4
	fw_rule_mon DIGLETT, DUGTRIO
	db DIGLETTS_CAVE, $ff
	db 1
	db SMILE_BUBBLE
	dw FwT_Diglett
	fw_rule_type PSYCHIC_TYPE
	db MR_PSYCHICS_HOUSE, $ff
	db 1
	db QUESTION_BUBBLE
	dw FwT_Psychic
	fw_rule_mon PORYGON, PORYGON
	db CELADON_CITY, $ff
	db 1
	db QUESTION_BUBBLE
	dw FwT_Porygon
	fw_rule_mon DITTO, DITTO
	db ROUTE_15, $ff
	db 1
	db QUESTION_BUBBLE
	dw FwT_Ditto
	fw_rule_type FLYING
	db ROUTE_18, $ff
	db 1
	db SMILE_BUBBLE
	dw FwT_Flying
	fw_rule_type GHOST
	db LAVENDER_TOWN, $ff
	db 1
	db SMILE_BUBBLE
	dw FwT_Ghost
	db $ff

; ---------------------------------------------------------------- 会話（キットの会話文案.md。1行18マス）
FwT_Sleep:
	text_ram wNameBuffer
	text "は"
	line "すこし　ねむそうだ"
	prompt
FwT_Poison:
	text_ram wNameBuffer
	text "は"
	line "ぐあいが　わるそうだ"
	prompt
FwT_Burn:
	text_ram wNameBuffer
	text "は"
	line "すこし　いたそうだ"
	prompt
FwT_Freeze:
	text_ram wNameBuffer
	text "は"
	line "こおりづけに　なっている！"
	prompt
FwT_Paralyze:
	text_ram wNameBuffer
	text "は"
	line "うごきが　にぶく　なっている"
	prompt
FwT_Bulbasaur1:
	text_ram wNameBuffer
	text "は"
	line "つるを　くねくね　させた！"
	prompt
FwT_Bulbasaur2:
	text_ram wNameBuffer
	text "は"
	line "つるを　ぴしっと　ならした！"
	prompt
FwT_Charmander:
	text_ram wNameBuffer
	text "は"
	line "しっぽの　ほのおを　もやした！"
	prompt
FwT_Pikachu1:
	text_ram wNameBuffer
	text "は"
	line "たのしく　おどった！"
	prompt
FwT_Pikachu2:
	text_ram wNameBuffer
	text "は　うれしくて"
	line "おどりだした！"
	prompt
FwT_Squirtle:
	text_ram wNameBuffer
	text "は　ころんで"
	line "ちょっと　くやしそうだ！"
	prompt
FwT_Clefairy1:
	text_ram wNameBuffer
	text "は"
	line "そらを　みあげている！"
	prompt
FwT_Clefairy2:
	text_ram wNameBuffer
	text "は"
	line "とつぜん　おどりだした！"
	prompt
FwT_Onix:
	text_ram wNameBuffer
	text "は　たのしそうに"
	line "じめんに　もぐっている！"
	prompt
FwT_Rock1:
	text_ram wNameBuffer
	text "は　たのしそうに"
	line "ころがっている！"
	prompt
FwT_Rock2:
	text_ram wNameBuffer
	text "は"
	line "いわを　けずりはじめた！"
	prompt
FwT_Rock3:
	text_ram wNameBuffer
	text "は　たのしそうに"
	line "いわを　ぶつけている！"
	prompt
FwT_Rock4:
	text_ram wNameBuffer
	text "は　じめんを"
	line "たたいて　ならしはじめた！"
	prompt
FwT_Diglett:
	text_ram wNameBuffer
	text "は　からだを"
	line "のばして　くつろいでいる！"
	prompt
FwT_Psychic:
	text "⋯⋯　⋯⋯　⋯⋯　⋯⋯"
	para "@"
	text_ram wNameBuffer
	text "は"
	line "だまって　うなずいた！"
	prompt
FwT_Porygon:
	text_ram wNameBuffer
	text "は"
	line "なにか　つぶやいた⋯⋯"
	prompt
FwT_Ditto:
	text "⋯⋯おや？　@"
	text_ram wNameBuffer
	text "の"
	line "すがたは⋯⋯"
	cont "かわらなかった！"
	prompt
FwT_Flying:
	text_ram wNameBuffer
	text "は"
	line "ゆうがに　そらを　とんでいる！"
	prompt
FwT_Ghost:
	text_ram wNameBuffer
	text "は　たのしそうに"
	line "ゆらゆら　ゆれている"
	prompt
FwT_Normal:
	text_ram wNameBuffer
	text "は"
	line "あなたと　いっしょで　うれしそうだ！"
	prompt
FwT_Find:
	text_ram wNameBuffer
	text "は"
	line "なにか　みつけた　ようだ"
	para "ひろいますか？"
	done
FwT_GotItem:
	text "<PLAYER>は"
	line "きんのたまを　てにいれた！@"
	sound_get_item_1
	text_promptbutton
	text_end
FwT_BagFull:
	text "しかし　どうぐが"
	line "いっぱいで　もてない！"
	prompt
