from flask import current_app, request
import traceback


def register_signaling(socketio):
    """Register simple call signaling events on the provided SocketIO server.

    This module keeps signaling modular and only relays messages between
    connected clients. It expects clients to provide a 'to' field with the
    target socket id or user id depending on your application mapping.
    """

    # Mapa en memoria: usuario_id -> socket sid
    user_sockets = {}

    @socketio.on('connect')
    def _on_connect():
        print('Signaling: cliente conectado', request.sid if 'request' in globals() else '')

    @socketio.on('register_user')
    def on_register_user(data):
        try:
            usuario_id = data.get('usuario_id')
            if not usuario_id:
                return
            user_sockets[str(usuario_id)] = request.sid
            print(f'Registrado usuario {usuario_id} -> sid {request.sid}')
        except Exception as e:
            print('Error en on_register_user:', e)
            traceback.print_exc()

    @socketio.on('disconnect')
    def _on_disconnect():
        # limpiar cualquier mapeo que apunte a esta sid
        sid = request.sid
        keys_to_remove = [k for k, v in user_sockets.items() if v == sid]
        for k in keys_to_remove:
            del user_sockets[k]
            print(f'Usuario {k} desconectado; limpiado mapping')

    @socketio.on('call_request')
    def on_call_request(data):
        try:
            # data: { to: <socketId or userId>, from: <socketId or userId>, ... }
            to = data.get('to')
            if not to:
                return
            # if target is a known usuario_id, map to sid
            target_sid = None
            if str(to) in user_sockets:
                target_sid = user_sockets[str(to)]

            if target_sid:
                socketio.emit('call_request', data, to=target_sid)
            else:
                # fallback: try emitting to 'to' as sid directly
                try:
                    socketio.emit('call_request', data, to=to)
                except TypeError:
                    socketio.emit('call_request', data)
        except Exception as e:
            print('Error en on_call_request:', e)
            traceback.print_exc()

    @socketio.on('call_response')
    def on_call_response(data):
        try:
            to = data.get('to')
            if not to:
                return
            target_sid = user_sockets.get(str(to))
            if target_sid:
                socketio.emit('call_response', data, to=target_sid)
            else:
                try:
                    socketio.emit('call_response', data, to=to)
                except TypeError:
                    socketio.emit('call_response', data)
        except Exception as e:
            print('Error en on_call_response:', e)
            traceback.print_exc()

    @socketio.on('webrtc_offer')
    def on_webrtc_offer(data):
        try:
            to = data.get('to')
            if not to:
                return
            target_sid = user_sockets.get(str(to))
            if target_sid:
                socketio.emit('webrtc_offer', data, to=target_sid)
            else:
                try:
                    socketio.emit('webrtc_offer', data, to=to)
                except TypeError:
                    socketio.emit('webrtc_offer', data)
        except Exception as e:
            print('Error en on_webrtc_offer:', e)
            traceback.print_exc()

    @socketio.on('webrtc_answer')
    def on_webrtc_answer(data):
        try:
            to = data.get('to')
            if not to:
                return
            target_sid = user_sockets.get(str(to))
            if target_sid:
                socketio.emit('webrtc_answer', data, to=target_sid)
            else:
                try:
                    socketio.emit('webrtc_answer', data, to=to)
                except TypeError:
                    socketio.emit('webrtc_answer', data)
        except Exception as e:
            print('Error en on_webrtc_answer:', e)
            traceback.print_exc()

    @socketio.on('webrtc_ice_candidate')
    def on_webrtc_ice(data):
        try:
            to = data.get('to')
            if not to:
                return
            target_sid = user_sockets.get(str(to))
            if target_sid:
                socketio.emit('webrtc_ice_candidate', data, to=target_sid)
            else:
                try:
                    socketio.emit('webrtc_ice_candidate', data, to=to)
                except TypeError:
                    socketio.emit('webrtc_ice_candidate', data)
        except Exception as e:
            print('Error en on_webrtc_ice:', e)
            traceback.print_exc()
