; variants: v s f sf x sx xf sxf
; STARTボタンの メニューの「パソコン」で「ボックスを かえる」を した あと、人に 話しかけると
; ちがう 会話が 出たり 止まったり するのを 直す。
; 原因：ボックスを かえる 処理（ChangeBox）の 最後は、
;     wCurMapTextPtr を wChangeBoxSavedMapTextPointer（$CD3D）に とっておく
;     → RestoreMapTextPointer（hSavedMapTextPtr を wCurMapTextPtr に もどす）
;     → レポートを 書く（SaveGameData）→ SetMapTextPointer（hl = $CD3D）
;   と なって いる。もとの ゲームでは パソコンは かならず PrintPredefTextID の 中から 開くので、
;   wCurMapTextPtr は 一時的な 表（TextPredefs）で、最後に PrintPredefTextID が もとに もどす。
;   STARTボタンの メニューの「パソコン」は PrintPredefTextID を 通らないので、hSavedMapTextPtr には 古い 値が
;   入った まま。もどす 人も いないので、wCurMapTextPtr が $CD3D の ままに なり、そのあと 人に 話しかけると
;   こわれた 表を 読む（レポートにも 古い 値が 書かれる）。
; 直し方：ChangeBox の 最後（ChangeBox+$51 から 24バイト。151匹そろう版は 3バイト うしろ）を、べつの バンクの 処理への jp Bankswitch に かえる。
;   wCurMapTextPtr が TextPredefs の ときだけ（パソコンの 机から 開いた とき）元の とおりに する。
;   ちがう とき（STARTボタンの メニュー）は、wCurMapTextPtr は もう マップの 会話の 表なので、
;   そのまま レポートを 書くだけに する。
; 赤フルカラーの キット「赤_パソコンでボックスをかえたあとのフリーズ」を この版の 番地に 当てた もの。

DEF TEXT_PREDEFS EQU $3f64 ; PrintPredefTextID の ld hl, TextPredefs（どの版も 同じ）

IF DEF(V_151)
DEF CHANGEBOX_TAIL EQU $7d7f ; ChangeBox（$7D2E）+ $51
ELSE
DEF CHANGEBOX_TAIL EQU $7d7c ; ChangeBox（$7D2B）+ $51
ENDC

SECTION "ChangeBoxTail", ROMX[CHANGEBOX_TAIL], BANK[$1c]
ChangeBoxTail:
	assert ChangeBoxTail == ChangeBox + $51
	ld b, BANK(ChangeBoxSaveFix)
	ld hl, ChangeBoxSaveFix
	jp Bankswitch
	ds 24 - 8, 0 ; もう 使わない（元の ld hl, wCurMapTextPtr 〜 ret）

SECTION "ChangeBoxSaveFix", ROMX
ChangeBoxSaveFix:
	ld hl, wCurMapTextPtr
	ld a, [hli]
	cp LOW(TEXT_PREDEFS)
	jr nz, .save
	ld a, [hld]
	cp HIGH(TEXT_PREDEFS)
	jr nz, .save
	; パソコンの 机から（元の とおり）
	ld de, wChangeBoxSavedMapTextPointer
	ld a, [hli]
	ld [de], a
	inc de
	ld a, [hl]
	ld [de], a
	call RestoreMapTextPointer
	call .save
	ld hl, wChangeBoxSavedMapTextPointer
	jp SetMapTextPointer
.save ; STARTボタンの メニューから：会話の 表は そのまま。レポートを 書くだけ
	ld b, BANK(SaveGameData)
	ld hl, SaveGameData
	jp Bankswitch
