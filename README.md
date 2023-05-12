# GEN2 Wallbox for Home Assistant

This is integration for the wallbox GEN2 EcoCharge instaled by the MalinaGroup mainly in CZ / SK or DE. This one:

![wallbox image](imgs/gen2_middle.jpg)

This wallbox is just rebranded Tuya and it is possible to control it using tinytuy (https://github.com/jasonacox/tinytuya) via local network.  

## Installation via HACS - recomended
The preffered variant is HACS (Home Assistant Comunity Store)

1. Install HACS to your Home Assistant (https://hacs.xyz/docs/setup/download/)

2. **Add this repository**. 
 Navigate to HACS -> Integrations. 
 ![](imgs/hacs1.png)
 Add this github repo URL as "Integration"
 ![](imgs/hacs2.png)

3. Search for  GEN2 Wallbox integration and download it
4. Restart Home Assistant

## Manual instalation
Copy content `custom_components/gen2_wallbox` to your home assistant.

## Configuration
TODO
- get DEVICEID, IP and LOCALKEY

