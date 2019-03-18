from Pipeline.ShotsPipeline import ShotsPipeline
from Pipeline.ImapShotsProvider import ImapShotsProvider
from Pipeline.DirectoryShotsProvider import DirectoryShotsProvider
from Processors.DiffContoursProcessor import DiffContoursProcessor
# from Pipeline import ShotsGroup

temp = 'temp'
imap_folder = 'camera/foscam'

# # 0. Preload
# yoloData = YoloPreloader()

# # 1. Get from source
imap = ImapShotsProvider(temp)
shotsImap = imap.GetShots(imap_folder);

# directory = DirectoryShotsProvider()
# shotsDir = directory.GetShots(shotsImap)

# # 2. Create Pipeline
pipeline = ShotsPipeline()
pipeline.shots = [shotsImap[:]] # , shotsDir[:]

# # 3. Add Processors
# # proceccor : Analyse() GetJsonResult() Draw()  
diff = DiffContoursProcessor()
pipeline.processors.append(diff)

# magnify = MagnifyProcessor(diff)
# pipeline.processor.append(magnify)

# yolo = YoloObjDetectionProcessor(yoloData)
# pipeline.processors.append(yolo)

# tracking = TrackingProcessor(diff, yolo)
# pipeline.processors.append(tracking)

pipeline.PreLoad()
pipeline.Process()
pipeline.Show()

# elastic = ElasticPostProcessor()
# pipeline.postprocessor.append(elastic) 

# mailSender = MailSenderPostProcessor()
# pipeline.postprocessor.append(elastic) 

# imageArchiver = ImageArchiverPostProcssor()
# pipeline.postprocessor.append(imageArchiver) 

# pipeline.PostProcess()