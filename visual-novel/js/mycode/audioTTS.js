// todo speed it up a bit?
const audioTTS = async inputText => {
  // Returns base64 encoded mp3 audio
  default_voice = "ga_CO_snc_nemo"; 
  api_str = "LINK REMOVED";
  voice_str = "&voice=" + default_voice;
  send_str = api_str + encodeURIComponent(inputText) + voice_str;
  console.log('TTS input text: ' + inputText);
  console.log('TTS API call: ' + send_str);
  try {
    const response = await fetch(
        send_str,
      {
      method: "GET",
      headers: {
        "accept": "application/json",
      },
    });
    if (response.ok) {
      console.log('in tts response.ok ')
      const data = await response.json()
      return data
    } else {
      console.log('in tts response else ')
      // Handle non-2xx HTTP error status codes
      const errorText = await response.text()
      throw new Error(
        `Request failed with status ${response.status}. ${errorText}`
      )
    }
  } catch (error) {
    alert(error.message)
    return false
  }
}