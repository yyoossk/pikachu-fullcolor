; variants: v s f sf x sx xf sxf
; ポケモンセンター：
;  1) 回復して もらった あと（「またの ごりようを…」の あと）、主人公が 下を 向く
;     （A ボタンを 連打しても、もう一度 ジョーイさんに 話しかけない）。「やめる」の ときは 今までどおり。
;  2) 「せってい」に「かいふくの アニメ」（みる／とばす）を 足す。「とばす」なら 回復の きかいの アニメーション
;     （ボールが 並んで 光る・回復の 音楽）を しない。町の 音楽は そのまま。
;     値は $D2D6（wUnusedObtainedBadges。レポートに 入る）の ビット1（0 = みる・1 = とばす）。
;     ビット0 は「わすれさせる ときの カーソル」。wOptions は 文字の 速さ・サウンド・しあいの ルール・
;     せんとう アニメで 全部 うまって いるので 使わない。前の レポートは 0 なので「みる」。
; 赤フルカラーの キット「赤_ポケモンセンターの回復」を この版に 当てた もの。

DEF wHealOpts EQU $d2d6 ; wUnusedObtainedBadges
DEF BIT_SKIP_HEAL_ANIM EQU 1
DEF HEAL_MACHINE EQU $44b9 ; 1C:44B9 AnimateHealingMachine（8つの 版で 同じ）
DEF FAREWELL_TEXT EQU $7223 ; 01:7223 「またの ごりようを おまちしてます！」
DEF ROW EQUS "$c3a0 + 20 *"

; ---------------------------------------------------------------- ポケモンセンター（bank 1）
; 元：01:70ED farcall AnimateHealingMachine / 01:70F5 predef HealParty /
;     01:70FA〜710F 音楽を もとに もどす / 01:716E jr .done
SECTION "Pokecenter: heal animation call", ROMX[$70ed], BANK[$01]
	ld b, BANK(KitHealAnim)
	ld hl, KitHealAnim
	call Bankswitch
	assert @ == $70f5 ; predef HealParty（そのまま）
SECTION "Pokecenter: skip music restore", ROMX[$70fa], BANK[$01]
	jr @ + 2 + ($7110 - $70fc) ; 音楽を もどす 所は KitHealAnim で した
; 01:70FC〜710F（20バイト）：回復した ときの 終わり
KitHealDone:
	ld hl, FAREWELL_TEXT
	call PrintText
	xor a ; 下
	ld [wSpritePlayerStateData1FacingDirection], a
	jp UpdateSprites
	ds $7110 - @, 0
SECTION "Pokecenter: after heal", ROMX[$716e], BANK[$01]
	jr KitHealDone

SECTION "Pokecenter: heal animation", ROMX, BANK[$3d]
KitHealAnim:
	ld a, [wHealOpts]
	bit BIT_SKIP_HEAL_ANIM, a
	jr nz, .skip
	ld b, $1c
	ld hl, HEAL_MACHINE
	call Bankswitch
	; 元の 01:70FA〜710F（音楽を もとに もどす）
	xor a
	ld [wAudioFadeOutControl], a
	ld a, [wAudioSavedROMBank]
	ld [wAudioROMBank], a
	ld a, [wMapMusicSoundID]
	ld [wLastMusicSoundID], a
	ld [wNewSoundID], a
	jp PlaySound
.skip ; アニメーションを とばす：音楽は そのまま。少しだけ 間を あける
	ld c, 8
	jp DelayFrames

; ---------------------------------------------------------------- せってい（bank $3D：3D:5E99〜）
; 項目は 表（3D:5ECD）の 8つ：0 はなしの はやさ・1 せんとう アニメ・2 しあいの ルール・3 サウンド・
; 4 プリントの こさ・5 あき（何も しない）・6 わすれさせる ときの カーソル・7 おわり。値は 行 2＋2×番号の 11 けため。
; 「わすれさせる ときの カーソル」の 名前（行 12 いっぱい）を 行 11 に 上げ、その 値（はい／いいえ）を 5番（行 12）に、
; 6番（行 14）を 新しい「かいふくの アニメ」に する。名前は 行 13 に 出す。
; 名前には だくてんの 字が ないので、前の 項目の 値の 行の すぐ 下に 置ける（だくてんは 上の 行に 出る）。
; 「とばす」の だくてんは 行 13 の 12 けためで、名前（1〜9 けため）とは 重ならない。
SECTION "Options: item 5 and 6", ROMX[$5ecd + 5 * 2], BANK[$3d]
	dw $60c6 ; 5：わすれさせる ときの カーソル（元の 6番の 処理）
	dw KitOptHeal ; 6：かいふくの アニメ
SECTION "Options: forget value row", ROMX[$60e1 + 1], BANK[$3d]
	dw ROW 12 + 11 ; 元は 行 14
SECTION "Options: down skips item 5", ROMX[$6115 + 1], BANK[$3d]
	db $ff ; 元：cp 4（4 の つぎは 6）→ とばさない
SECTION "Options: up skips item 5", ROMX[$611e + 2], BANK[$3d]
	db $ff ; 元：cp 6（6 の つぎは 4）→ とばさない
; ▶ を 消す：元は 10 けための 行 1〜11 と 13〜16（行 12 の 名前を 消さない ため）。
; 名前が 行 11 に なったので、値の 行（2〜16 の 偶数）だけ 消す。
SECTION "Options: clear cursor", ROMX[$612f], BANK[$3d]
	ld de, 40
	ld hl, ROW 2 + 10
	ld c, 8
	call $6151
	jr @ + 2 + ($6142 - ($612f + 13))
	ds $6142 - @, 0
; 名前を 出す：元は ld hl, coord 1,2 / ld de, 名前の 文字 / call PlaceString（3D:6161〜6169）
SECTION "Options: labels", ROMX[$6161], BANK[$3d]
	call KitOptLabels
	jr @ + 2 + ($616a - ($6161 + 5))
	ds $616a - @, 0

SECTION "Options: new", ROMX, BANK[$3d]
KitOptLabels:
	ld hl, ROW 2 + 1
	ld de, $6190
	call PlaceString
	; 行 12 の「わすれさせる ときの カーソル」を 行 11 に 上げる
	ld hl, ROW 12 + 1
	ld de, ROW 11 + 1
	ld c, 18
.move
	ld a, [hl]
	ld [de], a
	ld a, $7f ; 空白
	ld [hli], a
	inc de
	dec c
	jr nz, .move
	ld hl, ROW 13 + 1
	ld de, KitOptHealLabel
	jp PlaceString

; 6番：かいふくの アニメ（左右で みる／とばす）。元の 6番（3D:60C6）と 同じ 形
KitOptHeal:
	ldh a, [hJoy5]
	and PAD_LEFT | PAD_RIGHT
	jr z, .show
	ld a, [wHealOpts]
	xor 1 << BIT_SKIP_HEAL_ANIM
	ld [wHealOpts], a
.show
	ld a, [wHealOpts]
	ld de, .see
	bit BIT_SKIP_HEAL_ANIM, a
	jr z, .put
	ld de, .skip
.put
	ld hl, ROW 14 + 11
	call PlaceString
	and a
	ret
.see:  db "みる", $7f, "@"
.skip: db "とばす@"

KitOptHealLabel:
	db "かいふくの", $7f, "アニメ@"
