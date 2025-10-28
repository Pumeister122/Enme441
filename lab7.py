import socket
import RPi.GPIO as GPIO
import time

# =========================
#  GPIO + PWM SETUP
# =========================
led_pins = [5, 6, 26]      # BCM pin numbers for the 3 LEDs
freq = 1000                # PWM frequency (Hz)
brightness = [0, 0, 0]     # store current brightness % for each LED
pwms = []

GPIO.setmode(GPIO.BCM)
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, freq)
    pwm.start(0)
    pwms.append(pwm)


# =========================
#  BRIGHTNESS CONTROL
# =========================
def change_brightness(index, value):
    """Clamp and set LED brightness."""
    try:
        val = int(value)
    except:
        val = 0
    val = max(0, min(100, val))
    brightness[index] = val
    pwms[index].ChangeDutyCycle(val)


# =========================
#  POST DATA PARSER
# =========================
def parsePOSTdata(data):
    """Extract key:value pairs from POST body."""
    try:
        data = data.decode('utf-8')
    except:
        data = str(data)
    body_start = data.find('\r\n\r\n') + 4
    body = data[body_start:]
    pairs = body.split('&')
    result = {}
    for p in pairs:
        if '=' in p:
            k, v = p.split('=', 1)
            result[k] = v
    return result


# =========================
#  HTML PAGE BUILDER
# =========================
def html_page(active_led=0, slider_val=None):
    if slider_val is None:
        slider_val = levels[active_led]
    chk0 = "checked" if active_led == 0 else ""
    chk1 = "checked" if active_led == 1 else ""
    chk2 = "checked" if active_led == 2 else ""

    html = """\
<html>
<head>
  <title>LED Brightness</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="font-family: Georgia, 'Times New Roman', Times, serif; margin:.75rem;">
  <form method="POST" action="/">
    <fieldset style="border:1px solid #888; border-radius:6px; padding:.8rem 1rem; width:340px;">
      <div style="font-size:18px; margin-bottom:6px;">Brightness level:</div>
      <input type="range" name="brightness" min="0" max="100" value="{slider}"
             style="display:block; width:100%; margin-bottom:14px;">

      <div style="font-size:18px; margin:10px 0 6px;">Select LED:</div>

      <div style="margin:4px 0;">
        <label>
          <input type="radio" name="led" value="0" {chk0}>
          LED 1 ({l0}%)
        </label>
      </div>
      <div style="margin:4px 0;">
        <label>
          <input type="radio" name="led" value="1" {chk1}>
          LED 2 ({l1}%)
        </label>
      </div>
      <div style="margin:4px 0;">
        <label>
          <input type="radio" name="led" value="2" {chk2}>
          LED 3 ({l2}%)
        </label>
      </div>

      <button type="submit"
              style="display:block; margin-top:14px; padding:.45rem .75rem; border:1px solid #666; border-radius:6px; background:#eee;">
        Change Brightness
      </button>
    </fieldset>
  </form>
</body>
</html>
""".format(
        chk0=chk0, chk1=chk1, chk2=chk2,
        slider=slider_val,
        l0=levels[0], l1=levels[1], l2=levels[2]
    )
    return html.encode("utf-8")

    return bytes(html, "utf-8")


# =========================
#  WEB SERVER LOOP
# =========================
def serve_web_page():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))  # use 80 if running with sudo
    s.listen(1)
    print("Server running — visit http://raspberrypi.local:80")

    while True:
        print("Waiting for connection...")
        conn, addr = s.accept()
        print(f"Connection from {addr}")
        request = conn.recv(1024)

        selected_led = 0  # default LED

        if b"POST" in request:
            post_data = parsePOSTdata(request)
            if "led" in post_data and "brightness" in post_data:
                try:
                    led_index = int(post_data["led"])
                    selected_led = led_index
                    value = int(post_data["brightness"])
                    change_brightness(led_index, value)
                except Exception as e:
                    print("Error parsing POST:", e)

        # Send HTTP response
        conn.send(b"HTTP/1.1 200 OK\r\n")
        conn.send(b"Content-Type: text/html\r\n")
        conn.send(b"Connection: close\r\n\r\n")
        try:
            conn.sendall(web_page(selected_led))
        finally:
            conn.close()


# =========================
#  MAIN
# =========================
try:
    serve_web_page()
except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    for p in pwms:
        p.stop()
    GPIO.cleanup()


