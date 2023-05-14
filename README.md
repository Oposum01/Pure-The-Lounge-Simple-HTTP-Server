# Pure "The Lounge" Simple HTTP Server

## Introduction
This project (documentation) tries to replace Pure's "Lounge" / "The Lounge" for Pure Siesta Flow (applies to other Pure Radios like Evoke etc. too) with a self hosted simple python HTTP server solution running on a Raspberry Pi (or any other Linux).
As of 9th of May 2023 Pure shut down their web portal for those Wi-Fi capable radios, which means they'll lose any internet radio funtionality.
I was able to capture most of the traffic (luckily plain HTTP/1.1) between my Siesta Flow and their server, before this date and did some reverse engineering.
Sure, you are still able to use the built-in "Mediaplayer"/upnp function, streaming mp3s or even m3us (incl. Internet radio streams) as a workaround for the missing "TheLounge" portal.
Though my main motivation for this project was to continue using "TheLounge" for the alarm clock. The Siesta Flow has a limitation here, where it can use only DAB+, FM or "TheLounge" as a source for the alarms, but not the "Mediaplayer".


## Status
2023/05/09: I am stuck with the key (pure:CredentialObject) - the radio expects an answer with a correct key, where I do not know the method to obtain that for.
Disassambling with Ghidra was not possible, due to the weird Frontier Silicon Chorus 2 (FS1020G-F) platform and it's nearly unkown architecture. The core is a META122 CPU with extensive DSP capabilities ("RISC 32-bit with DaOpPaMe template extensions to 64-bit").
Running "strings" on the "conwy.app.elf" file unveiled some stuff like "ilibblowfish.c", a "ImaginationKLkey" and a "xlogin.c" reference where most of the XML stuff is constructed in.
Looking at the internal pictures of the FCC certification (https://fccid.io/X280055/Internal-Photos/Internal-photos-1387479), there does not seem to be something like UART or serial to access the Linux (busybox) which is running on the system.
A unpopulated JTAG header could be spotted though, but that doesn't help.
A portscan with nmap showed no open ports for TCP and UDP (1-65535).

## Procedure of the Siesta Flow to play a internet radio stream

Phase I:
Connect to Wi-Fi, acquire DHCP lease.
DNS resolve "radio.thelounge.com"
Contact "radio.thelounge.com" for authentication, time and firmware status (?)
 - first packet: "action=X_login", pure:CredentialObject (128 chars), "pure:MAC" (mac address of the radio), "pure:PV" (unknown, what this is for)
 - the radio expects a "X_LoginReponse" with a 64 char long key as response in <pure:Reponse>
 - second packet: "action=X_login", "pure:CredentialObject" (140 chars), "pure:MAC" (mac address of the radio), "pure:PV" (unknown, what this is for)
 - ...
 
Phase II:
DNS resolve "p.flowlive.com"
Contact "p.flowlive.com" to retrieve a m3u playlist

Phase III:
Access the URL from the m3u and play the audio stream


## Requirements:
- redirect these two DNS-entries, using your local DNS (router):
 - "radio.thelounge.com" to your local Raspberry Pi ip address
 - "p.flowlive.com" to your local Raspberry Pi ip address
 - replace radio url in python script (default: "Hochschulradio Aachen") with the one you'd like to listen to
- Raspberry Pi where you execute the python3 script: "sudo python3 pure-server.py"

## Files:
"Siesta-Flow-after-coldboot-play-lounge.pcap": wireshark packet capture of the Siesta Flow talking to radio.thelounge.com and p.flowlive.com when the servers where still active
"conwy.app.elf": extracted elf-file from "_conwy_2.53.1.65.008.dfu.extracted/squashfs-root/bin" (Siesta Flow v5.1 firmware) using "binwalk"

## Addendum:

Redirect DNS entries on a LANCOM router:
```
cd /Setup/DNS/DNS-List
add p.flowlive.com 0 192.168.0.123
add radio.thelounge.com 0 192.168.0.123
```

Example of m3u from p.flowlive.com request ("GET /r/27/84/8427.m3u HTTP/1.1\r\n"):

```
#EXTM3U
#EXT-IMG-INF:IS-PLAYLIST=TRUE,StreamFormat=SHOUTCAST/SHOUTCAST,AudioFormat=MP3,Bitrate=128
http://evans.hochschulradio.rwth-aachen.de:8000/hoeren/high.m3u

```

I would like to give some credits to "FW Hacking": https://fwhacking.blogspot.com/search/label/siesta%20flow