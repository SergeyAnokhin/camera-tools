# from Pipeline import ShotsGroup


# # 0. Preload
# yoloData = YoloPreloader()

# # 1. Get from source
# source = XXXXShotsProvider()
# shots = source.GetShots();

# # 2. Create Pipeline
# pipeline = ShotsPipeline()
# pipeline.shots = shots

# # 3. Add Processors
# # proceccor : Analyse() GetJsonResult() Draw()  
# diff = DiffContoursProcessor()
# pipeline.processors.append(diff)

# magnify = MagnifyProcessor(diff)
# pipeline.processor.append(magnify)

# yolo = YoloObjDetectionProcessor(yoloData)
# pipeline.processors.append(yolo)

# tracking = TrackingProcessor(diff, yolo)
# pipeline.processors.append(tracking)

# pipeline.Process()
# pipeline.Show()

# elastic = ElasticPostProcessor()
# pipeline.postprocessor.append(elastic) 

# imageArchiver = ImageArchiverPostProcssor()
# pipeline.postprocessor.append(imageArchiver) 

# pipeline.PostProcess()