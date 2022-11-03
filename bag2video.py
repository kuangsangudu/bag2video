import numpy as np
import pyrealsense2 as rs
import cv2
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Bag2video:
    """
    a simply class to transfor bag file to video or image file.
    address - bag file address
    """
    def __init__(self, address):
        self.__address = address
        self.__allowed = [rs.stream.color, rs.stream.depth, rs.stream.infrared]

    @staticmethod
    def get_idx(i, pre_zero=10):
        first = str(i)
        return (pre_zero - len(first)) * "0" + first

    @staticmethod
    def check_file(path):
        if not os.path.exists(path):
            os.makedirs(path)

    def _bag2trans(self, path, data_stream=rs.stream.color, data_format=rs.format.rgb8, fps=30, pro_type=0, video=None,
                   is_color=True):
        if data_stream not in self.__allowed:
            logger.warning("this function can only process [color|depth|infrared] data stream")
            return

        if pro_type == 0:
            original = path
        else:
            pre_add, video_f = os.path.split(path)
            original = pre_add

        self.check_file(original)

        # Create pipeline
        pipeline = rs.pipeline()
        colorizer = rs.colorizer()
        try:
            # Create a config object
            config = rs.config()

            # Tell config that we will use a recorded device from file to be used by the pipeline through playback.
            rs.config.enable_device_from_file(config, self.__address, repeat_playback=False)

            # Configure the pipeline to stream the data stream
            # Change this parameters according to the recorded bag file resolution
            # config.enable_stream(data_stream, data_format, fps)
            config.enable_all_streams()

            # Start streaming from file
            pipeline.start(config)

            # Skip 5 first frames to give the Auto-Exposure time to adjust
            for x in range(5):
                pipeline.wait_for_frames()

            # Streaming loop
            i = 1

            while True:
                # Get frame set of data stream
                frames = pipeline.wait_for_frames()

                # Get data frame
                if data_stream == rs.stream.color:
                    color_frame = frames.get_color_frame()
                    color_frame_image = np.array(color_frame.get_data())
                    data_frame_image = cv2.cvtColor(color_frame_image, cv2.COLOR_RGB2BGR)
                elif data_stream == rs.stream.depth:
                    if not is_color:
                        depth_frame = frames.get_depth_frame()
                        data_frame_image = np.np.asanyarray(depth_frame.get_data())
                    else:
                        align = rs.align(rs.stream.color)
                        frames = align.process(frames)

                        # Update color and depth frames:
                        aligned_depth_frame = frames.get_depth_frame()
                        data_frame_image = np.asanyarray(colorizer.colorize(aligned_depth_frame).get_data())
                        data_frame_image = cv2.cvtColor(data_frame_image, cv2.COLOR_RGB2BGR)
                else:
                    infrared_frame = frames.get_infrared_frame()
                    data_frame_image = np.array(infrared_frame.get_data())
                if pro_type == 0:
                    n_path = os.path.join(original, self.get_idx(i) + ".jpg")
                    cv2.imwrite(n_path, data_frame_image)
                else:
                    video.write(data_frame_image)
                i += 1
        except RuntimeError:
            pass
        except Exception as e:
            logger.error("%s happened" % e)
        finally:
            try:
                pipeline.stop()
            except:
                pass
            if video:
                video.release()

    def bag2image(self, path, data_stream=rs.stream.color, data_format=rs.format.rgb8, fps=30, is_color=True):
        self._bag2trans(path, data_stream, data_format, fps, video=None, is_color=is_color)

    def bag2video(self, path, data_stream=rs.stream.color, data_format=rs.format.rgb8, fps=30, size=(1280, 720),
                  is_color=True):
        pre_add, video_f = os.path.split(path)
        file_extension = video_f.split(".")[-1]
        self.check_file(pre_add)
        if file_extension == "mp4":
            video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M', 'P', '4', 'V'), fps, size, is_color)
        elif file_extension == "avi":
            video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps, size, is_color)
        else:
            logger.warning("I haven't decided on this part")
            return
        self._bag2trans(path, data_stream, data_format, fps, 1, video, is_color)

    def image2video(self, img_path, video_path, size, fps=30):
        pre_add, video_f = os.path.split(video_path)
        file_extension = video_f.split(".")[-1]
        self.check_file(pre_add)
        if file_extension == "mp4":
            video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc('M', 'P', '4', 'V'), fps, size)
        elif file_extension == "avi":
            video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps, size)
        else:
            logger.warning("I haven't decided on this part")
            return
        file_list = os.listdir(img_path)
        for item in file_list:
            if item.endswith('.jpg'):
                item = os.path.join(img_path, item)
                img = cv2.imread(item)
                video.write(img)
        video.release()
