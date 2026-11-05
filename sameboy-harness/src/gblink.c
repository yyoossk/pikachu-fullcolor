// Two headless SameBoy instances connected by a link cable, driven by a script on stdin.
// Commands take the instance number (1 or 2) where needed:
//   wait N                 run both until instance 1 has N more frames
//   press W KEYS N         hold KEYS on instance W for N frames (then 4 frames released)
//   down W KEYS / up W KEYS
//   shot W file.ppm
//   peek W addr N / poke W addr val
//   bload W file / bsave W file / reset W
//   call W bank:addr
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <Core/gb.h>
static GB_gameboy_t *gb[2]; static uint32_t px[2][256*224]; static int vbl[2];
static bool bit_out[2];
static void vblank0(GB_gameboy_t *g, GB_vblank_type_t t){ vbl[0]=1; }
static void vblank1(GB_gameboy_t *g, GB_vblank_type_t t){ vbl[1]=1; }
static uint32_t enc(GB_gameboy_t *g,uint8_t r,uint8_t gg,uint8_t b){return (r<<16)|(gg<<8)|b;}
static char *noinput(GB_gameboy_t *g){return NULL;}
static void logcb(GB_gameboy_t *g,const char *s,GB_log_attributes_t a){}
static int idx(GB_gameboy_t *g){ return g==gb[0]?0:1; }
static void bit_start(GB_gameboy_t *g, bool bit){ bit_out[idx(g)]=bit; }
static bool bit_end(GB_gameboy_t *g){ int i=idx(g), o=1-i;
  bool ret=GB_serial_get_data_bit(gb[o]); GB_serial_set_data_bit(gb[o], bit_out[i]); return ret; }
static long long cyc[2];
static void frames(int n){
  for(int f=0;f<n;f++){ vbl[0]=0;
    while(!vbl[0]){
      // keep the two machines within a small number of cycles of each other
      if(cyc[0]<=cyc[1]) cyc[0]+=GB_run(gb[0]); else cyc[1]+=GB_run(gb[1]);
    }
  }
}
static int keyidx(char c){ switch(c){case 'R':return GB_KEY_RIGHT;case 'L':return GB_KEY_LEFT;case 'U':return GB_KEY_UP;case 'D':return GB_KEY_DOWN;case 'A':return GB_KEY_A;case 'B':return GB_KEY_B;case 'S':return GB_KEY_START;case 's':return GB_KEY_SELECT;} return -1;}
static void keys(int w,const char*a,int st){ for(const char*p=a;*p;p++){int k=keyidx(*p); if(k>=0) GB_set_key_state(gb[w],k,st);} }
int main(int argc,char**argv){
  if(argc<4){fprintf(stderr,"gblink rom1 rom2 bootrom < script\n");return 1;}
  for(int i=0;i<2;i++){
    gb[i]=GB_alloc(); GB_init(gb[i], GB_MODEL_CGB_E);
    GB_load_boot_rom(gb[i], argv[3]); GB_load_rom(gb[i], argv[1+i]);
    GB_set_vblank_callback(gb[i], i?vblank1:vblank0); GB_set_rgb_encode_callback(gb[i], enc);
    GB_set_pixels_output(gb[i], px[i]); GB_set_log_callback(gb[i], logcb);
    GB_set_async_input_callback(gb[i], noinput); GB_set_input_callback(gb[i], noinput);
    GB_set_color_correction_mode(gb[i], GB_COLOR_CORRECTION_DISABLED);
    GB_set_turbo_mode(gb[i], true, true);
    GB_set_serial_transfer_bit_start_callback(gb[i], bit_start);
    GB_set_serial_transfer_bit_end_callback(gb[i], bit_end);
  }
  char line[512]; setvbuf(stdout,NULL,_IOLBF,0);
  while(fgets(line,sizeof line,stdin)){
    char cmd[64]={0}, a[256]={0}, b[256]={0}; int w=0, n=0;
    sscanf(line,"%63s",cmd);
    if(!strcmp(cmd,"wait")){ sscanf(line,"%*s %d",&n); frames(n); continue; }
    sscanf(line,"%*s %d %255s %255s",&w,a,b); w=(w==2)?1:0; n=atoi(b);
    if(!strcmp(cmd,"press")){ keys(w,a,1); frames(n?n:4); keys(w,a,0); frames(4); }
    else if(!strcmp(cmd,"down")) keys(w,a,1);
    else if(!strcmp(cmd,"up")) keys(w,a,0);
    else if(!strcmp(cmd,"shot")){ FILE*f=fopen(a,"wb"); fprintf(f,"P6 160 144 255\n"); for(int i=0;i<160*144;i++){uint8_t c[3]={px[w][i]>>16,px[w][i]>>8,px[w][i]}; fwrite(c,1,3,f);} fclose(f); }
    else if(!strcmp(cmd,"peek")){ unsigned ad=strtoul(a,0,16); fprintf(stdout,"%04x:",ad); for(int i=0;i<(n?n:16);i++) fprintf(stdout," %02x",GB_safe_read_memory(gb[w],ad+i)); fprintf(stdout,"\n"); }
    else if(!strcmp(cmd,"poke")){ unsigned ad=strtoul(a,0,16); GB_write_memory(gb[w],ad,(uint8_t)strtoul(b,0,10)); }
    else if(!strcmp(cmd,"bload")) GB_load_battery(gb[w],a);
    else if(!strcmp(cmd,"bsave")) GB_save_battery(gb[w],a);
    else if(!strcmp(cmd,"reset")) GB_reset(gb[w]);
    else if(!strcmp(cmd,"call")){ unsigned bank=strtoul(a,0,16)>>16, addr=strtoul(a,0,16)&0xffff; GB_gameboy_t*g=gb[w];
      uint16_t sp=g->registers[GB_REGISTER_SP]-2; GB_write_memory(g,sp,g->pc&255); GB_write_memory(g,sp+1,g->pc>>8);
      g->registers[GB_REGISTER_SP]=sp; GB_write_memory(g,0x2000,bank); GB_write_memory(g,0xffb8,bank); g->pc=addr; }
    else if(!strcmp(cmd,"pc")) fprintf(stdout,"pc=%04x bank=%02x\n", gb[w]->pc, gb[w]->mbc_rom_bank);
  }
  return 0;
}
