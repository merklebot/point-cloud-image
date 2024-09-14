import cv2
import depthai as dai
import numpy as np
from flask import Flask, send_file
import threading
import io

app = Flask(__name__)

# Global variable to store the latest frame
latest_frame = None

def create_pipeline():
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define source and output
    camRgb = pipeline.create(dai.node.ColorCamera)
    xoutRgb = pipeline.create(dai.node.XLinkOut)

    xoutRgb.setStreamName("rgb")

    # Properties
    camRgb.setPreviewSize(416, 416)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

    # Linking
    camRgb.preview.link(xoutRgb.input)

    return pipeline

def capture_frames():
    global latest_frame

    # Connect to device and start pipeline
    with dai.Device(create_pipeline()) as device:
        # Output queue will be used to get the rgb frames from the output defined above
        qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            inRgb = qRgb.get()  # blocking call, will wait until a new data has arrived
            frame = inRgb.getCvFrame()
            
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            latest_frame = buffer.tobytes()

@app.route('/get_frame')
def get_frame():
    if latest_frame is not None:
        return send_file(
            io.BytesIO(latest_frame),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='frame.jpg'
        )
    else:
        return "No frame available", 404

if __name__ == '__main__':
    # Start frame capture in a separate thread
    threading.Thread(target=capture_frames, daemon=True).start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5002)