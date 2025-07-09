; installer.iss - Script para Inno Setup

; --- Definiciones del Preprocesador ---
; Estas variables se usan para configurar el instalador antes de compilar.
#define MyAppName "CyberTrainer"
#define MyAppVersion "1.0"
; Define un valor por defecto para SourcePath. El script .bat lo sobreescribirá.
#define SourcePath "."

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
PrivilegesRequired=admin
SetupIconFile="{#SourcePath}\assets\images\app_icon.ico"
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=.
OutputBaseFilename="{#MyAppName}Setup-v{#MyAppVersion}"

[Files]
Source: "dist\CyberTrainer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "npcap\npcap-1.82.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
; Crea un icono en el Menú de Inicio para todos los usuarios
Name: "{commonprograms}\CyberTrainer"; Filename: "{app}\CyberTrainer.exe"
; Crea un icono en el Escritorio para todos los usuarios
Name: "{commondesktop}\CyberTrainer"; Filename: "{app}\CyberTrainer.exe"; Tasks: desktopicon

[Run]
; Se instala Npcap de forma silenciosa (/S) asegurando que el modo de compatibilidad
; con WinPcap y el adaptador de loopback estén activados. El modo /q es para la versión gratuita.
Filename: "{tmp}\Npcap-1.82.exe"; Parameters: "/q /winpcap_mode=yes /loopback=yes"; StatusMsg: "Instalando Npcap..."; Flags: waituntilterminated; Check: NeedsNpcap

Filename: "{app}\CyberTrainer.exe"; Description: "Iniciar CyberTrainer"; Flags: nowait postinstall skipifsilent

[Tasks]
; Añade una casilla de verificación en el instalador para que el usuario decida si quiere un icono en el escritorio
Name: "desktopicon"; Description: "Crear un icono en el escritorio"; GroupDescription: "Accesos directos:";

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