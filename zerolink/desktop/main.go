package main

import (
 "bufio"
 "crypto/rand"
 "crypto/sha256"
 "crypto/subtle"
 "crypto/tls"
 "crypto/x509"
 "crypto/x509/pkix"
 "encoding/hex"
 "encoding/json"
 "encoding/pem"
 "fmt"
 "io"
 "math/big"
 "net"
 "net/http"
 "net/url"
 "os"
 "os/exec"
 "path/filepath"
 "runtime"
 "strings"
 "sync"
 "time"
)

type Entry struct { ID string `json:"id"`; Time string `json:"time"`; From string `json:"from"`; Kind string `json:"kind"`; Text string `json:"text"`; Name string `json:"name,omitempty"`; Size int64 `json:"size,omitempty"`; SHA string `json:"sha,omitempty"`; Path string `json:"-"` }
type Store struct { sync.Mutex; entries []Entry; dir, log string }
func random(n int) string { b:=make([]byte,n); if _,e:=rand.Read(b);e!=nil{panic(e)}; return hex.EncodeToString(b) }
func stamp() string{return time.Now().Format(time.RFC3339)}
func must(e error){if e!=nil{panic(e)}}
func saveSecret(path string) string { b,e:=os.ReadFile(path);if e==nil && len(b)==64{return string(b)};v:=random(32);must(os.WriteFile(path,[]byte(v),0600));return v }
func cert(dir string)(tls.Certificate,string){ cp,kp:=filepath.Join(dir,"cert.pem"),filepath.Join(dir,"key.pem")
 c,e:=tls.LoadX509KeyPair(cp,kp);if e!=nil{ 
  // Ed25519 is compact and supported by TLS 1.3; use a local self-signed identity.
  pub,priv,e:=edKey();must(e)
  tmpl:=x509.Certificate{SerialNumber:big.NewInt(time.Now().UnixNano()),Subject:pkix.Name{CommonName:"ZeroLink local receiver"},NotBefore:time.Now().Add(-time.Hour),NotAfter:time.Now().AddDate(10,0,0),KeyUsage:x509.KeyUsageDigitalSignature,ExtKeyUsage:[]x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth}}
  der,e:=x509.CreateCertificate(rand.Reader,&tmpl,&tmpl,pub,priv);must(e);key,e:=x509.MarshalPKCS8PrivateKey(priv);must(e)
  must(os.WriteFile(cp,pem.EncodeToMemory(&pem.Block{Type:"CERTIFICATE",Bytes:der}),0600));must(os.WriteFile(kp,pem.EncodeToMemory(&pem.Block{Type:"PRIVATE KEY",Bytes:key}),0600));c,e=tls.LoadX509KeyPair(cp,kp);must(e)
 };sum:=sha256.Sum256(c.Certificate[0]);return c,hex.EncodeToString(sum[:]) }
func (s *Store) load(){f,e:=os.Open(s.log);if e!=nil{return};defer f.Close();sc:=bufio.NewScanner(f);sc.Buffer(make([]byte,4096),1024*1024);for sc.Scan(){var x Entry;if json.Unmarshal(sc.Bytes(),&x)==nil{if x.Kind=="file"{x.Path=filepath.Join(s.dir,category(x.Name),x.ID+"_"+safeName(x.Name))};s.entries=append(s.entries,x);if len(s.entries)>500{s.entries=s.entries[1:]}}}}
func (s *Store) append(x Entry)error{s.Lock();defer s.Unlock();f,e:=os.OpenFile(s.log,os.O_CREATE|os.O_APPEND|os.O_WRONLY,0600);if e!=nil{return e};e=json.NewEncoder(f).Encode(x);if e==nil{e=f.Sync()};f.Close();if e!=nil{return e};s.entries=append(s.entries,x);if len(s.entries)>500{s.entries=s.entries[1:]};return nil}
func (s *Store) history(w http.ResponseWriter){s.Lock();defer s.Unlock();w.Header().Set("Content-Type","application/json");if s.entries==nil{io.WriteString(w,"[]");return};json.NewEncoder(w).Encode(s.entries)}
func category(n string)string{switch strings.ToLower(filepath.Ext(n)){case ".jpg",".jpeg",".png",".gif",".webp",".heic",".avif":return "Photos";case ".mp4",".mkv",".mov",".avi",".webm":return "Videos";case ".pdf",".doc",".docx",".txt",".pptx",".xlsx",".csv":return "Documents";case ".mp3",".wav",".m4a",".flac",".ogg":return "Audio";case ".zip",".rar",".7z",".tar",".gz":return "Archives";default:return "Other"}}
func safeName(n string)string{n=filepath.Base(strings.ReplaceAll(n,"\\","/"));n=strings.Map(func(r rune)rune{if r<32||strings.ContainsRune(`<>:"/\|?*`,r){return '_'};return r},n);n=strings.Trim(n," .");if n==""||n=="."||n==".."{n="file"};rs:=[]rune(n);if len(rs)>100{n=string(rs[:100])};return n}
func respond(w http.ResponseWriter,x Entry){w.Header().Set("Content-Type","application/json");json.NewEncoder(w).Encode(x)}
func (s *Store) message(w http.ResponseWriter,r *http.Request,from string){if r.Method!="POST"{http.Error(w,"POST required",405);return};r.Body=http.MaxBytesReader(w,r.Body,65536);var v struct{Text string};if json.NewDecoder(r.Body).Decode(&v)!=nil||strings.TrimSpace(v.Text)==""{http.Error(w,"Invalid text",400);return};x:=Entry{ID:random(8),Time:stamp(),From:from,Kind:"text",Text:v.Text};if e:=s.append(x);e!=nil{http.Error(w,"Cannot save message",507);return};respond(w,x);if from=="phone"{notify("ZeroLink • New message",v.Text)}}
func (s *Store) file(w http.ResponseWriter,r *http.Request){if r.Method!="POST"{http.Error(w,"POST required",405);return};n:=safeName(r.URL.Query().Get("name"));id:=random(8);folder:=filepath.Join(s.dir,category(n));if e:=os.MkdirAll(folder,0700);e!=nil{http.Error(w,"Cannot create folder",507);return};f,e:=os.CreateTemp(folder,".zerolink-*.part");if e!=nil{http.Error(w,"Cannot create file",507);return};tmp:=f.Name();defer os.Remove(tmp);h:=sha256.New();size,e:=io.CopyBuffer(io.MultiWriter(f,h),r.Body,make([]byte,128*1024));if e==nil{e=f.Sync()};f.Close();if e!=nil||(r.ContentLength>=0&&size!=r.ContentLength){http.Error(w,"Incomplete transfer",400);return};sum:=hex.EncodeToString(h.Sum(nil));want:=r.Header.Get("X-File-SHA256");if want!=""&&!strings.EqualFold(want,sum){http.Error(w,"Checksum mismatch",422);return};dest:=filepath.Join(folder,id+"_"+n);if e=os.Rename(tmp,dest);e!=nil{http.Error(w,"Cannot save file",507);return};x:=Entry{ID:id,Time:stamp(),From:"phone",Kind:"file",Name:n,Size:size,SHA:sum,Path:dest};if e=s.append(x);e!=nil{os.Remove(dest);http.Error(w,"Cannot save history",507);return};respond(w,x);notify("ZeroLink • File saved",n)}
func ips()[]string{var out []string;as,_:=net.InterfaceAddrs();for _,a:=range as{if n,ok:=a.(*net.IPNet);ok&&n.IP.To4()!=nil&&!n.IP.IsLoopback()&&n.IP.IsPrivate(){out=append(out,n.IP.String())}};return out}
func openURL(u string){if runtime.GOOS=="windows"{exec.Command("rundll32","url.dll,FileProtocolHandler",u).Start()}else{exec.Command("xdg-open",u).Start()}}
var notices=make(chan [2]string,32)
func notify(title,body string){select{case notices<-[2]string{title,body}:default:}}
func notificationWorker(){for m:=range notices{if runtime.GOOS!="windows"{continue};r:=[]rune(m[1]);if len(r)>180{r=r[:180]};cmd:=exec.Command("powershell.exe","-NoProfile","-NonInteractive","-WindowStyle","Hidden","-Command",`Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; $n=New-Object System.Windows.Forms.NotifyIcon; $n.Icon=[System.Drawing.SystemIcons]::Information; $n.Visible=$true; $n.ShowBalloonTip(3500,$env:ZL_TITLE,$env:ZL_BODY,[System.Windows.Forms.ToolTipIcon]::Info); Start-Sleep -Milliseconds 4000; $n.Dispose()`);cmd.Env=append(os.Environ(),"ZL_TITLE="+m[0],"ZL_BODY="+string(r));cmd.Run()}}
func main(){base,e:=os.UserConfigDir();must(e);base=filepath.Join(base,"ZeroLink");must(os.MkdirAll(base,0700));home,e:=os.UserHomeDir();must(e);dest:=filepath.Join(home,"Downloads","ZeroLink");must(os.MkdirAll(dest,0700));s:=&Store{dir:dest,log:filepath.Join(base,"history.jsonl")};s.load();token:=saveSecret(filepath.Join(base,"pair.token"));c,fp:=cert(base);go notificationWorker()
 api:=http.NewServeMux();api.HandleFunc("/history",func(w http.ResponseWriter,r *http.Request){s.history(w)});api.HandleFunc("/message",func(w http.ResponseWriter,r *http.Request){s.message(w,r,"phone")});api.HandleFunc("/file",s.file)
 secure:=http.HandlerFunc(func(w http.ResponseWriter,r *http.Request){host,_,e:=net.SplitHostPort(r.RemoteAddr);ip:=net.ParseIP(host);if e!=nil||ip==nil||(!ip.IsPrivate()&&!ip.IsLoopback()){http.Error(w,"Local network only",403);return};if subtle.ConstantTimeCompare([]byte(r.Header.Get("Authorization")),[]byte("Bearer "+token))!=1{http.Error(w,"Pairing required",401);return};api.ServeHTTP(w,r)})
 ln,e:=net.Listen("tcp4",":47821");must(e);srv:=&http.Server{Handler:secure,ReadHeaderTimeout:10*time.Second,IdleTimeout:60*time.Second,TLSConfig:&tls.Config{Certificates:[]tls.Certificate{c},MinVersion:tls.VersionTLS12}};go func(){must(srv.Serve(tls.NewListener(ln,srv.TLSConfig)))}()
 key:=random(24);prefix:="/"+key;ui:=http.NewServeMux();ui.HandleFunc(prefix+"/",func(w http.ResponseWriter,r *http.Request){w.Header().Set("Cache-Control","no-store");w.Header().Set("Referrer-Policy","no-referrer");w.Header().Set("X-Content-Type-Options","nosniff");switch strings.TrimPrefix(r.URL.Path,prefix){case "/":w.Header().Set("Content-Type","text/html; charset=utf-8");io.WriteString(w,page);case "/info":w.Header().Set("Content-Type","application/json");json.NewEncoder(w).Encode(map[string]any{"ips":ips(),"token":token,"fingerprint":fp,"folder":dest});case "/history":s.history(w);case "/message":s.message(w,r,"desktop");case "/download":id:=r.URL.Query().Get("id");s.Lock();var found Entry;for _,x:=range s.entries{if x.ID==id&&x.Kind=="file"{found=x;break}};s.Unlock();if found.Path==""{http.NotFound(w,r);return};w.Header().Set("Content-Disposition","attachment; filename*=UTF-8''"+url.PathEscape(found.Name));w.Header().Set("Content-Type","application/octet-stream");http.ServeFile(w,r,found.Path);default:http.NotFound(w,r)}})
 local,e:=net.Listen("tcp4","127.0.0.1:0");must(e);address:="http://"+local.Addr().String()+prefix+"/";fmt.Println("ZeroLink:",address,"\nKeep this process running. Files:",dest);openURL(address);must((&http.Server{Handler:ui,ReadHeaderTimeout:10*time.Second,IdleTimeout:60*time.Second}).Serve(local))
}
