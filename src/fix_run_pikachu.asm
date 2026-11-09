; variants: v s f sf x sx xf sxf
; ランニングシューズで走ると、つれ歩いているピカチュウが消えていたのを直す（走っているあいだもついてくる）。
; キットが走るあいだピカチュウを消していた所を、3か所なくす／かえる。
;  1. 走りはじめ: ピカチュウを消して（wPikachuSpawnState を 0）、ついてくる道のりも消していた → やめる
;  2. ShouldPikachuSpawn: 走っているあいだ（wStatusFlags6 の bit 7）は出さない → やめる
;  3. ピカチュウについてくる道のりを足す判定（Func_fcc23）: 走っているあいだは足さない → やめる
;     （道のりがたまると、ピカチュウは速く歩く FastPikachuFollow ので、走ってもついてくる）
;  4. 走りおわり: ピカチュウを出しなおしていた → ピカチュウが出ている時はしない（その場でワープしないように）

IF DEF(V_60FPS)
DEF RUN_HIDE_PIKACHU  EQU $79a8
DEF RUN_STOP_RESPAWN  EQU $6f87
ELSE
DEF RUN_HIDE_PIKACHU  EQU $6c88
DEF RUN_STOP_RESPAWN  EQU $6f67
ENDC

SECTION "RunKeepPikachu", ROMX[RUN_HIDE_PIKACHU], BANK[$20]
	ds 12, 0 ; nop（xor a / ld [wPikachuSpawnState], a / callfar ClearPikachuFollowCommandBuffer）

SECTION "RunKeepPikachuSpawn", ROMX[$44f6], BANK[$3f]
	ds 7, 0 ; nop（ld a, [wStatusFlags6] / bit 7, a / jr nz, .hide）

SECTION "RunKeepPikachuFollow", ROMX[$4c4d], BANK[$3f]
	ds 7, 0 ; nop（ld a, [wStatusFlags6] / bit 7, a / jr nz, .no）

SECTION "RunStopRespawnHook", ROMX[RUN_STOP_RESPAWN], BANK[$3a]
	call RunStopRespawnIfHidden ; ld a, 2 / ld [wPikachuSpawnState], a のかわり
	ds 2, 0

SECTION "RunStopRespawn", ROMX, BANK[$3a]
RunStopRespawnIfHidden:
	ld a, [wSpritePikachuStateData1ImageIndex]
	inc a
	jr z, .respawn
	pop af ; ピカチュウが出ている: 出しなおさずにもどる
	ret
.respawn
	ld a, 2
	ld [wPikachuSpawnState], a
	ret

; 走っているあいだは、ピカチュウもいつも速く歩く（1マスうしろをついてくる）
SECTION "RunPikachuFastHook", ROMX[$47e1], BANK[$3f]
	call RunPikachuFastCheck ; call AreThereAtLeastTwoStepsInPikachuFollowCommandBuffer のかわり

SECTION "RunPikachuFast", ROMX, BANK[$3f]
RunPikachuFastCheck:
	ld a, [wStatusFlags6]
	bit 7, a ; 走っている
	jp z, AreThereAtLeastTwoStepsInPikachuFollowCommandBuffer
	scf
	ret
