# ZeroLink 0.1 — offline hotspot messaging
Experimental Android + Windows MVP. No remote servers, accounts, or subscriptions.

## Install
Download the Windows and Android artifacts from the branch's GitHub Actions build when successful. Unzip the artifact bundles. Android APK is a debug-signed development build; Windows EXE is unsigned. Verify origin before installation.

1. Enable your phone hotspot; connect Windows to it. Mobile data can be off if the device permits hotspot without upstream data.
2. Run ZeroLink.exe on Windows. The receiver opens a local browser dashboard. Keep the receiver process running; closing the tab is safe. The optional install-autostart.cmd copies the exe to LocalAppData and adds a current-user startup entry.
3. Windows Firewall may need an explicit inbound rule for TCP 47821 on the hotspot network profile. Do not disable the firewall; scope a rule to the phone's local IP or hotspot subnet.
4. Open the Android app and enter one of the shown local IPv4 addresses (choose the hotspot adapter), the pairing key and certificate fingerprint. Keep the pairing key secret. If the IP changes, change it in the app.
5. Send a message or attach a file. Android's Share sheet also supports ZeroLink. The receiver saves files to Downloads/ZeroLink by type and displays messages in chat. Desktop can reply with text while the phone app is open.

## Build
Desktop: Go 1.22+; from desktop, run go test ./... and GOOS=windows GOARCH=amd64 go build -trimpath -ldflags="-s -w" -o ZeroLink.exe . (set environment variables separately on Windows).
Android: JDK 17, Android SDK 35, Gradle 8.9; from android, run gradle assembleDebug.

## Security and limits
TLS with certificate fingerprint pinning and random bearer key. Receiver only accepts private-network/loopback source addresses. Files use sanitized names, unique IDs, chunked streaming and atomic rename. SHA-256 is compared on sender after transfer. No auto-execution. Keep the hotspot private. The browser UI binds to loopback and uses an unguessable URL; do not share that URL.
This MVP is phone-to-desktop files and bidirectional text, manual pairing, foreground Android transfers, last 500 visible history entries, and Windows balloon notifications (subject to notification settings). No automatic retry/queue across app restarts, QR pairing, file resume, duplicate detection, notification actions, image previews, Android background sync, or Windows native chat window yet. Desktop UI opens in the system browser only on launch; receiver itself has no bundled browser engine. Windows startup script opens the receiver console and dashboard; silent tray mode is not implemented. Resource use and real hotspot compatibility have not been measured.
Stored messages and received files use disk space. The receiver does not store a second full copy of files. Delete pair.token in the ZeroLink configuration folder while the receiver is stopped to revoke the shared key; pair again afterward. Delete the startup registry entry to disable auto-start.
