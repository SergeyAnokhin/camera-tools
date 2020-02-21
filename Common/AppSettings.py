from django.conf import settings

class GmailSettings:
    USERNAME = getattr(settings, "GMAIL_USERNAME", None)
    PASSWORD = getattr(settings, "GMAIL_PASSWORD", None)

class DnsAdGuardSettings:
    API_QUERY_LOG  = getattr(settings, "DNS_ADGUARD_API_QUERY_LOG", "")
    API_AUTH       = getattr(settings, "DNS_ADGUARD_API_AUTH", "")

class AppSettings:
    USED_SETTINGS              = getattr(settings, "USED_SETTINGS", None)

    # Secret
    IMAGE_ID_DECODE_KEY        = getattr(settings, "IMAGE_ID_DECODE_KEY", None)
    HOST                       = getattr(settings, "HOST", None)
    ELASTICSEARCH_HOST         = getattr(settings, "ELASTICSEARCH_HOST", None)
    GMAIL                      = GmailSettings()

    CAMERA_LIVE_PATH           = getattr(settings, "CAMERA_LIVE_PATH", None)
    CAMERA_ARCHIVE_PATH        = getattr(settings, "CAMERA_ARCHIVE_PATH", None)
    CAMERA_ARCHIVE_NAS_PATH    = getattr(settings, "CAMERA_ARCHIVE_NAS_PATH", None)
    HASSIO_PATH                = getattr(settings, "HASSIO_PATH", None)
    DNS_HOST                   = getattr(settings, "DNS_HOST", None)
    SOURCE_IMAGE_PATTARN       = getattr(settings, "SOURCE_IMAGE_PATTARN", None)

    DNS_ADGUARD                = DnsAdGuardSettings()

    def __init__(self):
        print("AppSettings init. User Settings: " + getattr(settings, "USED_SETTINGS", None)) 

    # def GetNetworkName(self):
    #     print(f'/// Platform: {sys.platform + " ":/<61}')
    #     interface_output = os.environ.get("host_net_interfaces")
    #     if interface_output:
    #         interface_output = interface_output.lower()
    #     if 'ethernet' in interface_output and 'connecte' in interface_output:
    #         return 'ethernet'
    #     host_wifi_name = os.environ.get("host_wifi_name")
    #     if host_wifi_name:
    #         return host_wifi_name.lower().strip()
    #     return 'offline'

    # def GetNetworkConfig(self):
    #     computername = os.environ["COMPUTERNAME"].lower()
    #     if not CommonHelper.network:
    #         CommonHelper.network = self.GetNetworkName()
    #         print(f'/// Current network: {CommonHelper.network + " ":/<54}')
    #         print(f'/// Computer name:   {computername + " ":/<54}')
    #     platform = sys.platform
    #     if not CommonHelper.networkConfig:
    #         CommonHelper.networkConfig = self.secretConfig.GetNetworkConfig(self.network, computername, platform)
    #         if not CommonHelper.networkConfig:
    #             print(f"ERROR: network config not found for : {self.network} / {computername} / {platform}")

    #         elasticsearch = CommonHelper.networkConfig['elasticsearch']
    #         if elasticsearch:
    #             (elasticsearch_host, elasticsearch_port) = elasticsearch.split(':')
    #             print(f'/// Elasticsearch connection: http://{elasticsearch_host + ":" + elasticsearch_port + " ":/<38}')
    #         else:
    #             print(f'/// Elasticsearch connection: {" NONE ":/^45}')
    #         print(f'/// Network config name: {CommonHelper.networkConfig["name"] + " ":/<50}')
    #     return CommonHelper.networkConfig

