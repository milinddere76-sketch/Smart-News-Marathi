# 🚩 स्मार्ट न्यूज मराठी: Render डिप्लॉयमेंट मार्गदर्शिका

तुमचा प्रोजेक्ट आता **Render** वर अतिशय स्थिर आणि कार्यक्षमपणे चालेल. Render चे 'Blueprints' वैशिष्ठ्य तुमचे Backend, Frontend, Redis आणि Stream Engine या सर्वांना एकाच वेळी आपोआप सेट करते.

## १. पूर्वतयारी (Prerequisites)

१. **Render Account**: [https://render.com/](https://render.com/) वर जाऊन अकाउंट काढा.
२. **GitHub/GitLab**: तुमची कोड फाईल्स GitHub वर पुश केलेली असावीत.
३. **Neon.tech (Database)**: तुमच्याकडे Neon PostgreSQL ची URL तयार असावी.

---

## २. डिप्लॉयमेंट प्रक्रिया (Step-by-Step)

तुमच्या प्रोजेक्टमध्ये `render.yaml` फाईल आधीच तयार आहे. ती वापरून डिप्लॉय करण्यासाठी खालील पायऱ्या वापरा:

१. **Render Dashboard** वर जा.
२. **New** बटनावर क्लिक करा आणि **Blueprint** निवडा.
३. तुमचा GitHub प्रोजेक्ट कनेक्ट करा.
४. तुमच्या 'Service Group' ला एक नाव द्या (उदा. `vartapravah-news`).
५. खालील **Environment Variables** (Secrets) विचारले जातील, ते भरा:
   - `DATABASE_URL`: तुमची Neon PostgreSQL लिंक.
   - `GEMINI_API_KEY`: तुमची Google Gemini API की.
   - `YOUTUBE_STREAM_KEY`: तुमची YouTube Live Stream की.

६. **Apply** बटनावर क्लिक करा.

आता Render आपोआप खालील गोष्टी तयार करेल:
- **Backend**: FastAPI सर्व्हर (Marathi fonts आणि FFmpeg सह).
- **Frontend**: Next.js टीव्ही डॅशボード.
- **Redis**: अंतर्गत डेटा मॅनेजमेंटसाठी.
- **Stream Engine**: बॅकग्राउंडमध्ये व्हिडिओ जनरेट करून यूट्यूबवर पाठवणारा सर्व्हर.

---

## ३. महत्त्वाच्या लिंक (Internal Networking)

Render च्या अंतर्गत नेटवर्कमुळे:
- **Frontend** आपोआप Backend ला जोडले जाईल.
- **Stream Engine** आपोआप Backend ला जोडले जाईल.
तुमच्या `render.yaml` मध्ये हे सर्व आधीच सेट केलेले आहे.

---

## ४. मीडिया स्टोअरेज (Persistent Disk)

Render वर Backend साठी **१० GB चा टॅब (Disk)** जोडला जाईल. यामुळे डिप्लॉयमेंट रिस्टार्ट झाली तरी तुमचे जुने व्हिडिओ आणि ऑडिओ फाईल्स सुरक्षित राहतील.

---

## ५. लाईव्ह स्ट्रीम सुरू करणे

डिप्लॉयमेंट यशस्वी झाल्यावर:
१. **Backend** सुरू होईल आणि बातम्या गोळा करेल.
२. **Streamer** बातम्यांचे व्हिडिओ बनवून यूट्यूबवर पाठवेल.
३. पहिल्यांदा व्हिडिओ दिसायला ३-५ मिनिटे लागू शकतात.

*झालं! तुमचा प्रोजेक्ट आता Render वर २४x७ लाईव्ह आहे!* 🚩🚩🚩🚀
