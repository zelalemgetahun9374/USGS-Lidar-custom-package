import numpy as np
import pdal
import json
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point

from app_logger import App_Logger
from file_handler import FileHandler

class LidarProcessor:
    """
    This class contains functons useful for fetching, manipulating, and visualizing LIDAR point cloud data.
    """

    def __init__(self, public_data_url: str = "https://s3-us-west-2.amazonaws.com/usgs-lidar-public/", pipeline_json_path: str="../assets/get_data.json") -> None:
        """
        This method is used to instantiate the class.

        Args:
            public_data_url (str, optional): [the url where the dataset can be accessed from]. Defaults to "https://s3-us-west-2.amazonaws.com/usgs-lidar-public/".
            pipeline_json_path (str, optional): [the json file describing the pipeline structure]. Defaults to "../assets/get_data.json".
        """
        self.logger = App_Logger().get_logger(__name__)
        self.file_handler = FileHandler()
        self.pipeline_json = self.file_handler.read_json(pipeline_json_path)
        self.public_data_url = public_data_url
        self.input_epsg = 3857
        self.metadata = self.file_handler.read_csv("../assets/usgs_3dep_metadata.csv")
        values = {"year": 0}
        self.metadata.fillna(value=values, inplace=True)

    def get_polygon_boundaries(self, polygon: Polygon):
        """
        This method returns the bounds and exterior coordinates of a polygon as strings.

        Args:
            polygon (Polygon): [a polygon object]

        Returns:
            [tuple]: [bounds string and polygon exterior coordinates string]
        """
        polygon_df = gpd.GeoDataFrame([polygon], columns=['geometry'])

        polygon_df.set_crs(epsg=self.output_epsg, inplace=True)
        polygon_df['geometry'] = polygon_df['geometry'].to_crs(epsg=self.input_epsg)
        minx, miny, maxx, maxy = polygon_df['geometry'][0].bounds

        polygon_input = 'POLYGON(('
        xcords, ycords = polygon_df['geometry'][0].exterior.coords.xy
        for x, y in zip(list(xcords), list(ycords)):
            polygon_input += f'{x} {y}, '
        polygon_input = polygon_input[:-2]
        polygon_input += '))'

        return f"({[minx, maxx]},{[miny,maxy]})", polygon_input

    def get_pipeline(self, region: str, polygon: Polygon):
        """
        This method fills the empty values in the pipeline dictionary and creates a pdal pipeline object.

        Args:
            region (str): [the filename of the region where the data is extracted from]
            polygon (Polygon): [a polygon object]

        Returns:
            [pdal.Pipeline]: [pdal pipeline object]
        """
        boundaries, polygon_input = self.get_polygon_boundaries(polygon)

        full_dataset_path = f"{self.public_data_url}{region}/ept.json"

        self.pipeline_json['pipeline'][0]['filename'] = full_dataset_path
        self.pipeline_json['pipeline'][0]['bounds'] = boundaries
        self.pipeline_json['pipeline'][1]['polygon'] = polygon_input
        self.pipeline_json['pipeline'][3]['out_srs'] = f'EPSG:{self.output_epsg}'

        pipeline = pdal.Pipeline(json.dumps(self.pipeline_json))

        return pipeline

    def run_pipeline(self, polygon: Polygon, epsg, region: str = "IA_FullState"):
        """
        This method runs a pdal pipeline and fetches data.

        Args:
            polygon (Polygon): [a polygon object]
            epsg (int): [the desired coordinate reference system(CRS)]
            region (str, optional): [the filename of the region where the data is extracted from]. Defaults to "IA_FullState".

        Returns:
            [pdal.Pipeline]: [pdal pipeline object]
        """
        self.output_epsg = epsg
        pipeline = self.get_pipeline(region, polygon)

        try:
            pipeline.execute()
            self.logger.info(f'Pipeline executed successfully.')
            return pipeline
        except RuntimeError as e:
            self.logger.exception('Pipeline execution failed')
            print(e)

    def make_geo_df(self, arr: dict):
        """
        This method creates a geopandas dataframe from a dictionary.

        Args:
            arr (dict): a point cloud data dictionary with X, Y and Z keys.

        Returns:
            [Geopandas.GeoDataFrame]: [a geopandas dataframe]
        """
        geometry_points = [Point(x, y) for x, y in zip(arr["X"], arr["Y"])]
        elevetions = arr["Z"]
        df = gpd.GeoDataFrame(columns=["elevation", "geometry"])
        df['elevation'] = elevetions
        df['geometry'] = geometry_points
        df = df.set_geometry("geometry")
        df.set_crs(self.output_epsg, inplace=True)
        return df

    def get_regions(self, polygon: Polygon, epsg: int) -> list:
        """
        This method fetches all the region filenames that contain the polygon.

        Args:
            polygon (Polygon): [a polygon object]
            epsg (int): [the desired coordinate reference system(CRS)]

        Returns:
            [list]: [list of all the region filenames that contain the polygon]
        """
        self.output_epsg = epsg
        polygon_df = gpd.GeoDataFrame([polygon], columns=['geometry'])

        polygon_df.set_crs(epsg=self.output_epsg, inplace=True)
        polygon_df['geometry'] = polygon_df['geometry'].to_crs(epsg=self.input_epsg)
        minx, miny, maxx, maxy = polygon_df['geometry'][0].bounds

        cond_xmin = self.metadata.xmin <= minx
        cond_xmax = self.metadata.xmax >= maxx
        cond_ymin = self.metadata.ymin <= miny
        cond_ymax = self.metadata.ymax >= maxy

        df = self.metadata[cond_xmin & cond_xmax & cond_ymin & cond_ymax]
        sort_df = df.sort_values(by=['year'])
        regions = sort_df['filename'].to_list()
        return regions

    def get_region_data(self, polygon: Polygon, epsg: int, region: str):
        """
        This method fetches data for a specific region filename.

        Args:
            polygon (Polygon): [a polygon object]
            epsg (int): [the desired coordinate reference system(CRS)]
            region (str): [the filename of the region where the data is extracted from]

        Returns:
            [Geopandas.GeoDataFrame]: [a geopandas dataframe]
        """
        pipeline = self.run_pipeline(polygon, epsg, region)
        arr = pipeline.arrays[0]
        return self.make_geo_df(arr)

    def get_data(self, polygon: Polygon, epsg: int) -> dict:
        """
        This method fetches data from all regions that contain a polygon.

        Args:
            polygon (Polygon): [a polygon object]
            epsg (int): [the desired coordinate reference system(CRS)]

        Returns:
            [dict]: [a dictionary with the years as keys and the respective geodataframes as the
            values for the specified polygon]
        """

        regions = self.get_regions(polygon, epsg)
        region_dict = {}
        for region in regions:
            year = int(self.metadata[self.metadata.filename == region].year.values[0])
            if year == 0:
                year = 'unknown'
            region_df = self.get_region_data(polygon, epsg, region)
            empty = region_df.empty
            if not empty:
                region_dict[year] = region_df

        return region_dict

    def plot_terrain_3d(self, gdf: gpd.GeoDataFrame, fig_size: tuple=(12, 10), size: float=0.01):
        """
        This method displays points in a geodataframe as a 3d scatter plot.

        Args:
            gdf (gpd.GeoDataFrame): [a geopandas dataframe containing points in the geometry column and height in the elevation column.]
            fig_size (tuple, optional): [filesze of the figure to be displayed]. Defaults to (12, 10).
            size (float, optional): [size of the points to be plotted]. Defaults to 0.01.
        """
        fig, ax = plt.subplots(1, 1, figsize=fig_size)
        ax = plt.axes(projection='3d')
        ax.scatter(gdf.geometry.x, gdf.geometry.y, gdf.elevation, s=size)
        plt.show()

    def subsample(self, gdf: gpd.GeoDataFrame, res: int = 3):
        """
        This method subsamples the points in a point cloud data using some resolution.

        Args:
            gdf (gpd.GeoDataFrame): [a geopandas dataframe containing points in the geometry column and height in the elevation column.]
            res (int, optional): [resolution]. Defaults to 3.

        Returns:
            [Geopandas.GeoDataFrame]: [a geopandas dataframe]
        """

        points = np.vstack((gdf.geometry.x, gdf.geometry.y, gdf.elevation)).transpose()

        voxel_size=res

        non_empty_voxel_keys, inverse, nb_pts_per_voxel = np.unique(((points - np.min(points, axis=0)) // voxel_size).astype(int), axis=0, return_inverse=True, return_counts=True)
        idx_pts_vox_sorted=np.argsort(inverse)

        voxel_grid={}
        grid_barycenter=[]
        last_seen=0

        for idx,vox in enumerate(non_empty_voxel_keys):
            voxel_grid[tuple(vox)]= points[idx_pts_vox_sorted[
            last_seen:last_seen+nb_pts_per_voxel[idx]]]
            grid_barycenter.append(np.mean(voxel_grid[tuple(vox)],axis=0))
            last_seen+=nb_pts_per_voxel[idx]

        sub_sampled =  np.array(grid_barycenter)
        df_subsampled = gpd.GeoDataFrame(columns=["elevation", "geometry"])

        geometry = [Point(x, y) for x, y in zip( sub_sampled[:, 0],  sub_sampled[:, 1])]

        df_subsampled['elevation'] = sub_sampled[:, 2]
        df_subsampled['geometry'] = geometry

        return df_subsampled
