import os, sys, struct, urllib2, time, ssl

idbe_url = "https://idbe-wup.cdn.nintendo.net/icondata/10/{}{}.idbe"

IV = "A46987AE47D82BB4FA8ABC0450285FA4" # Init Vector (for AES-128-CBC)

K0 = "4AB9A40E146975A84BB1B4F3ECEFC47B" # aes_keys[0]
K1 = "90A0BB1E0E864AE87D13A6A03D28C9B8" # aes_keys[1]
K2 = "FFBB57C14E98EC6975B384FCF40786B5" # aes_keys[2]
K3 = "80923799B41F36A6A75FB8B48C95F66F" # aes_keys[3]

AES_KEYS = [K0, K1, K2, K3]

# Begin of our program #

argc = len(sys.argv)

if(argc < 2):
	print("[WARNING] Usage: idbe_decrypt.py TITLE_ID <optional: VERSION>")
	time.sleep(5)
	sys.exit()

title_id = sys.argv[1]
tid_len = len(title_id)

if(tid_len == 17 or tid_len == 16):
	title_id = title_id.replace("-", "") # In the case of: "00050000-13374269" like title id
else:
	print("[WARNING] Invalid Title ID")
	time.sleep(5)
	sys.exit()

version = None

if(argc >= 3):
	version = sys.argv[2]
	idbe_url = idbe_url.format(title_id, "-"+version) # Need a specific version icon
else:
	idbe_url = idbe_url.format(title_id, "")			   # Need last version


# ### Downlaod game icon ### #

ssl._create_default_https_context = ssl._create_unverified_context # Patch "SSL_CreateDefaultContext" so we can connect to N servers as they don't have any ssl cert

try:
	urllib2.urlopen(idbe_url)
except Exception as e:
	print("")
	print("[WARNING] Invalid Title ID or Nintendo Server is blocking the connection.")
	print("[WARNING] Contact me (NexoCube) if it happens again. Exiting in 5 seconds...")
	time.sleep(5)
	sys.exit()

print("")

ret = urllib2.urlopen(idbe_url)
idbe_buf = ret.read()

print("""  _____ _____  ____  ______    _____                             _            
 |_   _|  __ \|  _ \|  ____|  |  __ \                           | |           
   | | | |  | | |_) | |__     | |  | | ___  ___ _ __ _   _ _ __ | |_ ___ _ __ 
   | | | |  | |  _ <|  __|    | |  | |/ _ \/ __| '__| | | | '_ \| __/ _ \ '__|
  _| |_| |__| | |_) | |____   | |__| |  __/ (__| |  | |_| | |_) | ||  __/ |   
 |_____|_____/|____/|______|  |_____/ \___|\___|_|   \__, | .__/ \__\___|_|   
                                                      __/ | |                 
                                                     |___/|_|  """)

print("")
print ("					by NexoCube")

print("")
print("")
print("[INFO] Successfully downloaded encrypted image from: \n{}".format(idbe_url))
print("")

f = open("file_temp.idbe", "wb")
f.write(idbe_buf[2:len(idbe_buf)])
f.close()

# ### File is downloaded now and placed in idbe_buf ### #

def read8(buf, index):
	return struct.unpack("=b", buf[index])[0]

def read16(buf, index):
	return struct.unpack("=h", buf[index:index+2:1])[0]

def read32(buf, index):
	return struct.unpack("=i", buf[index:index+4:1])[0]

def read_hex_from_string(buf, size):
	temp_buf = ""
	for i in range(0,size):
		new_value = hex(ord(buf[i])).replace("0x", "")
		if new_value == "0":
			new_value = "00"
		temp_buf += new_value

	return temp_buf

def utf16_to_8(buf, size):
	utf8_buf = ""
	for i in range(0, size/2):
		if buf[i*2:(i*2)+2] == "\x00\x00":
			return utf8_buf
		utf8_buf += buf[(i*2)+1:(i*2)+2]

	return utf8_buf

print("[INFO] Starting decryption ... (AES-128-CBC)")

time.sleep(1.5)

key_index = read8(idbe_buf, 0x01)

print("[INFO] AES_KEYS index: {}".format(key_index))

cmd_line_buf = "openssl enc -d -aes-128-cbc -K \"{}\" -iv \"{}\" -in file_temp.idbe -out {}.tga -md md5 -nopad"
cmd_line_buf = cmd_line_buf.format(AES_KEYS[key_index], IV, title_id)

os.system(cmd_line_buf)
os.remove("file_temp.idbe")

f = open(title_id+".tga", "r+b")
tga_buf = f.read()

file_hash = read_hex_from_string(tga_buf, 32)
game_name = utf16_to_8(tga_buf[0x250:0x290], 200)
publisher = utf16_to_8(tga_buf[0x1D0:0x220], 200)


print("")
print("[INFO] SHA256: " + file_hash)
print("[INFO] Game name:      {}".format(game_name))
print("[INFO] Game publisher: {}".format(publisher))

print("")

f.seek(0)
f.write(tga_buf[0x2050:len(tga_buf)])
f.close()


print("[INFO] Done! File decrypted at: {}.tga".format(title_id))

