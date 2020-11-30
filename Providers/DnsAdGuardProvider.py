import json, datetime, requests, re, pytz, sys
from dns import reversename, resolver
from django.core.serializers.json import DjangoJSONEncoder
from Providers.Provider import Provider
from Common.AppSettings import AppSettings

class DnsAdGuardProvider(Provider):

    def __init__(self, isSimulation=False):
        super().__init__("DNS", isSimulation)
        self.pattern_id = re.compile("\d+\.\d+\.\d+\.(\d+)")
        resolver.default_resolver = resolver.Resolver(configure=False)
        resolver.default_resolver.nameservers = [AppSettings.DNS_HOST]
        self.encoder = DjangoJSONEncoder()
        self.pattern6OrMoreDigits = re.compile("\.(\d{6})\d+") # .123456789 => .(123456)789
        self.patterFloat = re.compile("(\d+\.\d+)") # 12.3456789


    def GetProtected(self, data) -> []:
        if AppSettings.DNS_ADGUARD.API_QUERY_LOG.startswith("http"):
            url = f"{AppSettings.DNS_ADGUARD.API_QUERY_LOG}"

            headers = {
                'Authorization': AppSettings.DNS_ADGUARD.API_AUTH,
                'User-Agent': "PostmanRuntime/7.20.1",
                'Accept': "*/*",
                'Cache-Control': "no-cache",
                'Accept-Encoding': "gzip, deflate",
                'Connection': "keep-alive",
                'cache-control': "no-cache"
                }

            response = requests.request("GET", url, headers=headers)
            re_json = response.json()
        else:
            self.log.debug(f'Read data from file: 💾 {AppSettings.DNS_ADGUARD.API_QUERY_LOG}')
            with open(AppSettings.DNS_ADGUARD.API_QUERY_LOG) as json_file:
                re_json = json.load(json_file)            

        data = re_json['data']
        oldestMinutes = self.OldestDateTimeMinutes(re_json['oldest'])
        if oldestMinutes > 20:
            self.log.debug(f'Oldest (minutes): {oldestMinutes:.2f} (⏱️ {re_json["oldest"]})')
        else:
            self.log.error(f'Oldest (minutes): {oldestMinutes:.2f} (⏱️ {re_json["oldest"]})')
        self.log.debug(f"Data (items) : {len(data)}")

        return data

    def PostProcess(self, i, context: dict):
        try:
            match = self.pattern_id.search(i["client"])
            if match:
                i["client_id"] = int(match.group(1))
            i["client_ip"] = i["client"]

            # DNS reverse lookup
            rev_name = reversename.from_address(i["client_ip"])
            try:
                if not self.isSimulation:
                    answer = resolver.query(rev_name,"PTR", lifetime=60, raise_on_no_answer=False) # 
                    i["client"] = answer[0].target.labels[0].decode("utf-8") 
            except resolver.NXDOMAIN as err:
                self.log.warning(f"Cant resolve IP: 📶 {i['client_ip']}. {err}")
            except IndexError as err:
                self.log.warning(f"Cant resolve IP: 📶 {i['client_ip']}. {err}")
            
            if 'answer' in i:
                for item in i['answer']:
                    if not isinstance(item['value'], str): # simplify complex answer SRV
                        item['value'] = str(item['value']['Target']).strip('.')

            dt = self.ParseDateTime(i["time"])
            del(i["time"])
            dt = dt.astimezone(pytz.utc)
            dtStr = self.encoder.encode(dt).strip('"')
            i["@timestamp"] = dtStr
            i["tags"] = ["camera_tools"]
            i["elapsedMs"] = round(float(i["elapsedMs"]), 2)
            i['_index'] = f"dns-{dt:%Y.%m}"
            i['_id'] = f'{i["client"]}@{dtStr}_{i["question"]["host"]}'

        except:
            print("⚠ Unexpected error:", sys.exc_info()[0])
            self.log.debug("Source: " + json.dumps(i, indent=4))
            raise

    def ParseDateTime(self, datetimeStr: str):
        datetimeStr = datetimeStr.replace("Z", "+00:00")
        # 12.354698787984 => 12.354698 # exact 6 digit after "." and 2 before
        #  2.354698787984 => 02.354698
        #  2.354          => 02.354000
        datetimeStr = self.patterFloat.sub(lambda x: '{:0>9.6f}'.format(float(x.group(1))), datetimeStr)
        dt = datetime.datetime.fromisoformat(datetimeStr)
        # dt = dt.replace(tzinfo=None)
        return dt

    def OldestDateTimeMinutes(self, oldestStr: str):
        dt = self.ParseDateTime(oldestStr)
        dt = dt.replace(tzinfo=None)
        now = datetime.datetime.now()
        return (now - dt).total_seconds() / 60
