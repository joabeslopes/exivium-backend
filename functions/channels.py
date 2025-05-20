def get_channel(channel: int = None):
    all_channels = {
        1: "rtsp://localhost:8554/mystream"
    }
    if channel is None:
        return all_channels
    return all_channels.get(channel)