; installer.iss - Script para Inno Setup

[Setup]
AppName=CyberTrainer
AppVersion=1.0
PrivilegesRequired=admin
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
; Se instala Npcap de forma silenciosa (/S) asegurando que el modo de compatibilidad
; con WinPcap y el adaptador de loopback estén activados. El modo /q es para la versión gratuita.
Filename: "{tmp}\Npcap-1.82.exe"; Parameters: "/q /winpcap_mode=yes /loopback=yes"; StatusMsg: "Instalando Npcap..."; Flags: waituntilterminated; Check: NeedsNpcap

Filename: "{app}\app.exe"; Description: "Iniciar Cyber Trainer"; Flags: nowait postinstall skipifsilent

[Code]
function NeedsNpcap(): Boolean;
var
  Version: string;
begin
  // Es más fiable buscar la clave de registro de Npcap que un solo archivo DLL.
  // Esto asegura que Npcap (y no el antiguo WinPcap) esté instalado.
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Npcap', 'DisplayVersion', Version) then
  begin
    // Npcap ya está instalado.
    Result := False;
  end
  else
    // Npcap no está instalado, por lo que se necesita.
    Result := True;
end;