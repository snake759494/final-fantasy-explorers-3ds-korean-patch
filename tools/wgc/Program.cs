using System;using System.Runtime.InteropServices;using System.Threading;using System.Threading.Tasks;
using Windows.Graphics.Capture;using Windows.Graphics.DirectX;using Windows.Graphics.DirectX.Direct3D11;using Windows.Graphics.Imaging;using Windows.Storage;using Windows.Storage.Streams;using WinRT;
static class P{
 [ComImport,Guid("3628E81B-3CAC-4C60-B7F4-23CE0E0C3356"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
 interface IGraphicsCaptureItemInterop{ IntPtr CreateForWindow(IntPtr w,ref Guid iid); IntPtr CreateForMonitor(IntPtr m,ref Guid iid);}
 [DllImport("d3d11.dll")] static extern int D3D11CreateDevice(IntPtr a,int type,IntPtr sw,uint flags,IntPtr fl,uint nfl,uint sdk,out IntPtr dev,out int lvl,out IntPtr ctx);
 [DllImport("d3d11.dll")] static extern int CreateDirect3D11DeviceFromDXGIDevice(IntPtr dxgi,out IntPtr insp);
 static async Task<int> Run(IntPtr hwnd,string outp){
  D3D11CreateDevice(IntPtr.Zero,1,IntPtr.Zero,0x20,IntPtr.Zero,0,7,out var dev,out _,out _);
  Guid gdxgi=new Guid("54ec77fa-1377-44e6-8c32-88fd5f44c84c");Marshal.QueryInterface(dev,ref gdxgi,out var dxgi);
  CreateDirect3D11DeviceFromDXGIDevice(dxgi,out var insp);
  var d3d=MarshalInterface<IDirect3DDevice>.FromAbi(insp);
  var fac=ActivationFactory.Get("Windows.Graphics.Capture.GraphicsCaptureItem");
  var interop=(IGraphicsCaptureItemInterop)Marshal.GetObjectForIUnknown(fac.ThisPtr);
  Guid gi=new Guid("79C3F95B-31F7-4EC2-A464-632EF5D30760");
  var itemPtr=interop.CreateForWindow(hwnd,ref gi);
  var item=MarshalInterface<GraphicsCaptureItem>.FromAbi(itemPtr);
  var pool=Direct3D11CaptureFramePool.CreateFreeThreaded(d3d,DirectXPixelFormat.B8G8R8A8UIntNormalized,1,item.Size);
  var sess=pool.CreateCaptureSession(item);
  try{sess.IsBorderRequired=false;}catch{}
  try{sess.IsCursorCaptureEnabled=false;}catch{}
  var tcs=new TaskCompletionSource<Direct3D11CaptureFrame>();
  int n=0;
  pool.FrameArrived+=(p,o)=>{var f=p.TryGetNextFrame();if(++n<3){f.Dispose();return;} tcs.TrySetResult(f);};
  sess.StartCapture();
  var t=await Task.WhenAny(tcs.Task,Task.Delay(5000));
  if(t!=tcs.Task){Console.WriteLine("timeout");return 1;}
  var fr=tcs.Task.Result;
  var sb=await SoftwareBitmap.CreateCopyFromSurfaceAsync(fr.Surface,BitmapAlphaMode.Premultiplied);
  var file=await StorageFile.GetFileFromPathAsync(outp).AsTask().ContinueWith(x=>x.IsFaulted?null:x.Result);
  if(file==null){var dir=await StorageFolder.GetFolderFromPathAsync(System.IO.Path.GetDirectoryName(outp));file=await dir.CreateFileAsync(System.IO.Path.GetFileName(outp),CreationCollisionOption.ReplaceExisting);}
  using(var st=await file.OpenAsync(FileAccessMode.ReadWrite)){st.Size=0;var enc=await BitmapEncoder.CreateAsync(BitmapEncoder.PngEncoderId,st);enc.SetSoftwareBitmap(sb);await enc.FlushAsync();}
  sess.Dispose();pool.Dispose();Console.WriteLine("ok "+item.Size.Width+"x"+item.Size.Height);return 0;}
 static int Main(string[] a){return Run(new IntPtr(Convert.ToInt64(a[0],16)),System.IO.Path.GetFullPath(a[1])).GetAwaiter().GetResult();}
}
