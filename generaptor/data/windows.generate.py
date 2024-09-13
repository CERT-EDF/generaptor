#!/usr/bin/env python3
"""Generate windows.targets.csv and windows.rules.csv
"""
from io import StringIO
from csv import DictReader, DictWriter
from json import loads
from pathlib import Path
from operator import itemgetter
from collections import defaultdict
from urllib.request import urlopen
from yaml import safe_load


TARGETS_MAPPING = {
    '_BasicCollection': 'Triage/Basic',
    '_KapeTriage': 'Triage/Kape',
    '_SANS_Triage': 'Triage/SANS',
    '_Boot': 'SystemFile/Boot',
    '_J': 'SystemFile/J',
    '_LogFile': 'SystemFile/LogFile',
    '_MFT': 'SystemFile/MFT',
    '_MFTMirr': 'SystemFile/MFTMirr',
    '_SDS': 'SystemFile/Secure',
    '_T': 'SystemFile/T',
    '1Password': 'Vault/1Password',
    '4KVideoDownloader': 'FileTransfer/4KVideoDownloader',
    'AVG': 'Protection/AVG',
    'AceText': 'Editor/AceText',
    'AcronisTrueImage': 'Backup/Acronis',
    'Action1': 'Protection/Action1',
    'ActiveDirectoryNTDS': 'SystemFile/NTDS',
    'ActiveDirectorySysvol': 'SystemFile/SYSVOL',
    'AgentRansack': 'FileManager/AgentRansack',
    'Amcache': 'SystemFile/Amcache',
    'Ammyy': 'RMM/Ammyy',
    'Antivirus': 'Protection/*',
    'AnyDesk': 'RMM/AnyDesk',
    'ApacheAccessLog': 'Web/Server/Apache',
    'AppCompatPCA': 'SystemFile/AppCompatPCA',
    'AppData': 'UserFile/AppData',
    'AppXPackages': 'SystemFile/AppXPackages',
    'ApplicationEvents': 'SystemFile/Logs',
    'AsperaConnect': 'FileTransfer/AsperaConnect',
    'AteraAgent': 'RMM/AteraAgent',
    'Avast': 'Protection/Avast',
    'AviraAVLogs': 'Protection/Avira',
    'BCD': 'SystemFile/BCD',
    'BITS': 'FileTransfer/BITS',
    'BitTorrent': 'FileTransfer/BitTorrent',
    'Bitdefender': 'Protection/Bitdefender',
    'BoxDrive_Metadata': 'FileTransfer/BoxDrive/Metadata',
    'BoxDrive_UserFiles': 'UserFile/BoxDrive',
    'BraveBrowser': 'Web/Browser/Brave',
    'BrowserCache': 'Web/Browser/*/Cache',
    'CertUtil': None,
    'Chrome': 'Web/Browser/Chrome/Metadata',
    'ChromeExtensions': 'Web/Browser/Chrome/Extensions',
    'ChromeFileSystem': 'Web/Browser/Chrome/FileSystem',
    'CiscoJabber': 'Messaging/CiscoJabber',
    'ClipboardMaster': 'Screenshot/ClipboardMaster',
    'CloudStorage_All': 'FileTransfer/*',
    'CloudStorage_Metadata': 'FileTransfer/*',
    'CloudStorage_OneDriveExplorer': 'FileTransfer/OneDrive',
    'CombinedLogs': 'SystemFile/Logs',
    'Combofix': 'Protection/Combofix',
    'ConfluenceLogs': 'Wiki/Confluence',
    'Cybereason': 'Protection/Cybereason',
    'Cylance': 'Protection/Cylance',
    'DC__': 'FileTransfer/DC++',
    'DWAgent': 'RMM/DWService',
    'Debian': 'WSL/Debian',
    'DirectoryOpus': 'FileManager/DirectoryOpus',
    'DirectoryTraversal_AudioFiles': 'UserFile/Audio',
    'DirectoryTraversal_ExcelDocuments': 'UserFile/Office/Excel',
    'DirectoryTraversal_PDFDocuments': 'UserFile/PDF',
    'DirectoryTraversal_PictureFiles': 'UserFile/Picture',
    'DirectoryTraversal_SQLiteDatabases': 'UserFile/SQLite',
    'DirectoryTraversal_VideoFiles': 'UserFile/Video',
    'DirectoryTraversal_WildCardExample': None,
    'DirectoryTraversal_WordDocuments': 'UserFile/Office/Word',
    'Discord': 'Messaging/Discord',
    'DoubleCommander': 'FileManager/DirectoryOpus',
    'Drivers': 'SystemFile/Drivers',
    'Dropbox_Metadata': 'FileTransfer/Dropbox/Metadata',
    'Dropbox_UserFiles': 'UserFile/Dropbox',
    'EFCommander': 'FileManager/EFCommander',
    'ESET': 'Protection/ESET',
    'Edge': 'Web/Browser/Edge',
    'EdgeChromium': 'Web/Browser/Edgium/Metadata',
    'EdgeChromiumExtensions': 'Web/Browser/Edgium/Extensions',
    'Emsisoft': 'Protection/Emsisoft',
    'EncapsulationLogging': 'SystemFile/EncapsulationLogging',
    'EventLogs_RDP': 'SystemFile/Logs/RDP',
    'EventLogs': 'SystemFile/Logs',
    'EventTraceLogs': 'SystemFile/Logs/ETL',
    'EventTranscriptDB': 'SystemFile/EventTranscriptDB',
    'Evernote': 'Editor/Evernote',
    'Everything__VoidTools_': 'FileManager/VoidTools',
    'EvidenceOfExecution': None,
    'Exchange': 'WindowsServer/Exchange',
    'ExchangeClientAccess': 'WindowsServer/Exchange',
    'ExchangeCve_2021_26855': 'WindowsServer/Exchange',
    'ExchangeSetupLog': 'WindowsServer/Exchange',
    'ExchangeTransport': 'WindowsServer/Exchange',
    'FSecure': 'Protection/FSecure',
    'FTPClients': 'FileTransfer/*',
    'Fences': 'Desktop/Fences',
    'FileExplorerReplacements': 'FileManager/*',
    'FileSystem': 'SystemFile/FileSystem',
    'FileZillaClient': 'FileTransfer/FileZilla/Client',
    'FileZillaServer': 'FileTransfer/FileZilla/Server',
    'Firefox': 'Web/Browser/Firefox',
    'FreeCommander': 'FileManager/FreeCommander',
    'FreeDownloadManager': 'FileTransfer/FreeDownloadManager',
    'FreeFileSync': 'FileTransfer/FreeFileSync',
    'Freenet': 'FileTransfer/Freenet',
    'FrostWire': 'FileTransfer/FrostWire',
    'Gigatribe': 'FileTransfer/Gigatribe',
    'GoogleDriveBackupSync_UserFiles': 'UserFile/GoogleDrive',
    'GoogleDrive_Metadata': 'FileTransfer/GoogleDrive/Metadata',
    'GoogleEarth': 'Reader/GoogleEarth',
    'GroupPolicy': 'SystemFile/GroupPolicy',
    'HeidiSQL': 'Database/HeidiSQL',
    'HexChat': 'Messaging/HexChat',
    'HitmanPro': 'Protection/HitmanPro',
    'IISConfiguration': 'Web/Server/IIS',
    'IISLogFiles': 'Web/Server/IIS',
    'IRCClients': 'Messaging/IRC/*',
    'ISLOnline': 'RMM/ISLOnline',
    'IceChat': 'Messaging/IceChat',
    'IconCacheDB': 'SystemFile/IconCacheDB',
    'Idrive': 'Backup/Idrive',
    'ImgBurn': 'Burner/ImgBurn',
    'InternetExplorer': 'Web/Browser/IE',
    'IrfanView': 'Reader/IrfanView',
    'JDownloader2': 'FileTransfer/JDownloader2',
    'JavaWebCache': 'FileTransfer/JavaWebCache',
    'Kali': 'WSL/Kali',
    'KapeTriage': 'Triage/Kape',
    'Kaseya': 'RMM/Kaseya',
    'Keepass': 'Vault/Keepass',
    'KeepassXC': 'Vault/KeepassXC',
    'LNKFilesAndJumpLists': 'SystemFile/LinksAndJumpLists',
    'Level': None,
    'LinuxOnWindowsProfileFiles': 'WSL/*/ProfileFiles',
    'LiveUserFiles': 'UserFile/*',
    'LogFiles': 'SystemFile/Logs',
    'LogMeIn': 'VPN/LogMeIn',
    'MOF': 'SystemFile/MOF',
    'MSSQLErrorLog': 'Database/MSSQL',
    'MacriumReflect': 'Backup/MacriumReflect',
    'Malwarebytes': 'Protection/Malwarebytes',
    'ManageEngineLogs': 'RMM/ManageEngine',
    'Mattermost': 'Messaging/Mattermost',
    'McAfee': 'Protection/McAfee',
    'McAfee_ePO': 'Protection/McAfee_ePO',
    'MediaMonkey': 'Reader/MediaMonkey',
    'Megasync': 'FileTransfer/Megasync',
    'MemoryFiles': 'SystemFile/Memory',
    'MeshAgent': 'RMM/MeshAgent',
    'MessagingClients': 'Messaging/*',
    'MicrosoftOfficeBackstage': 'SystemFile/OfficeBackstage',
    'MicrosoftOneNote': 'Editor/Microsoft/OneNote',
    'MicrosoftSafetyScanner': 'Protection/SafetyScanner',
    'MicrosoftStickyNotes': 'Editor/Microsoft/StickyNotes',
    'MicrosoftTeams': 'Messaging/Teams',
    'MicrosoftToDo': 'Editor/Microsoft/ToDo',
    'MidnightCommander': 'FileManager/MidnightCommander',
    'MiniTimelineCollection': 'Triage/MiniTimeline',
    'MultiCommander': 'FileManager/MultiCommander',
    'NETCLRUsageLogs': 'SystemFile/NETCLRUsage',
    'NGINXLogs': 'Web/Server/Nginx',
    'NZBGet': 'FileTransfer/NZBGet',
    'Nessus': 'Protection/Nessus',
    'NetMonitorforEmployeesProfessional': 'RMM/ManageEngine',
    'NewsbinPro': 'Reader/NewsbinPro',
    'Newsleecher': 'Reader/Newsleecher',
    'Nicotine__': 'FileTransfer/Nicotine+',
    'Notepad__': 'Editor/Notepad++',
    'Notepad': 'Editor/Notepad',
    'Notion': 'Editor/Notion',
    'OfficeAutosave': 'UserFile/Office/Autosave',
    'OfficeDiagnostics': 'SystemFile/Office/Diagnostics',
    'OfficeDocumentCache': 'UserFile/Office/Cache',
    'OneCommander': 'FileManager/OneCommander',
    'OneDrive_Metadata': 'FileTransfer/OneDrive/Metadata',
    'OneDrive_UserFiles': 'UserFile/OneDrive',
    'OpenSSHClient': 'RMM/OpenSSH/Client',
    'OpenSSHServer': 'RMM/OpenSSH/Server',
    'OpenVPNClient': 'VPN/OpenVPN',
    'Opera': 'Web/Browser/Opera',
    'OutlookPSTOST': 'Messaging/Outlook',
    'P2PClients': 'FileTransfer/*',
    'PeaZip': 'Archiver/PeaZip',
    'PerfLogs': 'SystemFile/PerfLogs',
    'PowerShell7Config': 'UserFile/PowerShell',
    'PowerShellConsole': 'UserFile/PowerShell',
    'PowerShellTranscripts': 'UserFile/PowerShell',
    'Prefetch': 'SystemFile/Prefetch',
    'ProgramData': 'SystemFile/ProgramData',
    'ProtonVPN': 'VPN/ProtonVPN',
    'PuffinSecureBrowser': 'Web/Browser/Puffin',
    'PushNotification': 'SystemFile/NotificationsDB',
    'Q_Dir': 'FileManager/QDir',
    'QFinderPro__QNAP_': 'RMM/QFinderPro',
    'QlikSense': 'Analytics/QlikSense',
    'RDPCache': 'RMM/RDP',
    'RDPJumplist': 'RMM/RDP',
    'RDPLogs': 'RMM/RDP',
    'Radmin': 'RMM/Radmin',
    'RcloneConf': 'FileTransfer/Rclone',
    'RecentFileCache': 'UserFile/RecentFileCache',
    'RecycleBin': 'UserFile/RecycleBin',
    'RecycleBin_DataFiles': 'UserFile/RecycleBin',
    'RecycleBin_InfoFiles': 'UserFile/RecycleBin',
    'RegistryHives': 'SystemFile/RegistryHives',
    'RegistryHivesMSIXApps': 'SystemFile/RegistryHives',
    'RegistryHivesOther': 'SystemFile/RegistryHives',
    'RegistryHivesSystem': 'SystemFile/RegistryHives',
    'RegistryHivesUser': 'SystemFile/RegistryHives',
    'RemoteAdmin': 'RMM/*',
    'RemoteUtilities_app': 'RMM/*',
    'RoamingProfile': 'UserFile/RoamingProfile',
    'Robo_FTP': 'FileTransfer/Robo_FTP',
    'RogueKiller': 'Protection/RogueKiller',
    'RustDesk': 'RMM/RustDesk',
    'SABnbzd': 'Reader/SABnbzd',
    'SCCMClientLogs': 'SystemFile/SCCMClient',
    'SDB': 'SystemFile/SDB',
    'SOFELK': 'Triage/SOFELK',
    'SQLiteDatabases': 'Database/SQLite',
    'SRUM': 'SystemFile/SRUM',
    'SUM': 'SystemFile/SUM',
    'SUPERAntiSpyware': 'Protection/SUPERAntiSpyware',
    'SUSELinuxEnterpriseServer': 'WSL/SUSE_LES',
    'ScheduledTasks': 'SystemFile/ScheduledTasks',
    'ScreenConnect': 'RMM/ScreenConnect',
    'SecureAge': 'Protection/SecureAge',
    'SentinelOne': 'Protection/SentinelOne',
    'ServerTriage': 'Triage/Server',
    'ShareX': 'Screenshot/ShareX',
    'Shareaza': 'FileTransfer/Shareaza',
    'SiemensTIA': 'ICS/SiemensTIA',
    'Signal': 'Messaging/Signal',
    'SignatureCatalog': 'SystemFile/SignatureCatalog',
    'Skype': 'Messaging/Skype',
    'Slack': 'Messaging/Slack',
    'Snagit': 'Screenshot/Snagit',
    'SnipAndSketch': 'Screenshot/SnipAndSketch',
    'Sophos': 'Protection/Sophos',
    'Soulseek': 'FileTransfer/Soulseek',
    'SpeedCommander': 'FileManager/SpeedCommander',
    'Splashtop': 'RMM/Splashtop',
    'StartupFolders': 'SystemFile/StartupFolders',
    'StartupInfo': 'SystemFile/StartupInfo',
    'Steam': 'Gaming/Steam',
    'SublimeText': 'Editor/SublimeText',
    'SugarSync': 'FileTransfer/SugarSync',
    'SumatraPDF': 'Reader/SumatraPDF',
    'SupremoRemoteDesktop': 'RMM/SupremoRemoteDesktop',
    'Symantec_AV_Logs': 'Protection/Symantec',
    'Syscache': 'SystemFile/Syscache',
    'TablacusExplorer': 'FileManager/TablacusExplorer',
    'TeamViewerLogs': 'RMM/TeamViewer',
    'Telegram': 'Messaging/Telegram',
    'TeraCopy': 'FileTransfer/TeraCopy',
    'ThumbCache': 'SystemFile/ThumbCache',
    'Thunderbird': 'Messaging/Thunderbird',
    'TorrentClients': 'FileTransfer/*',
    'Torrents': 'UserFile/Torrents',
    'TotalAV': 'Protection/TotalAV',
    'TotalCommander': 'FileManager/TotalCommander',
    'TreeSize': 'FileManager/TreeSize',
    'TrendMicro': 'Protection/TrendMicro',
    'UEMS': 'RMM/ManageEngine',
    'USBDetective': 'Protection/USBDetective',
    'USBDevicesLogs': 'SystemFile/USBDevices',
    'Ubuntu': 'WSL/Ubuntu',
    'Ultraviewer': 'RMM/Ultraviewer',
    'Usenet': 'FileTransfer/Usenet',
    'UsenetClients': 'FileTransfer/*',
    'UsersFolders': 'UserFile/*',
    'VIPRE': 'Protection/VIPRE',
    'VLC_Media_Player': 'Reader/VLC',
    'VMware': 'Virtualization/VMware/*',
    'VMwareInventory': 'Virtualization/VMware/Inventory',
    'VMwareMemory': 'Virtualization/VMware/Memory',
    'VNCLogs': 'RMM/VNC',
    'Viber': 'Messaging/Viber',
    'VirtualBox': 'Virtualization/VirtualBox/*',
    'VirtualBoxConfig': 'Virtualization/VirtualBox/Config',
    'VirtualBoxLogs': 'Virtualization/VirtualBox/Logs',
    'VirtualBoxMemory': 'Virtualization/VirtualBox/Memory',
    'VirtualDisks': 'Virtualization/*/VirtualDisks',
    'VisualStudioCode': 'Editor/Microsoft/VSCode',
    'Vivaldi': 'Web/Browser/Vivaldi',
    'WBEM': 'SystemFile/WBEM',
    'WER': 'SystemFile/WER',
    'WSL': 'WSL/*',
    'WebBrowsers': 'Web/Browser/*',
    'WebServers': 'Web/Server/*',
    'Webroot': 'Protection/Webroot',
    'WhatsApp': 'Messaging/WhatsApp',
    'WhatsApp_Media': 'UserFile/WhatsApp',
    'WinDefendDetectionHist': 'Protection/Defender',
    'WinSCP': 'FileTransfer/WinSCP',
    'WindowsCopilotRecall': 'SystemFile/Recall',
    'WindowsDefender': 'Protection/Defender',
    'WindowsFirewall': 'Protection/WindowsFirewall',
    'WindowsHello': 'SystemFile/Hello',
    'WindowsIndexSearch': 'SystemFile/IndexSearch',
    'WindowsNetwork': 'SystemFile/Network',
    'WindowsNotificationsDB': 'SystemFile/NotificationsDB',
    'WindowsOSUpgradeArtifacts': 'SystemFile/Update',
    'WindowsPowerDiagnostics': 'SystemFile/Diagnostics',
    'WindowsServerDNSAndDHCP': 'SystemFile/DNSAndDHCP',
    'WindowsSubsystemforAndroid': 'WSA',
    'WindowsTelemetryDiagnosticsLegacy': 'SystemFile/Diagnostics',
    'WindowsTimeline': 'SystemFile/Timeline',
    'WindowsUpdate': 'SystemFile/Update',
    'WindowsYourPhone': 'SystemFile/YourPhone',
    'XPRestorePoints': 'Backup/XPRestorePoints',
    'XYplorer': 'FileManager/XYplorer',
    'Xeox': 'RMM/Xeox',
    'Yandex': 'Web/Browser/Yandex',
    'ZohoAssist': 'RMM/ZohoAssist',
    'Zoom': 'Messaging/Zoom',
    'iTunesBackup': 'Backup/iTunes',
    'mIRC': 'Messaging/mIRC',
    'mRemoteNG': 'RMM/mRemoteNG',
    'openSUSE': 'WSL/openSUSE',
    'pCloudDatabase': 'FileTransfer/pCloud',
    'qBittorrent': 'FileTransfer/qBittorrent',
    'uTorrent': 'FileTransfer/uTorrent',
}
EXTRA_RULES = (
    {
        'Name': 'IIS Temporary ASP Files',
        'Category': 'UserFile/IIS',
        'Glob': 'Windows\\Microsoft.NET\\Framework*\\v*\\Temporary ASP.NET Files\\**10',
        'Accessor': 'ntfs',
        'Comment': 'Highly dependent on the configuration',
    },
    {
        'Name': 'IIS ASP Files',
        'Category': 'UserFile/IIS',
        'Glob': 'inetpub\\wwwroot\\**10',
        'Accessor': 'ntfs',
        'Comment': 'Highly dependent on the configuration',
    },
    {
        'Name': 'Exchange ASP Files',
        'Category': 'SystemFile/Exchange',
        'Glob': 'Program Files\\Microsoft\\Exchange Server\\V15\\FrontEnd\\HttpProxy\\owa\\auth\\**10',
        'Accessor': 'ntfs',
        'Comment': 'Highly dependent on the configuration',
    },
)


CACHE_FILE = Path('/tmp/targets.yaml')
SOURCE_URL = 'https://raw.githubusercontent.com/Velocidex/velociraptor/master/artifacts/definitions/Windows/KapeFiles/Targets.yaml'
RULES_FILE = Path('windows.rules.csv')
TARGETS_FILE = Path('windows.targets.csv')


def _fetch_upstream_data():
    if not CACHE_FILE.is_file():
        with urlopen(SOURCE_URL) as resp:
            CACHE_FILE.write_bytes(resp.read())
    return safe_load(CACHE_FILE.read_bytes())


def _load_rules_and_targets(data):
    kape_rules = None
    kape_targets = None
    for parameter in data['parameters']:
        if parameter['name'] == 'KapeRules':
            kape_rules = list(DictReader(StringIO(parameter['default'])))
        if parameter['name'] == 'KapeTargets':
            kape_targets = list(DictReader(StringIO(parameter['default'])))
    assert kape_rules, "failed to fetch kape rules"
    assert kape_targets, "failed to fetch kape targets"
    return kape_rules, kape_targets


def _populate_datasets(
    kape_rules,
    kape_targets,
    windows_rules,
    windows_targets,
):
    # add valid kape rules
    for kape_rule in kape_rules:
        if None in kape_rule.values():
            continue
        kape_rule['Id'] = int(kape_rule['Id'])
        windows_rules.append(kape_rule)
    # add extra rules
    for extra_rule in EXTRA_RULES:
        next_id = len(windows_rules)
        category = extra_rule['Category']
        injected_rule = {'Id': next_id}
        injected_rule.update(extra_rule)
        windows_rules.append(injected_rule)
        windows_targets[category].add(next_id)
    # remap kape targets
    for kape_target in kape_targets:
        group = TARGETS_MAPPING[kape_target['Group']]
        if group is None:
            continue
        parts = group.split('/')
        rule_ids = set(loads(kape_target['RuleIds']))
        for k in range(1, len(parts)):
            if parts[k - 1] == '*':
                continue
            key = '/'.join(parts[:k] + ['*'])
            windows_targets[key].update(rule_ids)
        windows_targets[group].update(rule_ids)


def _write_csv(filepath, fieldnames, rows):
    with filepath.open('w', encoding='utf-8', newline='') as fobj:
        writer = DictWriter(fobj, fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    data = _fetch_upstream_data()
    kape_rules, kape_targets = _load_rules_and_targets(data)
    windows_rules = []
    windows_targets = defaultdict(set)
    _populate_datasets(
        kape_rules,
        kape_targets,
        windows_rules,
        windows_targets,
    )
    _write_csv(
        RULES_FILE,
        ['Id', 'Name', 'Category', 'Glob', 'Accessor', 'Comment'],
        sorted(windows_rules, key=itemgetter('Id')),
    )
    _write_csv(
        TARGETS_FILE,
        ['Group', 'RuleIds'],
        sorted(
            [
                {'Group': group, 'RuleIds': list(sorted(rule_ids))}
                for group, rule_ids in windows_targets.items()
            ],
            key=itemgetter('Group'),
        ),
    )


if __name__ == '__main__':
    main()
