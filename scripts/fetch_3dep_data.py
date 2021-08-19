import pdal
import json
from app_logger import App_Logger
from file_handler import FileHandler

class Fetch3depData:

    def __init__(self, public_data_url = "https://s3-us-west-2.amazonaws.com/usgs-lidar-public/", pipeline_json_path="./get_data.json") -> None:
        self.logger = App_Logger().get_logger(__name__)
        self.public_data_url = public_data_url
        self.file_handler = FileHandler()
        self.pipeline_json = self.file_handler.read_json(pipeline_json_path)

    def get_pipeline(self, region: str, output_filename: str = "temp"):
        BOUND = "([-10425171.94, -10423171.94], [5164494.71, 5166494.71])"

        full_dataset_path = f"{self.public_data_url}{region}/ept.json"

        self.pipeline_json['pipeline'][0]['filename'] = full_dataset_path
        self.pipeline_json['pipeline'][0]['bounds'] = BOUND
        self.pipeline_json['pipeline'][3]['filename'] = "../data/laz/" + output_filename + ".laz"
        self.pipeline_json['pipeline'][4]['filename'] = "../data/tif/" + output_filename + ".tif"

        pipeline = pdal.Pipeline(json.dumps(self.pipeline_json))

        return pipeline

    def run_pipeline(self, region: str = "IA_FullState"):
        pipeline = self.get_pipeline(region)

        try:
            pipeline.execute()
            metadata = pipeline.metadata
            log = pipeline.log
            self.logger.info(f'Pipeline executed successfully.')
            print(log)
            return pipeline
        except RuntimeError as e:
            self.logger.exception('Pipeline execution failed')
            print(e)

if(__name__ == '__main__'):
    data_fetcher = Fetch3depData()
    data_fetcher.run_pipeline()