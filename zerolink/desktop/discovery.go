package main

import (
 "crypto/hmac"
 "crypto/sha256"
 "encoding/hex"
 "log"
 "net"
 "strconv"
 "strings"
 "time"
)

const discoveryPort = 47822
const phonePort = 47823
func mac(key, payload string) string { h:=hmac.New(sha256.New,[]byte(key));h.Write([]byte(payload));return hex.EncodeToString(h.Sum(nil)) }
func discoveryPacket(kind,key,fp string) []byte {
 p:=kind+"|"+fp+"|"+strconv.FormatInt(time.Now().Unix(),10)
 return []byte(p+"|"+mac(key,p))
}
func validDiscovery(b []byte, kind,key,fp string) bool {
 fields:=strings.Split(string(b),"|")
 if len(fields)!=4 || fields[0]!=kind || fields[1]!=fp{return false}
 ts,e:=strconv.ParseInt(fields[2],10,64);if e!=nil{return false}
 now:=time.Now().Unix();if ts<now-120||ts>now+120{return false}
 p:=strings.Join(fields[:3],"|")
 return hmac.Equal([]byte(fields[3]),[]byte(mac(key,p)))
}
func startDiscovery(key,fp string) {
 c,e:=net.ListenUDP("udp4",&net.UDPAddr{Port:discoveryPort})
 if e!=nil{log.Printf("Discovery unavailable: %v",e);return}
 defer c.Close()
 go func(){
  ticker:=time.NewTicker(8*time.Second);defer ticker.Stop()
  for {
   packet:=discoveryPacket("ZL1-BEACON",key,fp)
   for _,ip:=range localGateways(){if ip.IsPrivate(){c.WriteToUDP(packet,&net.UDPAddr{IP:ip,Port:phonePort})}}
   <-ticker.C
  }
 }()
 buf:=make([]byte,512)
 for {
  n,peer,e:=c.ReadFromUDP(buf);if e!=nil{return}
  if !peer.IP.IsPrivate() || !validDiscovery(buf[:n],"ZL1-QUERY",key,fp){continue}
  c.WriteToUDP(discoveryPacket("ZL1-BEACON",key,fp),peer)
 }
}
