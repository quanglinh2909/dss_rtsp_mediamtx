from urllib.parse import quote


def get_rtsp(rtsp, user_name, password):
    password = quote(password)
    start_rtsp = f"rtsp://{user_name}:{password}@"
    if start_rtsp in rtsp:
        return rtsp
    return rtsp.replace("rtsp://", start_rtsp)

def get_rtsp_not_encode(rtsp, user_name, password):
    start_rtsp = f"rtsp://{user_name}:{password}@"
    if start_rtsp in rtsp:
        return rtsp
    return rtsp.replace("rtsp://", start_rtsp)
