#!/usr/bin/env python3
import gzip
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCE = "https://epgshare01.online/epgshare01/epg_ripper_CZ1.xml.gz"
OUT = Path("tv-epg")
CHANNELS = [
    ("ČT1.cz","ČT1"),("ČT2.cz","ČT2"),("ČT24.cz","ČT24"),("ČT.sport.cz","ČT sport"),
    ("ČT.:D.cz","ČT :D"),("Nova.cz","Nova"),("Nova.Cinema.cz","Nova Cinema"),
    ("Nova.Action.cz","Nova Action"),("Nova.Fun.cz","Nova Fun"),("Nova.Lady.cz","Nova Lady"),
    ("Prima.cz","Prima"),("Prima.Cool.cz","Prima COOL"),("Prima.LOVE.cz","Prima LOVE"),
    ("Prima.Krimi.cz","Prima Krimi"),("Prima.MAX.cz","Prima MAX"),("Prima.ZOOM.cz","Prima ZOOM"),
    ("Prima.Show.cz","Prima Show"),("CNN.Prima.News.cz","CNN Prima News")
]
KEEP = {x[0] for x in CHANNELS}

req = urllib.request.Request(SOURCE, headers={"User-Agent":"Mozilla/5.0","Referer":"https://epgshare01.online/"})
with urllib.request.urlopen(req, timeout=90) as r:
    root = ET.fromstring(gzip.decompress(r.read()))

out = ET.Element("tv", {"generator-info-name":"krsnak-cz-tv-guide"})
channel_by_id = {c.attrib.get("id"): c for c in root.findall("channel")}
for cid, name in CHANNELS:
    src = channel_by_id.get(cid)
    ch = ET.SubElement(out, "channel", {"id":cid})
    ET.SubElement(ch, "display-name").text = name
    if src is not None:
        icon = src.find("icon")
        if icon is not None:
            ch.append(icon)

for p in root.findall("programme"):
    if p.attrib.get("channel") not in KEEP:
        continue
    clean = ET.SubElement(out, "programme", dict(p.attrib))
    for tag in ("title","sub-title","category"):
        node = p.find(tag)
        if node is not None and node.text:
            n = ET.SubElement(clean, tag, dict(node.attrib))
            n.text = node.text

OUT.mkdir(exist_ok=True)
ET.ElementTree(out).write(OUT / "epg.xml", encoding="utf-8", xml_declaration=True)

epg = "https://raw.githubusercontent.com/krsnak/krsnak/main/tv-epg/epg.xml"
lines = ["#EXTM3U url-tvg=\"" + epg + "\""]
for cid, name in CHANNELS:
    lines += [f'#EXTINF:-1 tvg-id="{cid}" group-title="TV Program CZ",{name}', "https://example.invalid/" + cid]
(OUT / "guide.m3u").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("generated", len(CHANNELS), "channels", sum(1 for x in out if x.tag == "programme"), "programmes")

# Triggered by repository workflow.
