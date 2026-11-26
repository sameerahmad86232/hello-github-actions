//go:build windows

package main

import (
 "encoding/binary"
 "net"
 "syscall"
 "unsafe"
)

var forwardTable=syscall.NewLazyDLL("iphlpapi.dll").NewProc("GetIpForwardTable")
func localGateways() []net.IP {
 var size uint32
 forwardTable.Call(0,uintptr(unsafe.Pointer(&size)),0)
 if size<4||size>16*1024*1024{return nil}
 b:=make([]byte,size)
 rc,_,_:=forwardTable.Call(uintptr(unsafe.Pointer(&b[0])),uintptr(unsafe.Pointer(&size)),0)
 if rc!=0{return nil}
 // MIB_IPFORWARDTABLE: count followed by fixed 14-DWORD rows.
 count:=int(binary.LittleEndian.Uint32(b[:4]));out:=[]net.IP{};seen:=map[string]bool{}
 for i:=0;i<count;i++{
  off:=4+i*56;if off+56>len(b){break};row:=b[off:off+56]
  if binary.LittleEndian.Uint32(row[:4])!=0||binary.LittleEndian.Uint32(row[4:8])!=0{continue}
  ip:=net.IPv4(row[12],row[13],row[14],row[15]);if !ip.IsPrivate()||seen[ip.String()]{continue}
  seen[ip.String()]=true;out=append(out,ip)
 }
 return out
}
