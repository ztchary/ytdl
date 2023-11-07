import socket
import time
import os
import threading
port = 8085

def e404(conn):
  conn.send(b"HTTP/1.1 404 Not Found\r\n\r\nnot here pal")
  conn.close()

def sendfile(conn, file):
  with open(file, "rb") as f:
    content = f.read()
    conn.send(b"HTTP/1.1 200 OK\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: "+str(len(content)).encode()+b"\r\n\r\n"+content)
    conn.close()

def hint(conn):
  conn.send(b"HTTP/1.1 103 Early Hint\r\n\r\n")

def ytdl(conn, path):
  path = path[1:]
  if os.path.exists(path):
    return sendfile(conn, path)
  url = "https://youtube.com/watch?v="+path[9:-4]
  if path[-4:] == ".mp4":
    cmd = f"yt-dlp -S res,ext:mp4:m4a --recode mp4 -o \"{path[:-4]}\" "
  elif path[-4:] == ".mp3":
    cmd = f"yt-dlp -x --audio-format mp3 -o \"{path[:-4]}\" "
  else:
    conn.send(b"HTTP/1.1 400 Bad Request\r\n\r\nInvalid file format")
    return conn.close()
  os.system(cmd + url)
  while not os.path.exists(path):
    try:
      hint(conn)
    except:
      return
    time.sleep(1)
  sendfile(conn, path)

def serverLoop(server):
  conn, _ = server.accept()
  path = conn.recv(4096).split(b" ",2)[1].decode()
  if path == "/":
    conn.send(b"HTTP/1.1 302 Found\r\nLocation: https://www.dogwater53.us/posts/ytdl\r\n\r\n")
    return conn.close()
  if path == "/bookmark":
    return sendfile(conn, "bookmark.js")
  if path.startswith("/download/"):
    return threading.Thread(target=ytdl,args=[conn,path]).start()
  e404(conn)

if __name__ == "__main__":
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind(("0.0.0.0", port))
  server.listen(10)
  while True:
    try:
      serverLoop(server)
    except:
      pass
  print("Stopping server")
