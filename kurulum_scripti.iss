; Inno Setup Script
; StokGold Programı için Nihai Kurulum Reçetesi

[Setup]
AppId={{StokGold-C1B2A3D4}}
AppName=StokGold
AppVersion=1.1
AppPublisher=Aykut Ay
DefaultDirName={autopf}\StokGold
DefaultGroupName=StokGold
DisableProgramGroupPage=yes
OutputDir=.\SetupOutput1.1
OutputBaseFilename=StokGold-Setup
SetupIconFile=assets\icons\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\StokGold.exe

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

; --- EN ÖNEMLİ DEĞİŞİKLİK BURADA ---
[Files]
; Artık sadece ana .exe dosyasını ve programın çalışması için gereken
; sabit assets klasörünü (ikonlar için) alıyoruz.
; Veritabanı, resimler ve config dosyaları kurulumla gelmiyor, 
; program ilk açılışta kullanıcının AppData klasöründe kendisi oluşturuyor.
Source: "dist\StokGold.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
Name: "{group}\StokGold"; Filename: "{app}\StokGold.exe"
Name: "{group}\{cm:UninstallProgram,StokGold}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\StokGold"; Filename: "{app}\StokGold.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\StokGold.exe"; Description: "{cm:LaunchProgram,StokGold}"; Flags: nowait postinstall skipifsilent