# ❓ Real-Time MIDI Notation — FAQ (v2.0.0)

A collection of the most common questions from users, testers, developers, and researchers.

---

# 🎹 MIDI & INPUT

### **Q: My MIDI device is not detected.**
Most DAWs lock MIDI ports. Close all DAWs (FL Studio, Ableton, Cubase, etc.) and restart the app.  
If still not detected:
- reconnect the device  
- restart the OS  
- check OS MIDI permissions  
- ensure no other app is using the MIDI port  
- try a wired USB connection instead of Bluetooth  

### **Q: Does this support Yamaha arranger keyboards?**
Yes — the engine is built around the **Yamaha 16‑track standard**, including:
- channel colors  
- multi‑track routing  
- accompaniment parts  
- real‑time visualization  

### **Q: Can I use virtual MIDI ports?**
Yes — LoopMIDI (Windows), IAC Driver (macOS), and similar tools work perfectly.

### **Q: Does it support USB MIDI keyboards?**
Yes — any class‑compliant MIDI device works.

---

# 🎨 RENDERING & UI

### **Q: Why are notes delayed?**
Possible causes:
- high system latency  
- slow audio/MIDI drivers  
- background CPU load  
- USB hub bottlenecks  
- low‑quality MIDI interface  

### **Q: Why do some beams not appear?**
Beam grouping depends on rhythmic analysis.  
Unusual timing or extreme rhythms may require future improvements.

### **Q: Why are some notes drawn with different colors?**
Colors represent **tracks** (Yamaha 16‑track standard).  
Each track has its own color.

### **Q: Why does the renderer scroll automatically?**
Scrolling follows the **playhead**, controlled by the PlaybackEngine.

---

# 🧠 ARCHITECTURE & ENGINE

### **Q: Is the renderer modular?**
Yes — every part of the system is isolated:
- Processor  
- Renderer  
- UI  
- TrackManager  
- EventBus  
- StreamHandler  

### **Q: Can I replace the renderer with my own?**
Yes — the architecture supports custom renderers.

### **Q: Is this a DAW?**
No — it is a **real‑time notation engine**, not an audio workstation.

### **Q: Does it support audio?**
Not yet — MIDI only.

---

# 🛠 DEVELOPMENT & CONTRIBUTING

### **Q: How do I contribute?**
See **CONTRIBUTING.md** for:
- PR rules  
- feature requests  
- issue reporting  
- contributor levels  

### **Q: Can I add new UI components?**
Yes — UIManager v2 is designed for extension.

### **Q: Can I use this in my own project?**
Yes — the MIT License allows full reuse, including commercial use.

---

# 📦 EXPORT & FILES

### **Q: Can I export notation?**
Export is planned for:
- PNG  
- SVG  
- PDF  

### **Q: Can I load MIDI files?**
MIDI file import is planned for a future version.

---

# 🧪 TESTING & PERFORMANCE

### **Q: Why is the renderer slow on my system?**
Try:
- closing GPU‑heavy apps  
- updating graphics drivers  
- reducing window size  
- disabling background processes  
- using a wired MIDI interface instead of Bluetooth  

### **Q: Why does the playhead drift?**
This can happen if:
- CPU is overloaded  
- system timer resolution is low  
- background tasks interrupt timing  
- OS power‑saving modes are active  

---

# 🧩 MISCELLANEOUS

### **Q: Is this project stable?**
Yes — all core modules are complete and stable as of v2.0.0.

### **Q: Is this suitable for education?**
Absolutely — it is ideal for:
- music theory  
- rhythm training  
- MIDI analysis  
- live performance visualization  

### **Q: Is this suitable for research?**
Yes — the modular architecture is ideal for:
- real‑time systems  
- music informatics  
- HCI research  
- visualization studies  

---

# 🎉 More questions?
Open an Issue or contact the maintainer at **richardpizem@gmail.com**.
