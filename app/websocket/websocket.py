
from fastapi import APIRouter, Query
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from app.websocket.ConnectionManager import connection_websocket_manager

router = APIRouter()



@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket
):

    await connection_websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # {"add_event": "status_relay_device"}
            # {"remove_event": "status_relay_device"}
            if "add_event" in data:
                event = data["add_event"]
                await connection_websocket_manager.add_listen_event(websocket, event)
            elif "remove_event" in data:
                event = data["remove_event"]
                await connection_websocket_manager.remove_listen_event(websocket, event)

            print("Received data:", data)
            # Xử lý các action khác nếu cần
    except WebSocketDisconnect:
        await connection_websocket_manager.disconnect(websocket)

