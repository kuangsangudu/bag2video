from bag2video import Bag2video
import os
import pyrealsense2 as rs
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="a method to convert realsense bag file to [image|video] data")
    # Add argument which takes path to a bag file as an input
    parser.add_argument("-i", "--input", type=str, help="Path to the bag file", required=True)
    parser.add_argument("-o", "--output", type=str, help="Path to the output file. e.g c:data/images for images"
                                                         "c:/data/output.mp4 for video", required=True)
    parser.add_argument("-s", "--stream", type=str, help="the stream you want to process", default="color")
    parser.add_argument("-f", "--format", type=str, help="The format corresponding to the data stream",
                        default="rgb8")
    parser.add_argument("--fps", type=int, help="bag file frame fps", default=30)
    parser.add_argument("--width", type=int, help="the output video width, only when you want to output video",
                        default=1280)
    parser.add_argument("--height", type=int, help="the output video height, only when you want to output video",
                        default=720)
    # Parse the command line arguments to an object
    args = parser.parse_args()

    # Check if the given file have bag extension
    if os.path.splitext(args.input)[1] != ".bag":
        print("The given file is not of correct file format.")
        print("Only .bag files are accepted")
        exit()

    args.stream = args.stream.lower()
    args.format = args.format.lower()
    try:
        args.format = getattr(rs.format, args.format)
    except Exception as e:
        print("You put the wrong format")
        exit()

    if args.stream == "color":
        is_color = True
        args.stream = getattr(rs.stream, "color")
    elif args.stream == "rgbd":
        is_color = True
        args.stream = getattr(rs.stream, "depth")
    else:
        is_color = False
        try:
            args.stream = getattr(rs.stream, args.stream)
        except Exception as e:
            print("You put the wrong stream")
            exit()

    if os.path.isdir(args.output):
        Bag2video(args.input).bag2image(args.output, args.stream, args.format, args.fps, is_color=is_color)
    else:
        Bag2video(args.input).bag2video(args.output, args.stream, args.format, args.fps, (args.width, args.height),
                                        is_color=is_color)

