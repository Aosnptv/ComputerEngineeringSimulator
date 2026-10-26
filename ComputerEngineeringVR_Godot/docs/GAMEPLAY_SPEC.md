# Gameplay specification

PC Easy installs RAM, SSD, and GPU then inspects. Normal adds CPU, cooler, exact board/CPU power links, and inspection. Hard includes decoy socket/memory parts, PSU capacity selection, GPU power, and a state-driven POST check.

LAN Easy connects PC1–Switch–Router. Normal adds PC2 and simulated reachability. Hard adds PC3, deterministic fault seed 20261027, IP/mask/gateway repair, duplicate detection, and all-device reachability. Links are logical endpoint pairs; no host packets are sent.

Programming Easy reaches a fixed 4×4 goal with movement blocks. Normal uses Repeat on 5×5. Hard runs the same conditional program against two 6×6 obstacle scenarios. The interpreter tracks position, direction, trace, construct use, collisions, and a 256-step ceiling.

Easy gives exact goals; Normal gives work-area guidance; Hard provides no continuous answer highlighting. Hints are not penalized. Incorrect confirmed actions are deduplicated by stable action ID.

