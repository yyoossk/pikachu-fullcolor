; variants: v s f sf x sx xf sxf
; 戦闘のHPバーの色が、HPが減っても緑のままになるのを直す。
; キットのHPの数字の表示（バンク$3Aへの farcall）が e（HPバーのドット数）をこわすので、
; そのよびだしの前後で de をとっておく。
; （相手側は fix_enemy_hud_frame.asm の処理をよぶ。どちらもバンク$3A）

IF DEF(V_60FPS)
DEF KIT_PLAYER_HP EQU $7aa4
ELSE
DEF KIT_PLAYER_HP EQU $7a84
ENDC

SECTION "HPBarColorHookPlayer", ROMX[$4ff7], BANK[$0f]
	call KitPlayerHPKeepDE
	ds 5, 0 ; nop

SECTION "HPBarColorHookEnemy", ROMX[$50cb], BANK[$0f]
	call KitEnemyHPKeepDE
	ds 5, 0 ; nop

SECTION "HPBarColorStubs", ROMX, BANK[$0f]
KitPlayerHPKeepDE:
	push de
	ld hl, KIT_PLAYER_HP
	jr KitHPKeepDECommon
KitEnemyHPKeepDE:
	push de
	ld hl, EnemyHUDNumbersAndFrame ; キットのHPの数字＋枠（fix_enemy_hud_frame.asm）
KitHPKeepDECommon:
	ld b, $3a
	call Bankswitch
	pop de
	ret
