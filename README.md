# SYSTEM CAPTURE: MONDO EDITION
I am autistic AS FUCK and I need closed captions or I will die. A lot of shows don't have captions. Some Youtube channels dont have captions, and public lobbies in vrchat DEFINITELY don't have captions. After getting the Quest 3, which DOES caption vrchat public lobbies, I am spoiled, and I wanted captions when I am in desktop mode.

Windows 11 comes with a captioner, but it sucks. There's no other free captioner that did what I wanted to, except System Captioner was close.

System Captioner has been edited to do what I want, so I shall share it with you all!

I think there's a bug right now, in particular with the LARGE model where it will freeze after awhile, and it just needs restarted to get back to action. Stay tuned :tm: as we get that fixed.


This is 100% free, does not need to log into any server. There are no limits. It just -works-. Thank god for the OG creator.

-----
But Mondo! What got changed from the OG?

- Config editing added in general, which lets you edit font, font color, background color, opacity, etc. on the fly.
- Config editing added to the GUI!
- Titlebar added with option to turn off.
- Right click to move the window, Left click to copy text.
- AutoScroll on/off added in general & to the GUI on the fly
- Cool oil slick background & Mondo pic in the GUI.
- Reizeable window on the fly.
- Prolly some other stuff.

If you liked this readme, consider the time it took for me to type it out! Feel free to throw a couple bucks at me, it means a lot and will motivate me to write more readmes, FAQs, etc! -> https://mondocat.gumroad.com/coffee

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, LITERACY OR ILLITERACY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Screenshot:
<img width="1919" height="1046" alt="image" src="https://github.com/user-attachments/assets/70e9b0c7-bf1b-4798-9fbf-961b6a00d51d" />

-----

<img width="662" height="662" alt="MondoCat_ColorFixed_2025_Twitch" src="https://github.com/user-attachments/assets/5e2d90fd-8124-4fbb-a22a-67a3a59b5433" />

This is Norm, he is the Mondocat. He appears in human form as a girl/boy/enby. He is here to serve as a sperator between my text and the original repo text.








------

Below is the info from the original repo









# Update (02/2026): 

Th(e original) project is no longer maintained. I've since built [Hearica](https://hearica.com), a captioning app with lower requirements, better accuracy, and new features like session saving with audio replay. 

The original goal of this repo was an easy-to-install accessibility tool for everyone, but Whisper models turned out to be difficult to run for many users, and the chunking strategy used to compensate for the fact that Whisper models are not made for live captioning was quite error-prone. 

# System Captioner

Generates and shows real-time captions by listening to your Windows PC's audio. Makes digital content more accessible for those who are deaf or hard of hearing, aids language learning, and more. 


https://github.com/user-attachments/assets/7315ab7c-fe30-4c37-91aa-60bb32979338


## How it works

1. Captures system audio in real-time through Windows audio loopback using PyAudioWPatch
3. Locally transcribes the recordings using faster-whisper
4. Displays the transcriptions as captions in a overlay window that remains always on top


Language auto-detection, user-friendly GUI, draggable captions box, and intelligent mode that shows captions only when speech is detected.

By default, the app runs on and requires **nVidia CUDA** (dependencies included). The app should work with RTX 2000, 3000 and 4000 series cards. Turning off GPU mode will make the app run on CPU; start with the smallest model and settle with the model that's stable. 

## Installation (Windows)

1. Download the latest standalone .zip (currently 1.38) from the releases section and extract all files. 
 
2. Run SystemCaptioner.exe and follow the instructions.

Alternatively build the standalone executable yourself using build_portable.py. You will need the nvidia_dependencies folder from the standalone .zip (/SystemCaptioner/Controller/_internal/nvidia_dependencies) and install all the dependencies using requirements.txt inside a venv first. 

## Limitations/Troubleshooting 

‼️ Occasionally, the app can take a long time to start up/load a model. If there are no clear errors in console, wait for at least a few mins or try stopping and starting model again. 

If you experienced any issues with System Captioner, let me know in the 'Issues' page of this repo! Include the Console window log if possible. 
