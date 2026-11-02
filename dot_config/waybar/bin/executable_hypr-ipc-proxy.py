#!/usr/bin/env python3
import os
import sys
import re
import socket
import select
import signal
import threading

def get_real_hypr_dir():
    xdg = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if not sig or sig == "waybar_proxy":
        hypr_base = os.path.join(xdg, "hypr")
        if os.path.isdir(hypr_base):
            dirs = [d for d in os.listdir(hypr_base) if d != "waybar_proxy" and os.path.isdir(os.path.join(hypr_base, d))]
            if dirs:
                dirs.sort(key=lambda d: os.path.getmtime(os.path.join(hypr_base, d)), reverse=True)
                sig = dirs[0]
    if not sig or sig == "waybar_proxy":
        raise RuntimeError("Could not find active Hyprland instance signature")
    return os.path.join(xdg, "hypr", sig)

def translate_single(cmd_str):
    cmd_str = cmd_str.strip()
    m = re.match(r'^(?:dispatch\s+)?(?:workspace|focusworkspaceoncurrentmonitor)\s+(.+)$', cmd_str)
    if m:
        target = m.group(1).strip()
        if target.startswith('name:'):
            name = target[5:]
            return f'dispatch hl.dsp.focus({{ workspace = "{name}" }})'
        elif target.startswith('e+') or target.startswith('e-'):
            return f'dispatch hl.dsp.focus({{ workspace = "{target}" }})'
        elif target.isdigit() or (target.startswith('-') and target[1:].isdigit()):
            return f'dispatch hl.dsp.focus({{ workspace = {target} }})'
        else:
            return f'dispatch hl.dsp.focus({{ workspace = "{target}" }})'

    m_special = re.match(r'^(?:dispatch\s+)?togglespecialworkspace(?:\s+(.+))?$', cmd_str)
    if m_special:
        sp = m_special.group(1) or 'magic'
        return f'dispatch hl.dsp.workspace.toggle_special("{sp.strip()}")'

    return cmd_str

def translate(cmd_str):
    if cmd_str.startswith('[[BATCH]]'):
        parts = cmd_str[len('[[BATCH]]'):].split(';')
        translated_parts = [translate_single(p) for p in parts]
        return '[[BATCH]]' + ';'.join(translated_parts)
    return translate_single(cmd_str)

def handle_client(client_sock, real_sock_path):
    try:
        data = b""
        while True:
            chunk = client_sock.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(chunk) < 4096:
                break

        if not data:
            client_sock.close()
            return

        cmd_str = data.decode('utf-8', errors='ignore')
        translated_cmd = translate(cmd_str)

        real_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        real_sock.connect(real_sock_path)
        real_sock.sendall(translated_cmd.encode('utf-8'))

        while True:
            resp = real_sock.recv(4096)
            if not resp:
                break
            client_sock.sendall(resp)

        real_sock.close()
    except Exception:
        pass
    finally:
        client_sock.close()

def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError:
        sys.exit(1)
    os.setsid()
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError:
        sys.exit(1)

def main():
    if "--daemon" in sys.argv:
        daemonize()

    xdg = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    proxy_dir = os.path.join(xdg, "hypr", "waybar_proxy")
    os.makedirs(proxy_dir, exist_ok=True)

    proxy_sock_path = os.path.join(proxy_dir, ".socket.sock")
    proxy_sock2_path = os.path.join(proxy_dir, ".socket2.sock")

    real_dir = get_real_hypr_dir()
    real_sock_path = os.path.join(real_dir, ".socket.sock")
    real_sock2_path = os.path.join(real_dir, ".socket2.sock")

    if os.path.islink(proxy_sock2_path) or os.path.exists(proxy_sock2_path):
        os.remove(proxy_sock2_path)
    os.symlink(real_sock2_path, proxy_sock2_path)

    if os.path.exists(proxy_sock_path):
        os.remove(proxy_sock_path)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(proxy_sock_path)
    server.listen(64)

    def cleanup(signum, frame):
        try:
            server.close()
            if os.path.exists(proxy_sock_path):
                os.remove(proxy_sock_path)
            if os.path.islink(proxy_sock2_path):
                os.remove(proxy_sock2_path)
        except:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    while True:
        try:
            client_sock, _ = server.accept()
            if not os.path.exists(real_sock_path):
                real_dir = get_real_hypr_dir()
                real_sock_path = os.path.join(real_dir, ".socket.sock")
                real_sock2_path = os.path.join(real_dir, ".socket2.sock")
                if os.path.islink(proxy_sock2_path) or os.path.exists(proxy_sock2_path):
                    os.remove(proxy_sock2_path)
                os.symlink(real_sock2_path, proxy_sock2_path)

            t = threading.Thread(target=handle_client, args=(client_sock, real_sock_path), daemon=True)
            t.start()
        except KeyboardInterrupt:
            break
        except Exception:
            pass

if __name__ == "__main__":
    main()
