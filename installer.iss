; installer.iss - Script para Inno Setup

[Setup]
AppName=CyberTrainer
AppVersion=1.0
DefaultDirName={pf}\CyberTrainer
DefaultGroupName=CyberTrainer
OutputDir=.
OutputBaseFilename=CyberTrainerSetup

[Files]
Source: "dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "npcap\npcap-1.82.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{commondesktop}\Cyber Trainer"; Filename: "{app}\app.exe"

[Run]
Filename: "{tmp}\Npcap-1.82.exe"; StatusMsg: "Instalando Npcap..."; Flags: waituntilterminated; Check: NeedsNpcap
Filename: "{app}\app.exe"; Description: "Iniciar Cyber Trainer"; Flags: nowait postinstall skipifsilent

[Code]
function NeedsNpcap(): Boolean;
begin
  // Busca wpcap.dll en System32 (Npcap o WinPcap)
  Result := not FileExists(ExpandConstant('{sys}\wpcap.dll'));
end;