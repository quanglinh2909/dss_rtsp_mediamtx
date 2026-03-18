import subprocess
import time
import threading

from app.config.settings import settings
from app.constants.camera_enum import StatusCameraEnum
from app.constants.event_socket import EventSocket
from app.services.login_dahua_service import login_dahua_service
from app.websocket.ConnectionManager import connection_websocket_manager


class RTSPProcess:
    def __init__(self, id_camera):
        self.is_running = True
        self.time_current = time.time()
        self.process = None
        self.current_status = StatusCameraEnum.UNKNOWN
        self.id_camera = id_camera

    def start_rtsp_process(self, rtsp_url, output_url):
        # Use the more robust ffmpeg invocation requested by the user.
        # Keep args as a list so subprocess avoids shell interpretation issues.
        command = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-fflags", "nobuffer+discardcorrupt",
            "-flags", "low_delay",
            "-max_delay", "0",
            "-reorder_queue_size", "0",
            "-i", rtsp_url,

            "-map", "0:v",
            "-map", "0:a?",

            "-c:v", "copy",
            "-c:a", "copy",

            "-f", "rtsp",
            "-rtsp_transport", "tcp",
            "-rtsp_flags", "listen",
            output_url,
        ]

        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def set_status(self, status):
        if status != self.current_status:
            print("Status changed to {}".format(status))
            from app.services.camera_service import camera_service
            camera_service.update(self.id_camera, status=status)
            connection_websocket_manager.send_message_json_sync(EventSocket.UPDATE_CAMERA_STATUS, {
                "camera_id": self.id_camera,
                "status": status,
            })
        self.current_status = status

    def check_process(self):
        while self.is_running:
            if time.time() - self.time_current > 10:
                print("RTSP connection error detected. Restarting FFmpeg...")
                if self.process is not None:
                    self.process.kill()
                    self.process = None
                    self.time_current = time.time()

            time.sleep(1)

    def stop(self):
        self.is_running = False
        print("Stopping RTSP process...")
        if self.process is not None:
            self.process.kill()

    def monitor_process(self, channel_id, output_url):

        threading.Thread(target=self.check_process, daemon=True).start()

        while self.is_running:
            print(self.process, output_url)
            if self.process is None or self.process.poll() is not None:
                print("FFmpeg process exited, restarting...")
                self.set_status(StatusCameraEnum.RESTARTING)
                rtsp_url = login_dahua_service.get_rtsp(channel_id)
                if rtsp_url is None:
                    time.sleep(1)
                    continue
                
                if settings.DAHUA_IP_REPLACE is not None or settings.DAHUA_PORT_REPLACE is not None:
                    from urllib.parse import urlparse, urlunparse
                    parsed = urlparse(rtsp_url)
                    hostname = settings.DAHUA_IP_REPLACE if settings.DAHUA_IP_REPLACE is not None else parsed.hostname
                    port = settings.DAHUA_PORT_REPLACE if settings.DAHUA_PORT_REPLACE is not None else parsed.port
                    
                    netloc = ""
                    if parsed.username:
                        netloc += f"{parsed.username}"
                        if parsed.password:
                            netloc += f":{parsed.password}"
                        netloc += "@"
                    netloc += f"{hostname}"
                    if port:
                        netloc += f":{port}"
                        
                    parsed = parsed._replace(netloc=netloc)
                    rtsp_url = urlunparse(parsed)

                print("Starting FFmpeg with RTSP URL: {}".format(rtsp_url))
                #rtsp://192.168.105.15:9100/mediaServer/monitor/param/cameraid=1000000%240%26substream=1?token=18
                # relace ip and port
                self.process = self.start_rtsp_process(rtsp_url, output_url)

            if self.process.stderr:
                for line in iter(self.process.stderr.readline, ''):
                    if "size=N/A" in line.strip():
                        self.time_current = time.time()
                        self.set_status(StatusCameraEnum.ONLINE)
                        # print("RTSP connection is OK")

            time.sleep(5)  # Kiểm tra trạng thái sau mỗi 5 giây


class ManagerPublicCamera:
    def __init__(self):
        self.list_camera = {}
        self.list_output_url = {}

    def get_list_camera(self):
        return self.list_camera

    def add_camera(self, id_camera, channel_id, id_camera_vms):

        output_url = f"rtsp://{settings.IP_MEDIA_MTX}:{settings.PORT_MEDIA_MTX}/live/liveStream_{id_camera_vms}_0_0"
        print(output_url)
        self.delete_camera(id_camera)

        rtsp_process = RTSPProcess(id_camera=id_camera)
        threading.Thread(target=rtsp_process.monitor_process, args=(channel_id,output_url,), daemon=True).start()
        self.list_camera[id_camera] = rtsp_process
        self.list_output_url[id_camera] = output_url

    def delete_camera(self, id_camera):
        from app.services.camera_service import camera_service
        id_camera = str(id_camera)
        if id_camera in self.list_camera:
            camera_service.update(id_camera, status=StatusCameraEnum.OFFLINE)
            self.list_camera[id_camera].stop()
            del self.list_camera[id_camera]
            del self.list_output_url[id_camera]

    def delete_all_camera(self):
        print("Deleting all cameras...", self.list_camera)
        # Create a copy of the keys to avoid modifying dictionary during iteration
        camera_ids = list(self.list_camera.keys())
        for id_camera in camera_ids:
            self.delete_camera(id_camera)


manager_public_camera = ManagerPublicCamera()
