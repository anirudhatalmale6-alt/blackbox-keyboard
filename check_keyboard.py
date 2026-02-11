#!/usr/bin/env python3
"""Check if the on-screen keyboard exists in Firefox"""
import socket, json, time, sys

sys.path.insert(0, '/opt/theblackbox')

def send_cmd(s, msg_id, method, params=None):
    if params is None:
        params = {}
    cmd = json.dumps([0, msg_id, method, params])
    msg = str(len(cmd)) + ":" + cmd
    s.send(msg.encode())
    time.sleep(1)
    data = b""
    while True:
        try:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
            # Try to parse - if we have complete message, break
            try:
                text = data.decode()
                colon = text.index(":")
                length = int(text[:colon])
                payload = text[colon+1:colon+1+length]
                json.loads(payload)
                break
            except:
                continue
        except socket.timeout:
            break
    return data.decode()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)

try:
    s.connect(('localhost', 2828))
    data = s.recv(4096)
    print("1. Connected to Marionette")

    # New session
    resp = send_cmd(s, 1, "WebDriver:NewSession")
    print("2. Session started")

    # Check main page URL
    resp = send_cmd(s, 2, "WebDriver:GetCurrentURL")
    print("3. Current URL:", resp[:200])

    # Check if iframe exists and keyboard is in it
    js_check = """
    var result = [];
    var iframe = document.getElementById('tbbx-challenge-frame');
    result.push('Iframe: ' + (iframe ? 'YES' : 'NO'));
    if (iframe) {
        result.push('Iframe src: ' + iframe.src);
        try {
            var doc = iframe.contentDocument;
            result.push('Can access iframe doc: YES');
            var osk = doc.getElementById('osk-overlay');
            result.push('Keyboard div: ' + (osk ? 'FOUND display=' + osk.style.display : 'NOT FOUND'));
            var inputs = doc.querySelectorAll('input[type=text],input[type=password]');
            result.push('Input fields: ' + inputs.length);
            var scripts = doc.querySelectorAll('script');
            result.push('Script tags: ' + scripts.length);
            var lastScript = scripts[scripts.length-1];
            if (lastScript) result.push('Last script has osk: ' + (lastScript.textContent.indexOf('osk-overlay') > -1));
        } catch(e) {
            result.push('Cannot access iframe doc: ' + e.message);
        }
    }
    return result.join('\\n');
    """
    resp = send_cmd(s, 3, "WebDriver:ExecuteScript", {"script": js_check})
    print("4. Check result:")
    # Parse the response to get the value
    try:
        colon = resp.index(":")
        payload = json.loads(resp[colon+1:])
        if isinstance(payload, list) and len(payload) > 3:
            print(payload[3].get("value", payload[3]))
        else:
            print(resp[:300])
    except:
        print(resp[:300])

    # End session
    send_cmd(s, 4, "WebDriver:DeleteSession")
    s.close()
    print("5. Done")
except Exception as e:
    print("Error:", e)
