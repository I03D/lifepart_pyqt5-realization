#define MyAppName "LifePart"
#define MyAppVersion "1.0"
#define MyAppPublisher "I03D"
#define MyAppURL "https://github.com/I03D/LifePart"
#define MyAppExeName "lifepart.pyw"
#define DoubleAmp(Value) StringChange(Value, "&", "&&")

[Setup]
AppId={{B35DD25D-DE65-46BE-982B-8405F753805E}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
CloseApplications=yes
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=C:\Users\user\Desktop\lifepart_pyqt5-realization-main
OutputBaseFilename=Setup LifePart
SolidCompression=yes
WizardStyle=modern dynamic


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 1. Копируем основной файл
Source: "{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; 2. Обязательно копируем значок
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; 3. Копируем остальные файлы
Source: "*"; DestDir: "{app}"; Excludes: "*.pyw *.ico"; Flags: ignoreversion 

[Icons]
; Явно указываем иконку
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#DoubleAmp(MyAppName)}}"; Flags: shellexec postinstall skipifsilent
