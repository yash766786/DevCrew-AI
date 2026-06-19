# import asyncio
# import app.websocket.manager as ws_manager

# def emit_event(session_id: str, event: str, message: str):
#     print(f"EMIT => {session_id} {event} {message}")

#     if ws_manager.main_loop is None:
#         print("No main loop available")
#         return

#     asyncio.run_coroutine_threadsafe(
#         ws_manager.manager.send(session_id, {
#             "event": event,
#             "message": message,
#         }),
#         ws_manager.main_loop,
#     )

import asyncio
import app.websocket.manager as ws_manager

def emit_event(
    session_id: str,
    event: str,
    status: str,
    message: str
):
    print(
        f"EMIT => {session_id} | {event} | {status}"
    )

    if ws_manager.main_loop is None:
        print("No main loop available")
        return

    asyncio.run_coroutine_threadsafe(
        ws_manager.manager.send(
            session_id,
            {
                "event": event,
                "status": status,
                "message": message,
            },
        ),
        ws_manager.main_loop,
    )