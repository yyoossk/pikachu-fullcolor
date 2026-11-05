// Headless SameBoy runner driven by a script on stdin.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <Core/gb.h>
static GB_gameboy_t *gb; static int wlo=-1,whi=-1; static FILE*wlog;
static bool wcb(GB_gameboy_t*g,uint16_t a,uint8_t d){ if(a>=wlo&&a<=whi&&wlog){ fprintf(wlog,"%04x %02x pc=%04x bank=%02x\n",a,d,g->pc,g->mbc_rom_bank); } return true; }
 static uint32_t px[256*224]; static int vbl;
static FILE *vrec=NULL, *arec=NULL;
static void vblank(GB_gameboy_t *g, GB_vblank_type_t t){ vbl=1;
  if(vrec){ for(int i=0;i<160*144;i++){uint8_t c[3]={px[i]>>16,px[i]>>8,px[i]}; fwrite(c,1,3,vrec);} } }
static void sample(GB_gameboy_t *g, GB_sample_t *smp){ if(arec) fwrite(smp,4,1,arec); }
static uint32_t enc(GB_gameboy_t *g,uint8_t r,uint8_t gg,uint8_t b){return (r<<16)|(gg<<8)|b;}
static char *noinput(GB_gameboy_t *g){return NULL;}
static void logcb(GB_gameboy_t *g,const char *s,GB_log_attributes_t a){}
static unsigned minsp=0xffff;
static void frames(int n){ for(int i=0;i<n;i++){ vbl=0; while(!vbl){ GB_run(gb); unsigned sp=gb->registers[GB_REGISTER_SP]; if(sp>=0xde00 && sp<0xe000 && sp<minsp) minsp=sp; } } }
static int keyidx(char c){ switch(c){case 'R':return GB_KEY_RIGHT;case 'L':return GB_KEY_LEFT;case 'U':return GB_KEY_UP;case 'D':return GB_KEY_DOWN;case 'A':return GB_KEY_A;case 'B':return GB_KEY_B;case 'S':return GB_KEY_START;case 's':return GB_KEY_SELECT;} return -1;}
int main(int argc,char**argv){
  if(argc<3){fprintf(stderr,"gbrec rom bootrom < script\n");return 1;}
  gb=GB_alloc(); GB_init(gb, getenv("GBDMG")? GB_MODEL_DMG_B : getenv("GBSGB")? GB_MODEL_SGB_NTSC : GB_MODEL_CGB_E);
  GB_load_boot_rom(gb, argv[2]); GB_load_rom(gb, argv[1]);
  GB_set_vblank_callback(gb, vblank); GB_set_rgb_encode_callback(gb, enc);
  GB_set_pixels_output(gb, px); GB_set_log_callback(gb, logcb); GB_set_async_input_callback(gb, noinput); GB_set_input_callback(gb, noinput);
  GB_set_color_correction_mode(gb, GB_COLOR_CORRECTION_DISABLED);
  GB_set_turbo_mode(gb, true, true);
  GB_set_sample_rate(gb, 48000); GB_apu_set_sample_callback(gb, sample);
  char line[512];
  setvbuf(stdout,NULL,_IOLBF,0);
  while(fgets(line,sizeof line,stdin)){
    char cmd[64]={0}, a[256]={0}; int n=0;  sscanf(line,"%63s %255s %d",cmd,a,&n);
    if(!strcmp(cmd,"watch")){ wlo=strtoul(a,0,16); whi=wlo+(n?n:1)-1; if(!wlog) wlog=fopen(getenv("GBWATCHLOG")?getenv("GBWATCHLOG"):"watch.log","w"); GB_set_write_memory_callback(gb,wcb); }
    else if(!strcmp(cmd,"wmark")){ if(wlog){fprintf(wlog,"MARK %s\n",a); fflush(wlog);} }
    else if(!strcmp(cmd,"wflush")){ if(wlog) fflush(wlog); }
    else if(!strcmp(cmd,"wait")) frames(atoi(a));
    else if(!strcmp(cmd,"press")){ for(char*p=a;*p;p++){int k=keyidx(*p); if(k>=0) GB_set_key_state(gb,k,1);} frames(n?n:4); for(char*p=a;*p;p++){int k=keyidx(*p); if(k>=0) GB_set_key_state(gb,k,0);} frames(4);}
    else if(!strcmp(cmd,"down")){ for(char*p=a;*p;p++){int k=keyidx(*p); if(k>=0) GB_set_key_state(gb,k,1);} }
    else if(!strcmp(cmd,"up")){ for(char*p=a;*p;p++){int k=keyidx(*p); if(k>=0) GB_set_key_state(gb,k,0);} }
    else if(!strcmp(cmd,"shot")){ FILE*f=fopen(a,"wb"); int w=GB_get_screen_width(gb),h=GB_get_screen_height(gb); fprintf(f,"P6 %d %d 255\n",w,h); for(int i=0;i<w*h;i++){uint8_t c[3]={px[i]>>16,px[i]>>8,px[i]}; fwrite(c,1,3,f);} fclose(f);}
    else if(!strcmp(cmd,"save")) GB_save_state(gb,a);
    else if(!strcmp(cmd,"load")) GB_load_state(gb,a);
    else if(!strcmp(cmd,"peek")){ unsigned ad=strtoul(a,0,16); fprintf(stdout,"%04x:",ad); for(int i=0;i<(n?n:16);i++) fprintf(stdout," %02x",GB_safe_read_memory(gb,ad+i)); fprintf(stdout,"\n");}
    else if(!strcmp(cmd,"poke")){ unsigned ad=strtoul(a,0,16); GB_write_memory(gb,ad,(uint8_t)n); }
    else if(!strcmp(cmd,"vpeek")){ /* vpeek bank_addr(hex, bank*0x10000+addr) n */
      unsigned v=strtoul(a,0,16); size_t sz; uint16_t bk;
      uint8_t*vr=GB_get_direct_access(gb,GB_DIRECT_ACCESS_VRAM,&sz,&bk);
      unsigned off=(v>>16)*0x2000+((v&0xffff)-0x8000);
      fprintf(stdout,"%05x:",v); for(int i=0;i<(n?n:16);i++) fprintf(stdout," %02x",vr[off+i]); fprintf(stdout,"\n");}
    else if(!strcmp(cmd,"pals")){ fprintf(stdout,"BG:"); for(int i=0;i<64;i++) fprintf(stdout,"%02x",gb->background_palettes_data[i]); fprintf(stdout," OB:"); for(int i=0;i<64;i++) fprintf(stdout,"%02x",gb->object_palettes_data[i]); fprintf(stdout,"\n"); }
    else if(!strcmp(cmd,"oam")){ size_t sz; uint16_t bk; uint8_t*o=GB_get_direct_access(gb,GB_DIRECT_ACCESS_OAM,&sz,&bk); fprintf(stdout,"OAM:"); for(int i=0;i<160;i++) fprintf(stdout,"%02x",o[i]); fprintf(stdout,"\n"); }
    else if(!strcmp(cmd,"wpeek")){ /* wpeek bank*0x10000+addr */ unsigned v=strtoul(a,0,16); size_t sz; uint16_t bk; uint8_t*r=GB_get_direct_access(gb,GB_DIRECT_ACCESS_RAM,&sz,&bk); unsigned off=(v>>16)*0x1000+((v&0xffff)-0xd000); fprintf(stdout,"%05x:",v); for(int i=0;i<(n?n:16);i++) fprintf(stdout," %02x",r[off+i]); fprintf(stdout,"\n"); }
    else if(!strcmp(cmd,"bsave")) GB_save_battery(gb,a);
    else if(!strcmp(cmd,"bload")) GB_load_battery(gb,a);
    else if(!strcmp(cmd,"minsp")){ fprintf(stdout,"minsp=%04x\n",minsp); }
    else if(!strcmp(cmd,"reset")){ GB_reset(gb); }
    else if(!strcmp(cmd,"call")){ /* call bank:addr (hex) - test only */
      unsigned bank=strtoul(a,0,16)>>16, addr=strtoul(a,0,16)&0xffff;
      uint16_t sp=gb->registers[GB_REGISTER_SP]-2; GB_write_memory(gb,sp,gb->pc&255); GB_write_memory(gb,sp+1,gb->pc>>8);
      gb->registers[GB_REGISTER_SP]=sp; GB_write_memory(gb,0x2000,bank); GB_write_memory(gb,0xffb8,bank); gb->pc=addr; }
    else if(!strcmp(cmd,"render")){ GB_set_rendering_disabled(gb, atoi(a)==0); }
    else if(!strcmp(cmd,"rec")){ char p[300]; snprintf(p,300,"%s.rgb",a); vrec=fopen(p,"wb"); snprintf(p,300,"%s.pcm",a); arec=fopen(p,"wb"); }
    else if(!strcmp(cmd,"stoprec")){ if(vrec)fclose(vrec); if(arec)fclose(arec); vrec=arec=NULL; fprintf(stdout,"stopped\n"); }
    else if(!strcmp(cmd,"untilmem")){ unsigned ad,val; sscanf(a,"%x",&ad); val=n; static unsigned rb[512][3]; int n=0; long steps=0;
      while(steps<200000000){ unsigned pc=gb->pc; rb[n&511][0]=pc; rb[n&511][1]=gb->mbc_rom_bank; rb[n&511][2]=gb->registers[GB_REGISTER_SP]; n++; steps++; if(GB_safe_read_memory(gb,ad)==val) break; GB_run(gb);}
      for(int i=(n>400?n-400:0);i<n;i++) fprintf(stdout,"T %04x %02x %04x\n",rb[i&511][0],rb[i&511][1],rb[i&511][2]); fprintf(stdout,"END %ld\n",steps); }
    else if(!strcmp(cmd,"untilpc")){ unsigned target=strtoul(a,0,16); static unsigned rb[512][3]; int n=0; long steps=0;
      while(steps<200000000){ unsigned pc=gb->pc; rb[n&511][0]=pc; rb[n&511][1]=gb->mbc_rom_bank; rb[n&511][2]=gb->registers[GB_REGISTER_SP]; n++; steps++; if(pc==target) break; GB_run(gb);}
      for(int i=(n>400?n-400:0);i<n;i++) fprintf(stdout,"T %04x %02x %04x\n",rb[i&511][0],rb[i&511][1],rb[i&511][2]); fprintf(stdout,"END %ld\n",steps); }
    else if(!strcmp(cmd,"prof")){ long N=strtol(a,0,10); static unsigned cnt[0x200][0x4000/4]; memset(cnt,0,sizeof cnt); unsigned home[0x4000/4]; memset(home,0,sizeof home);
      for(long i=0;i<N;i++){ unsigned pc=gb->pc; if(pc<0x4000) home[pc>>2]++; else if(pc<0x8000) cnt[gb->mbc_rom_bank&0x1ff][(pc-0x4000)>>2]++; GB_run(gb);} 
      for(unsigned i=0;i<0x1000;i++) if(home[i]) fprintf(stdout,"P 00 %04x %u\n",i<<2,home[i]);
      for(unsigned b=0;b<0x200;b++) for(unsigned i=0;i<0x1000;i++) if(cnt[b][i]) fprintf(stdout,"P %02x %04x %u\n",b,0x4000+(i<<2),cnt[b][i]);
      fprintf(stdout,"END\n"); }
    else if(!strcmp(cmd,"pc")){ fprintf(stdout,"pc=%04x bank=%02x sp=%04x\n", gb->pc, gb->mbc_rom_bank, gb->registers[GB_REGISTER_SP]); }
  }
  return 0;
}
