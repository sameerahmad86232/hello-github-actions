package main
import("testing";"strings";"strconv";"time")
func TestDiscoveryAuthentication(t *testing.T){
 k:="secret";fp:="fingerprint"
 p:=discoveryPacket("ZL1-BEACON",k,fp)
 if !validDiscovery(p,"ZL1-BEACON",k,fp){t.Fatal("valid beacon rejected")}
 if validDiscovery(p,"ZL1-BEACON","wrong",fp)||validDiscovery(p,"ZL1-QUERY",k,fp)||validDiscovery(p,"ZL1-BEACON",k,"other"){t.Fatal("untrusted beacon accepted")}
 stale:="ZL1-BEACON|"+fp+"|"+strconv.FormatInt(time.Now().Unix()-121,10)
 if validDiscovery([]byte(stale+"|"+mac(k,stale)),"ZL1-BEACON",k,fp){t.Fatal("stale beacon accepted")}
 if validDiscovery([]byte(strings.Replace(string(p),fp,"forged",1)),"ZL1-BEACON",k,fp){t.Fatal("tampered beacon accepted")}
}
