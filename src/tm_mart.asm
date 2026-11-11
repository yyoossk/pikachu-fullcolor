; variants: v s f sf x sx xf sxf
; 殿堂入りしたあとは、タマムシデパート 2かいの わざマシンの店員が、一回しか手に入らない わざマシンも売る。
;   元から売っている 9本（01・02・05・07・09・17・32・33・37）に、ジムリーダーにもらう・道に落ちているなどで
;   一回しか手に入らない 38本を足して、わざマシンの番号の順にならべる（47本）。
;   ゲームコーナーの景品（15・23・50）は、コインでなんどでも手に入るので入れない。
;   値段は元のゲームの わざマシンの値段（TechnicalMachinePrices）のまま。
;   殿堂入りしたか: 殿堂入りの記録の数（wNumHoFTeams）が 0 でない。
;
; 店のリストは wItemList（16バイト。14こまで）に写してから出すので、47本は入らない。
; 「かう」のリストを出すところ（DisplayPokemartDialogue_ の ld hl, wItemList）を呼び出しにかえ、
; この店員で殿堂入りのあとなら、てきのパーティのデータの所（wEnemyPartyCount〜。たたかいの間だけ使う）に
; 長いリストを作って、そこを指す。

DEF TM_MART_BUF EQUS "wEnemyPartyCount" ; 1 + 47 + 1 = 49バイト

; ---------------------------------------------------------------- 呼び出し
; DisplayPokemartDialogue_.buyMenuLoop の ld hl, wItemList（バンク1 $6C24）
SECTION "TMMartHook", ROMX[$6c24], BANK[$01]
	call TMMartTrampoline ; hl = 出すリスト

; ホームの rst のあき（$0029〜$0033。rst $30 の $0030 はとびこす）
SECTION "TMMartTrampoline", ROM0[$0029]
TMMartTrampoline:
	ld b, BANK(TMMartList)
	ld hl, TMMartList
	jr .jp
	db $ff ; rst $30（元のまま）
.jp
	jp Bankswitch
	assert @ == $0034

; ---------------------------------------------------------------- 本体
SECTION "TMMartList", ROMX
; 出力: hl = 「かう」のリスト（数・品物…・$FF）
TMMartList:
	ld hl, wItemListPointer ; LoadItemList が 上・下 の順に入れている
	ld a, [hli]
	cp HIGH(CeladonMart2FClerk2Text + 1)
	jr nz, .normal
	ld a, [hl]
	cp LOW(CeladonMart2FClerk2Text + 1)
	jr nz, .normal
	ld a, [wNumHoFTeams]
	and a
	jr z, .normal
	ld hl, TMMartAllTMs
	ld de, TM_MART_BUF
.copy
	ld a, [hli]
	ld [de], a
	inc de
	inc a
	jr nz, .copy
	ld hl, TM_MART_BUF
	ret
.normal
	ld hl, wItemList
	ret

TMMartAllTMs:
	db .end - .items - 1
.items
	db TM_MEGA_PUNCH      ; 01
	db TM_RAZOR_WIND      ; 02
	db TM_SWORDS_DANCE    ; 03
	db TM_WHIRLWIND       ; 04
	db TM_MEGA_KICK       ; 05
	db TM_TOXIC           ; 06
	db TM_HORN_DRILL      ; 07
	db TM_BODY_SLAM       ; 08
	db TM_TAKE_DOWN       ; 09
	db TM_DOUBLE_EDGE     ; 10
	db TM_BUBBLEBEAM      ; 11
	db TM_WATER_GUN       ; 12
	db TM_ICE_BEAM        ; 13
	db TM_BLIZZARD        ; 14
	db TM_PAY_DAY         ; 16
	db TM_SUBMISSION      ; 17
	db TM_COUNTER         ; 18
	db TM_SEISMIC_TOSS    ; 19
	db TM_RAGE            ; 20
	db TM_MEGA_DRAIN      ; 21
	db TM_SOLARBEAM       ; 22
	db TM_THUNDERBOLT     ; 24
	db TM_THUNDER         ; 25
	db TM_EARTHQUAKE      ; 26
	db TM_FISSURE         ; 27
	db TM_DIG             ; 28
	db TM_PSYCHIC_M       ; 29
	db TM_TELEPORT        ; 30
	db TM_MIMIC           ; 31
	db TM_DOUBLE_TEAM     ; 32
	db TM_REFLECT         ; 33
	db TM_BIDE            ; 34
	db TM_METRONOME       ; 35
	db TM_SELFDESTRUCT    ; 36
	db TM_EGG_BOMB        ; 37
	db TM_FIRE_BLAST      ; 38
	db TM_SWIFT           ; 39
	db TM_SKULL_BASH      ; 40
	db TM_SOFTBOILED      ; 41
	db TM_DREAM_EATER     ; 42
	db TM_SKY_ATTACK      ; 43
	db TM_REST            ; 44
	db TM_THUNDER_WAVE    ; 45
	db TM_PSYWAVE         ; 46
	db TM_EXPLOSION       ; 47
	db TM_ROCK_SLIDE      ; 48
	db TM_TRI_ATTACK      ; 49
	db -1
.end
	assert .end - .items - 1 == 47
