; variants: v s f sf x sx xf sxf
; ポケモンだいすきクラブに初めて入った時のイベントで、ピカチュウが
; 技思い出しおじさん（6, 6）をすりぬけていくので、おじさんを1マス右（7, 6）にうつす。

SECTION "FanClubRelearnerX", ROMX[$71ac], BANK[$16]
	db 7 + 4 ; x
