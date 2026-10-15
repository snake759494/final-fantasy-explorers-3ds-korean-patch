using System;using System.IO;using System.Threading.Tasks;using System.Linq;
static class P{
 static byte[] Dec(byte[] d){
  uint enc=BitConverter.ToUInt32(d,d.Length-8);uint inc=BitConverter.ToUInt32(d,d.Length-4);
  int top=(int)(enc>>24),bottom=(int)(enc&0xffffff);
  var o=new byte[d.Length+inc];Array.Copy(d,o,d.Length);
  int src=d.Length-top,dst=o.Length,end=d.Length-bottom;
  while(src>end){byte fl=o[--src];
   for(int i=0;i<8&&src>end;i++){
    if((fl&0x80)!=0){src-=2;int v=o[src]|(o[src+1]<<8);int n=(v>>12)+3,disp=(v&0xfff)+3;
      for(int k=0;k<n;k++){dst--;o[dst]=o[dst+disp];}}
    else{o[--dst]=o[--src];}
    fl<<=1;}}
  return o;}
 static void Main(string[] a){
  if(a[0]=="dec"){var files=Directory.GetFiles(a[1]);Directory.CreateDirectory(a[2]);
   Parallel.ForEach(files,f=>{var b=File.ReadAllBytes(f);byte[] r;
    if(b.Length>=8&&b[0]=='b'&&b[1]=='l'&&b[2]=='z'&&b[3]==0) r=Dec(b);
    else if(b.Length>=8&&b[0]=='n'&&b[1]=='o'&&b[2]=='n'&&b[3]=='e') r=b; else return;
    File.WriteAllBytes(Path.Combine(a[2],Path.GetFileName(f)),r.Skip(8).ToArray());});}
  else if(a[0]=="one"){File.WriteAllBytes(a[2],Dec(File.ReadAllBytes(a[1])));}
 }}
