param([switch]$Restore,[switch]$ValidateOnly)
$ErrorActionPreference='Stop'
Add-Type @"
using System;
using System.Text;
using System.Diagnostics;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class Notice {
 public delegate bool Callback(IntPtr w,IntPtr p);
 [DllImport("user32.dll")] static extern bool EnumWindows(Callback f,IntPtr p);
 [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr w,Callback f,IntPtr p);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr w,StringBuilder s,int n);
 [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr w,out uint p);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr w);
 [DllImport("user32.dll")] static extern bool ShowWindowAsync(IntPtr w,int command);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern IntPtr SendMessageTimeout(IntPtr w,uint m,UIntPtr n,StringBuilder s,uint flags,uint ms,out UIntPtr result);
 static string Class(IntPtr w){var s=new StringBuilder(256);GetClassName(w,s,256);return s.ToString();}
 public static bool Matches(IntPtr w){
  if(Class(w)!="#32770")return false;
  uint pid;GetWindowThreadProcessId(w,out pid);
  try{if(!String.Equals(Process.GetProcessById((int)pid).ProcessName,"BaiduNetdiskUnite",StringComparison.OrdinalIgnoreCase))return false;}catch{return false;}
  bool found=false;
  EnumChildWindows(w,delegate(IntPtr c,IntPtr p){
   if(Class(c)!="Static")return true;
   var s=new StringBuilder(1024);UIntPtr result;
   if(SendMessageTimeout(c,13,(UIntPtr)1024,s,2,150,out result)!=IntPtr.Zero){
    string t=s.ToString();found|=t.Contains("\u5e94\u7528\u7a0b\u5e8f\u88ab\u4fee\u6539")&&t.Contains("\u8bf7\u91cd\u65b0\u5b89\u88c5");
   }return true;
  },IntPtr.Zero);return found;
 }
 public static IntPtr[] Find(){var a=new List<IntPtr>();EnumWindows(delegate(IntPtr w,IntPtr p){if(Matches(w))a.Add(w);return true;},IntPtr.Zero);return a.ToArray();}
 public static bool SetVisible(IntPtr w,bool visible){return Matches(w)&&ShowWindowAsync(w,visible?4:0);}
}
"@
if($ValidateOnly){Write-Host 'Helper compiled. No windows changed.';exit 0}
if($Restore){foreach($w in [Notice]::Find()){if(-not [Notice]::IsWindowVisible($w)){[void][Notice]::SetVisible($w,$true)}};Write-Host 'Restore requests sent.';exit 0}
$hidden=New-Object 'System.Collections.Generic.HashSet[System.IntPtr]'
Write-Host 'Watching ONLY the BaiduNetdiskUnite modification warning.'
Write-Host 'Keep this window running. Ctrl+C stops and requests restoration.'
Write-Host 'If forcibly closed, use Restore-Notice.cmd to show the notice.'
try{
 while($true){
  foreach($w in [Notice]::Find()){
   if([Notice]::IsWindowVisible($w) -and [Notice]::SetVisible($w,$false)){
    [void]$hidden.Add($w);Write-Host ('Hide requested: 0x{0:X}' -f $w.ToInt64())
   }
  }
  Start-Sleep -Milliseconds 250
 }
}finally{foreach($w in $hidden){[void][Notice]::SetVisible($w,$true)}}
