import smtplib
from os.path import basename
from cryptography.fernet import Fernet
from collections import Counter
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from Common.SecretConfig import SecretConfig
from Processors.Processor import Processor
from Processors.YoloObjDetectionProcessor import YoloObjDetectionProcessor
from Pipeline.Model.PipelineShot import PipelineShot

class MailSenderProcessor(Processor):
    sender: str = 'home.assistant.sergey@gmail.com'
    to: [] = ['home.assistant.sergey@gmail.com', 'anokhin.sergey@gmail.com']

    def __init__(self, isSimulation: bool = False):
        super().__init__("SMTP")
        self.secretConfig = SecretConfig()
        self.secretConfig.fromJsonFile()
        self.isSimulation = isSimulation

    def ProcessShot(self, pShot: PipelineShot, pShots: []):
        pass

    def AfterProcess(self, pShots: [], ctx):
        subject = self.GetSubject(pShots, ctx)

        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender
        msg['To'] = COMMASPACE.join(self.to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        html = """
<html lang="en">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css"> -->
        <style>
html{box-sizing:border-box}*,*:before,*:after{box-sizing:inherit}
/* html{-ms-text-size-adjust:100%;-webkit-text-size-adjust:100%}body{margin:0} */
html,body{font-family:Verdana,sans-serif;font-size:12px;line-height:1.5}html{overflow-x:hidden}
a{background-color:transparent}a:active,a:hover{outline-width:0}
.w3-container,.w3-panel{padding:0.03em 16px}
/* .w3-container:after,.w3-container:before,.w3-panel:after,.w3-panel:before,.w3-row:after,.w3-row:before,.w3-row-padding:after,.w3-row-padding:before, */

.w3-light-grey,.w3-hover-light-grey:hover,.w3-light-gray,.w3-hover-light-gray:hover{color:#000!important;background-color:#f1f1f1!important}
/* .w3-round-small{border-radius:2px} */
.w3-round,.w3-round-medium{border-radius:4px}
/* .w3-round-large{border-radius:8px}
.w3-round-xlarge{border-radius:16px}
.w3-round-xxlarge{border-radius:32px} */
/* .w3-cell-row:before,.w3-cell-row:after,.w3-clear:after,.w3-clear:before,.w3-bar:before,.w3-bar:after{content:"";display:table;clear:both} */
/* .w3-panel{margin-top:16px;margin-bottom:16px} */
.w3-blue,.w3-hover-blue:hover{color:#fff!important;background-color:#2196F3!important}
.w3-table,.w3-table-all{border-collapse:collapse;border-spacing:0;width:100%;display:table;margin-bottom: 4px}
/* .w3-table-all{border:1px solid #ccc} */
.w3-table td,.w3-table th,.w3-table-all td,.w3-table-all th{padding:1px 4px;display:table-cell;text-align:left;vertical-align:top}
.w3-table th:first-child,.w3-table td:first-child,.w3-table-all th:first-child,.w3-table-all td:first-child{padding-left:5px;}
/* .w3-border-0{border:0!important} */
.w3-border{border:1px solid #ccc!important;}
/* .w3-border-top{border-top:1px solid #ccc!important}
.w3-border-bottom{border-bottom:1px solid #ccc!important}
.w3-border-left{border-left:1px solid #ccc!important}
.w3-border-right{border-right:1px solid #ccc!important} */
/* .w3-bordered tr,.w3-table-all tr{border-bottom:1px solid #ddd}.w3-striped tbody tr:nth-child(even){background-color:#f1f1f1} */
/* .w3-table-all tr:nth-child(odd){background-color:#fff}.w3-table-all tr:nth-child(even){background-color:#f1f1f1} */
/* .w3-hoverable tbody tr:hover,.w3-ul.w3-hoverable li:hover{background-color:#ccc}.w3-centered tr th,.w3-centered tr td{text-align:center} */
.w3-card,.w3-card-2{box-shadow:0 2px 5px 0 rgba(0,0,0,0.16),0 2px 10px 0 rgba(0,0,0,0.12)}
.w3-pink,.w3-hover-pink:hover{color:#fff!important;background-color:#e91e63!important}
.w3-light-green,.w3-hover-light-green:hover{color:#000!important;background-color:#8bc34a!important}
.w3-green,.w3-hover-green:hover{color:#fff!important;background-color:#4CAF50!important}
.nowrap{white-space: nowrap;overflow: hidden;text-overflow: ellipsis;}
.nowrap:hover{overflow: visible;}
/* .w3-card-4,.w3-hover-shadow:hover{box-shadow:0 4px 10px 0 rgba(0,0,0,0.2),0 4px 20px 0 rgba(0,0,0,0.19)} */
        </style>
    </head>
    <body>
   <!-- 🚶‍ # &#128540; # &#x1F6B6; -->
    <div class="w3-container">    
        """
        html += self.MapToEmoji(self.GetYoloLabels(ctx))

        for pShot in pShots or []:
            f = pShot.Shot.fullname

            dt = pShot.Shot.GetDatetime()
            idSource = pShot.Shot.GetId(self.config.camera)
            #self.log.debug(f'Encode: {idSource}')
            id = self.helper.Encode(idSource)

            html += f"""
            {self.GetBodyHtml(pShot)}
            <img src="http://{self.secretConfig.camera_tools_host}/image?id={id}"><br>
            | <a target="_blank" href="http://{self.secretConfig.camera_tools_host}/image?id={id}&original=1">Original</a> |
            <br>
            """

            # html += f"""
            # {self.GetBodyHtml(pShot)}
            # <img src="cid:{pShot.Shot.filename}"><br>
            # """

        html += "</div></body></html>"
        # part1 = MIMEText(body, 'plain')
        #msg.attach(part1)
        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        meta0 = self.CreateMetadata(pShots[0])
        self.log.debug(f"- Send mail: '{subject}' to {self.to}")
        if not self.isSimulation:
            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.starttls()
            smtp.login(self.secretConfig.gmail_username, self.secretConfig.gmail_password)
            smtp.sendmail(self.sender, self.to, msg.as_string())
            smtp.quit() 
            smtp.close()
        else:
            meta0['html'] = html
            meta0['id'] = idSource

        meta0["Subject"] = subject
        meta0["MessageSize"] = len(msg.as_string())
        return pShots

    def GetSubject(self, pShots: [], ctx):
        dt = pShots[0].Shot.GetDatetime()
        camera = self.config.camera
        subject = f"{camera} @{dt:%H:%M:%S} "
        return subject + self.GetYoloLabels(ctx) + f' ({dt:%d.%m.%Y})'

    def GetYoloLabels(self, ctx):
        return ctx["YOLO"]["labels"] if "YOLO" in ctx and "labels" in ctx["YOLO"] else ""

    mapDict = {
        "question": "&#x2754;",
        "person": "&#x1F6B9;",
        "handbug": "&#x1F4BC;",
        "car": "&#x1F697;",
        "suitcase": "&#x1F9F3;",
        "fire hydrant": "&#x1F9EF;",
        "skateboard": "&#x1F6F9;",
        "dog": "&#x1F415;",
        "bear": "&#x1F43B;",
        "bird": "&#x1F426;",
    }

    def MapToEmojiOrEmpty(self, label: str):
        if label in self.mapDict:
            return self.mapDict[label]
        else:
            return ""

    def MapToEmoji(self, label: str):

        for old, new in self.mapDict.items():
            label = label.replace(old, new)
        return label
        #return mapDict[label] if label in mapDict else label
        
    def GetBodyText(self, pShots: []):
        body = ""
        for shot in pShots:
            body += f'#{shot.Index}: {shot.OriginalShot.filename} \n'
            if 'YOLO' in shot.Metadata and 'areas' in shot.Metadata['YOLO']:
                yolo = shot.Metadata['YOLO']['areas']
                for item in yolo:
                    body += f'- YOLO: {item["label"]} ({item["confidence"]}) prof: {item["size"][0]}x{item["size"][1]} = {item["profile_proportion"]} @{item["center_coordinate"][0]}x{item["center_coordinate"][1]}\n'
            if 'DIFF' in shot.Metadata:
                diff = shot.Metadata['DIFF']
                body += f'- DIFF: {diff["Diff"]["TotalArea"]}\n'
                if "boxes" in diff:
                    for item in diff["boxes"]:
                        body += f'  - BOX {item["area"]} prof: {item["profile_proportion"]} @{item["center"][0]}x{item["center"][1]}\n'
            if 'TRAC' in shot.Metadata:
                trac = shot.Metadata['TRAC']
                for key in trac:
                    body += f'- TRAC angle {trac[key]["angle"]} distance {trac[key]["distance"]} \n'
        return body

    def GetBodyHtml(self, shot):
        body = '<table class="w3-table w3-border w3-card-2">'
        body += f"""<tr class="w3-light-grey">
                <td>#{shot.Index}: {shot.OriginalShot.filename}</td>
                <td style="width: 100px;"></td>
            </tr>\n"""
        if 'YOLO' in shot.Metadata and 'areas' in shot.Metadata['YOLO']:
            yolo = shot.Metadata['YOLO']['areas']
            for item in yolo:
                body += self.GetLine(f'&#x1F9E0; YOLO: {self.MapToEmojiOrEmpty(item["label"])} {item["label"]} ({item["confidence"]}) prof: {item["size"][0]}x{item["size"][1]} = {item["profile_proportion"]} @{item["center_coordinate"][0]}x{item["center_coordinate"][1]}',
                                item["confidence"]*100, 'w3-blue')
        if 'DIFF' in shot.Metadata:
            diff = shot.Metadata['DIFF']
            body += self.GetLine(f'&#x1F53A; DIFF: {diff["Diff"]["TotalArea"]}', diff["Diff"]["TotalArea"] / 2.5e2, 'w3-green')
            if "boxes" in diff:
                for item in diff["boxes"]:
                    body += self.GetLine(f'&nbsp;- &#x1F532; BOX {item["area"]} prof: {item["profile_proportion"]} @{item["center"][0]}x{item["center"][1]}<br>\n',
                                item["area"] / 2.5e2, 'w3-light-green')
        if 'TRAC' in shot.Metadata:
            trac = shot.Metadata['TRAC']
            for key in trac:
                body += self.GetLine(f'&#x1F9ED; TRAC angle {trac[key]["angle"]} distance {trac[key]["distance"]}',
                    (trac[key]["angle"] + 180) / 360 * 100, 'w3-pink')
        body += '</table>'
        return body

    def GetLine(self, text, percent, style='w3-blue'):
        percent = percent if percent <= 100 else 100
        percent_int = round(percent)
        return f"""    <tr>
                <td>{text}</td>
                <td style="width: 100px;">
                        <div class="w3-light-grey w3-round">
                            <div class="w3-container {style} w3-round nowrap" style="width:{percent_int}px">{percent:.2f}%</div>
                        </div>
                    </td>
                </tr>
                """