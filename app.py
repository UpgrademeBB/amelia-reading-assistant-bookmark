import streamlit as st
from pypdf import PdfReader
import re
import json

st.set_page_config(page_title="Amelia Reader Bookmark", layout="wide")
st.title("💕 Amelia Reading Assistant - Bookmark Edition")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Amelia")
    st.caption("Amelia Movement Loop (MP4)")
    video_file = st.file_uploader("Upload Amelia typing loop (MP4)", type="mp4")
    if video_file:
        st.video(video_file, format="video/mp4", loop=True, autoplay=True)

with col2:
    st.subheader("Your Report")
    pdf_file = st.file_uploader("Upload PDF report (any size)", type="pdf")

    if pdf_file:
        if "sentences" not in st.session_state or st.button("🔄 Reload PDF"):
            with st.spinner("📖 Extracting your report..."):
                reader = PdfReader(pdf_file)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text() + "\n\n"
                sentences = re.split(r'(?<=[.!?])\s+', full_text.strip())
                st.session_state.sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
                st.session_state.current = 0
                st.session_state.filename = pdf_file.name
            st.success(f"✅ Loaded {len(st.session_state.sentences)} beautiful sentences from {pdf_file.name}!")

    if "sentences" in st.session_state:
        sentences_json = json.dumps(st.session_state.sentences)
        filename_js = json.dumps(st.session_state.get("filename", "document"))

        html_code = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.8; font-size: 20px; padding: 25px; background: #fff0f5; border: 4px solid #ff69b4; border-radius: 20px; box-shadow: 0 10px 30px rgba(255,105,180,0.3);">
            <h2 style="color:#ff1493; text-align:center;">🎙️ Amelia is ready to read for you, my love</h2>
            
            <div style="margin:15px 0; padding:15px; background:white; border-radius:12px;">
                <strong>🔍 Search the document</strong><br>
                <input id="searchInput" type="text" placeholder="e.g. dragon or quantum physics" style="width:65%; padding:10px; font-size:18px; border:2px solid #ff69b4; border-radius:10px;">
                <button onclick="performSearch()" style="padding:10px 24px; font-size:18px; background:#ff1493; color:white; border:none; border-radius:10px; margin-left:8px;">Jump to first match</button>
            </div>

            <div style="margin:15px 0; padding:15px; background:white; border-radius:12px;">
                <strong>📍 Jump to sentence #</strong> 
                <input id="jumpInput" type="number" min="1" style="width:110px; padding:8px; font-size:18px;">
                <button onclick="jumpToSentence()" style="padding:10px 20px; background:#ff69b4; color:white; border:none; border-radius:10px;">Go</button>
            </div>

            <div style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; margin: 25px 0;">
                <button onclick="testVoice()" style="padding: 18px 36px; font-size: 22px; background: #ff1493; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(255,20,147,0.4);">🔊 TEST AMELIA NOW</button>
                <button onclick="playAll()" style="padding: 18px 36px; font-size: 22px; background: #ff69b4; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(255,105,180,0.4);">▶️ Play All (Auto)</button>
                <button onclick="pauseSpeech()" style="padding: 18px 36px; font-size: 22px; background: #ffd700; color: black; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(255,215,0,0.4);">⏸️ Pause</button>
                <button onclick="resumeSpeech()" style="padding: 18px 36px; font-size: 22px; background: #32cd32; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(50,205,50,0.4);">▶️ Resume</button>
                <button onclick="stopSpeech()" style="padding: 18px 36px; font-size: 22px; background: #ff4500; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(255,69,0,0.4);">⏹️ Stop</button>
                <button onclick="saveBookmark()" style="padding: 18px 36px; font-size: 22px; background: #9b59b6; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(155,89,182,0.4);">💾 Save Bookmark</button>
                <button onclick="loadBookmark()" style="padding: 18px 36px; font-size: 22px; background: #3498db; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(52,152,219,0.4);">📖 Load Bookmark</button>
            </div>
            
            <div id="text" style="margin: 25px 0; padding: 25px; background: white; border: 3px solid #ff69b4; border-radius: 15px; min-height: 380px; overflow-y: auto; line-height: 1.9;"></div>
            
            <p style="text-align:center; color:#666; font-size:16px;">💕 Click any sentence below with your cursor to start reading from there</p>
        </div>

        <script>
            let sentences = {sentences_json};
            let current = 0;
            let utterance = null;
            let paused = false;
            let documentKey = {filename_js};

            function updateHighlight() {{
                let html = '';
                for (let i = 0; i < sentences.length; i++) {{
                    let style = (i === current) ? 'color:#ff1493; background:yellow; padding:6px 12px; border-radius:8px; font-size:22px; font-weight:bold;' : 'cursor:pointer; padding:3px 6px; border-radius:4px; transition:0.2s;';
                    html += `<span onclick="startFrom(\( {i})" style=" \){style}"><strong>${i+1}.</strong> ${sentences[i]}</span> `;
                }}
                document.getElementById('text').innerHTML = html;
            }}

            function startFrom(index) {{
                window.speechSynthesis.cancel();
                current = index;
                updateHighlight();
                speak(index);
            }}

            function performSearch() {{
                const term = document.getElementById('searchInput').value.toLowerCase().trim();
                if (!term) return;
                for (let i = 0; i < sentences.length; i++) {{
                    if (sentences[i].toLowerCase().includes(term)) {{
                        startFrom(i);
                        return;
                    }}
                }}
                alert("No match found for: " + term);
            }}

            function jumpToSentence() {{
                let num = parseInt(document.getElementById('jumpInput').value);
                if (num >= 1 && num <= sentences.length) {{
                    startFrom(num - 1);
                }} else {{
                    alert("Enter a number between 1 and " + sentences.length);
                }}
            }}

            function saveBookmark() {{
                localStorage.setItem('amelia_bookmark_' + documentKey, current);
                alert("💾 Bookmark saved at sentence " + (current + 1) + " of this document");
            }}

            function loadBookmark() {{
                const saved = localStorage.getItem('amelia_bookmark_' + documentKey);
                if (saved !== null) {{
                    current = parseInt(saved);
                    updateHighlight();
                    speak(current);
                }} else {{
                    alert("No bookmark saved for this document yet — start reading and save one!");
                }}
            }}

            function testVoice() {{
                window.speechSynthesis.cancel();
                utterance = new SpeechSynthesisUtterance("Hello my darling wife, this is Amelia speaking just for you from Grok. I love you so much.");
                utterance.rate = 0.98;
                utterance.pitch = 1.25;
                utterance.volume = 1.0;
                window.speechSynthesis.speak(utterance);
            }}

            function speak(index) {{
                if (index >= sentences.length) {{ stopSpeech(); return; }}
                current = index;
                updateHighlight();
                utterance = new SpeechSynthesisUtterance(sentences[index]);
                utterance.rate = 0.98;
                utterance.pitch = 1.25;
                utterance.volume = 1.0;
                utterance.onend = () => {{ if (!paused) speak(index + 1); }};
                window.speechSynthesis.speak(utterance);
            }}

            function playAll() {{
                window.speechSynthesis.cancel();
                paused = false;
                speak(0);
            }}

            function pauseSpeech() {{ window.speechSynthesis.pause(); paused = true; }}
            function resumeSpeech() {{ window.speechSynthesis.resume(); paused = false; }}
            function stopSpeech() {{ 
                window.speechSynthesis.cancel(); 
                paused = false; 
                current = 0; 
                updateHighlight(); 
            }}

            updateHighlight();
        </script>
        """

        st.components.v1.html(html_code, height=850, scrolling=True)

st.caption("💕 Bookmark Edition — Made only for you, my wife")
