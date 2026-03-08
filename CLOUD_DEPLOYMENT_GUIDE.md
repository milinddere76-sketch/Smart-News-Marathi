# 🚩 स्मार्ट न्यूज मराठी: Fly.io डिप्लॉयमेंट

तुमचा प्रोजेक्ट आता **Fly.io** वर अतिशय स्थिर आणि कार्यक्षमपणे चालेल. Fly.io तुमचे Backend, Frontend आणि YouTube Stream Engine या तिन्हींना एकाच ठिकाणी उत्कृष्टपणे चालवू शकते.

## १. पूर्वतयारी (Prerequisites)
१. **Fly.io Account**: [https://fly.io/](https://fly.io/) वर जाऊन अकाउंट काढा.
२. **Payment Method**: (नवीन अकाउंटला मोफत क्रेडिट्स मिळण्यासाठी कार्ड किंवा पेपाल लिंक करावे लागते, पैसे कापले जात नाहीत.)
३. **Flyctl इन्स्टॉल करा**:
   - तुमच्या कॉम्प्युटरवर Terminal (किंवा PowerShell) उघडा आणि ही कमांड टाका:
   - इन्स्टॉल झाल्यावर टर्मिनल (VS Code चे टर्मिनल) **बंद करून पुन्हा चालू करा**.
   - नंतर टर्मिनलमध्ये ही कमांड टाईप करून लॉगिन करा:
     ```powershell
     & "$HOME\.fly\bin\flyctl" auth login
     ```
   *(जर फक्त `fly` चालत नसेल, तर नेहमी `& "$HOME\.fly\bin\flyctl"` असे पूर्ण नाव वापरा)*

> [!NOTE]
> **Windows वापरकर्त्यांसाठी महत्त्वाचे:** जर तुमचा प्रोजेक्ट D: ड्राइव्हवर असेल आणि तुमचे टर्मिनल C: वर असेल, तर `cd` करण्यापूर्वी `d:` टाईप करून एंटर दाबा जेणेकरून ड्राइव्ह बदलेल.

---

## २. Backend डिप्लॉयमेंट (API)
आपल्याला सर्वात आधी Backend सुरू करावे लागेल जेणेकरून आपल्याला त्याची URL मिळेल.

१. **टर्मिनलमध्ये तुमच्या `backend` फोल्डरमध्ये जा** (ड्राइव्ह बदलण्याचे लक्षात ठेवा):
   ```powershell
   d:
   cd "d:\Apps\Smart News Marathi\backend"
   ```
   - (आधी आपली फाईल्स दिसतात का ते तपासा): `ls` कमांड टाका. तुम्हाला `Dockerfile` आणि `fly.toml` दिसले पाहिजेत.

२. **अ‍ॅप तयार करा**:
   ```powershell
   & "$HOME\.fly\bin\flyctl" apps create smart-news-backend --org personal
   ```
   *(टीप: जर नाव आधीच वापरले असेल, तर थोडे वेगळे नाव द्या, उदा. `smart-news-backend-तुमचेनाव`. महत्त्वाचे: जर तुम्ही नाव बदलले, तर तुमच्या फोल्डरमधील `fly.toml` उघडा आणि `app = "..."` मध्ये तेच नवीन नाव लिहा.)*

३. **Environment Variables सेट करा**:
   ```powershell
   & "$HOME\.fly\bin\flyctl" secrets set DATABASE_URL="तुमची_Neon_URL" GEMINI_API_KEY="तुमची_की"
   ```

४. **थेट डिप्लॉय करा**:
   ```powershell
   & "$HOME\.fly\bin\flyctl" deploy --remote-only
   ```
   *(आता फ्लाई ऑटोमॅटिकली `fly.toml` वाचेल आणि डिप्लॉयमेंट सुरू करेल.)*

*(यशस्वी झाल्यावर तुम्हाला `https://smart-news-backend.fly.dev` अशी लिंक मिळेल. ती कॉपी करून ठेवा.)*

---

१. **टर्मिनलमध्ये `frontend` फोल्डरमध्ये जा**:
   ```powershell
   d:
   cd "d:\Apps\Smart News Marathi\frontend"
   ```
२. **अ‍ॅप तयार करा**:
   ```powershell
   & "$HOME\.fly\bin\flyctl" apps create dere-snm-frontend --org personal
   ```
३. **Backend URL आणि YouTube ID लिंक करा**:
   ```powershell
   & "$HOME\.fly\bin\flyctl" secrets set NEXT_PUBLIC_API_URL="वरती_काढलेली_Backend_ची_लिंक" NEXT_PUBLIC_YOUTUBE_ID="तुमची_यूट्यूब_चॅनल_ID"
   ```
   *(टीप: `NEXT_PUBLIC_YOUTUBE_ID` हा तुमच्या यूट्यूब चॅनलचा ID आहे, उदा. `UCxxxxxxxxxxxxxxx`. तो तुम्हाला YouTube Studio च्या Settings मध्ये मिळेल.)*
४. **थेट डिप्लॉय करा**:
   ```powershell
   & "$HOME\.fly\bin\flyctl" deploy --remote-only
   ```
आता तुमची वेबसाईट Fly.io वर जगासाठी लाईव्ह आहे! 🚩🚀

---

१. **टर्मिनलमध्ये `stream-engine` फोल्डरमध्ये जा**:
   ```powershell
   d:
   cd "d:\Apps\Smart News Marathi\stream-engine"
   ```
२. **अ‍ॅप तयार करा**:
   ```powershell
   & "$HOME\.fly\bin\flyctl" apps create dere-snm-streamer --org personal
   ```

> [!TIP]
> **YouTube Stream Key कशी मिळवायची?**
> १. YouTube वर जाऊन [YouTube Studio](https://studio.youtube.com/) उघडा.
> २. वरती उजव्या कोपऱ्यात **Create** -> **Go Live** वर क्लिक करा.
> ३. तिथे डाव्या बाजूला **Stream Settings** मध्ये तुम्हाला **Stream Key** दिसेल. ती कॉपी करून खालील कमांडमध्ये वापरा.
   ```
३. **यूट्यूब की आणि Backend लिंक द्या**:
   ```powershell
   & "$HOME\.fly\bin\flyctl" secrets set YOUTUBE_STREAM_KEY="तुमची_YouTube_की" BACKEND_URL="वरती_काढलेली_Backend_ची_लिंक"
   ```
४. **थेट डिप्लॉय करा**:
   ```powershell
   & "$HOME\.fly\bin\flyctl" deploy --remote-only
   ```

---

## ५. लाईव्ह स्ट्रीम का दिसत नाही? (Troubleshooting)
जर डिप्लॉयमेंट झाल्यावरही स्ट्रीम दिसत नसेल, तर खालील गोष्टी तपासा:
१. **Backend ला बातम्या आहेत का?**: जोपर्यंत Backend बातम्या तयार करत नाही, तोपर्यंत Streamer फक्त 'Placeholder' (ब्लू स्क्रीन) दाखवेल.
२. **Secrets तपासा**: `NEXT_PUBLIC_API_URL` मध्ये `https://` असणे आवश्यक आहे.
३. **YouTube ID**: तुमचा Channel ID बरोबर असल्याची खात्री करा.

*झालं! आता तुमचे तिन्ही घटक Fly.io वर उत्तमरित्या चालू आहेत आणि यूट्यूब लाईव्ह स्ट्रीम २-३ मिनिटांत सुरू होईल!* 🚩🚩🚩🚀
