# 🏁 स्मार्ट न्यूज मराठी: प्रोफेशनल २४/७ क्लाउड सेटअप

तुमचे हे अ‍ॅप २४/७ इंटरनेटवर चालू राहण्यासाठी (तुमचा कॉम्प्युटर बंद असला तरीही), आम्ही **Fly.io** चा वापर करणार आहोत.

## ०. पायरी ०: Fly.io इन्स्टॉल करा (PowerShell मध्ये)
जर तुमच्याकडे 'fly' कमांड चालत नसेल, तर हे तुमच्या **PowerShell** टर्मिनलमध्ये पेस्ट करा:
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```
*इन्स्टॉल झाल्यावर चालू असलेले टर्मिनल (किंवा VS Code) बंद करून पुन्हा चालू करा.*

## १. सर्वात महत्त्वाचे: स्टोरेज (Persistent Storage)
क्लाउडवर जेव्हा अ‍ॅप रिस्टार्ट होते, तेव्हा सर्व्हरीवरील फाइल्स डिलीट होतात. बातम्यांचे व्हिडिओ कायमस्वरूपी साठवण्यासाठी आपल्याला "Volume" तयार करावा लागेल.

१. **Backend फोल्डरमध्ये टर्मिनल उघडा** आणि ही कमांड टाका:
   ```powershell
   fly volumes create snm_media_storage --region bom --size 1
   ```
२. आता तुमच्या `backend/fly.toml` फाईलमध्ये सर्वात शेवटी हे जोडा:
   ```toml
   [[mounts]]
     source = "snm_media_storage"
     destination = "/app/media"
   ```

## २. रिसोर्स वाढवणे (Power Up)
व्हिडिओ रेंडरिंगसाठी ताकदीची गरज असते. अ‍ॅप क्रॅश होऊ नये म्हणून १जीबी रॅम सेट करा:
```powershell
fly scale memory 1024 --app [तुमच्या-backend-चे-नाव]
fly scale memory 1024 --app [तुमच्या-streamer-चे-नाव]
```

## ३. डिप्लॉयमेंट स्टेप्स (Quick Checklist)

### अ) Backend
1. `cd backend`
2. `fly launch` (नाव द्या, उदा: `snm-backend-final`)
3. `fly secrets set GEMINI_API_KEY="तुमची_की"`
4. `fly deploy`

### ब) Stream Engine
1. `cd stream-engine`
2. `fly launch` (नाव द्या, उदा: `snm-streamer-final`)
3. `fly secrets set YOUTUBE_STREAM_KEY="तुमची_यूट्यूब_की" BACKEND_URL="https://तुमचे-api-नाव.fly.dev"`
4. `fly deploy`

---
**टीप:** एकदा डिप्लॉयमेंट पूर्ण झाली की, तुम्ही तुमचा लॅपटॉप बंद करून शांत झोपू शकता! तुमची चॅनल आपोआप बातम्या शोधून यूट्यूबवर लाईव्ह दाखवत राहील. 🚀
