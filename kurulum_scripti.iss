; Inno Setup Script
; StokGold Programı için Kurulum Reçetesi (Tek Dosya .exe Modu)

[Setup]
AppId={{StokGold-C1B2A3D4}}
AppName=StokGold
AppVersion=1.0
AppPublisher=Aykut Ay
DefaultDirName={autopf}\StokGold
DefaultGroupName=StokGold
DisableProgramGroupPage=yes
OutputDir=.\SetupOutput
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

; --- DEĞİŞİKLİK BURADA ---
[Files]
; Artık tek bir klasörü değil, gerekli dosyaları tek tek belirtiyoruz.
; Bu yollar, .iss script'inin bulunduğu ana proje dizinine göredir.
Source: "dist\StokGold.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "kuyumcu.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.ini"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\StokGold"; Filename: "{app}\StokGold.exe"
Name: "{group}\{cm:UninstallProgram,StokGold}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\StokGold"; Filename: "{app}\StokGold.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\StokGold.exe"; Description: "{cm:LaunchProgram,StokGold}"; Flags: nowait postinstall skipifsilent