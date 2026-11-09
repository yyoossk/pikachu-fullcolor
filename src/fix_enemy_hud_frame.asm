; variants: v s f sf x sx xf sxf
; 相手のHUDの枠の線が、キットで足したHPの数字（のこり／最大）で途切れていたのを直す。
; 自分のポケモンと同じように、数字の行の下に枠の線を引く。
;   2行め: │HP:バー        （そのまま）
;   3行め: │ 37/ 37        （左のたて線をのばす。数字の左右は空白）
;   4行め: └────────◣  （ここに線をうつす）
; そのため、相手のHUDを消す所（4か所）は5行消すようにし、
; 色の割りあて（バンク9の表）も 3行めの左はたて線（VRAMバンク1）、4行めは枠の色にする。

IF DEF(V_60FPS)
DEF KIT_ENEMY_HP_NUMBER EQU $71b8
ELSE
DEF KIT_ENEMY_HP_NUMBER EQU $7198
ENDC
DEF hIsGBC EQU $fffe

SECTION "EnemyHUDFrame", ROMX, BANK[$3a]
EnemyHUDNumbersAndFrame::
	call KIT_ENEMY_HP_NUMBER
	ldh a, [hIsGBC]
	and a
	ld a, $5e ; たて線（カラー）
	jr nz, .gotLine
	ld a, $73 ; たて線（白黒）
.gotLine
	hlcoord 1, 3
	ld [hli], a
	ld [hl], $7f ; 空白
	hlcoord 10, 3
	ld [hl], $7f ; 空白
	hlcoord 1, 4
	ld [hl], $74 ; └
	ld a, $76    ; ─
	ld b, 8
.line
	inc hl
	ld [hl], a
	dec b
	jr nz, .line
	inc hl
	ld [hl], $78 ; ◣
	ret

; 相手のHUDを消す所: 4行 → 5行
SECTION "EnemyHUDClear1", ROMX[$462b + 5], BANK[$0f]
	db 5
SECTION "EnemyHUDClear2", ROMX[$4b90 + 5], BANK[$0f]
	db 5
SECTION "EnemyHUDClear3", ROMX[$5032 + 5], BANK[$0f]
	db 5
SECTION "EnemyHUDClear4", ROMX[$55a0 + 5], BANK[$3d]
	db 5

; 戦闘の色の割りあて（32×18）
SECTION "EnemyHUDAttrRow3", ROMX[$5b10 + 3 * 32 + 1], BANK[$09]
	db $09 ; VRAMバンク1のたて線
SECTION "EnemyHUDAttrRow4", ROMX[$5b10 + 4 * 32 + 1], BANK[$09]
	ds 10, $01
