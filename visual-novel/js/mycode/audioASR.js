const audioASR = async audioData => {
  try {
    console.log("Sending audio to ABAIR ASR")
    const response = await fetch(
      "LINK REMOVED",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        recogniseBlob: audioData,
        developer: true,
        method: "online2bin"
      })
    })

    if (response.ok) {
      console.log("Recognized audio")
      const data = await response.json()
      return data
    } else {
      console.log("Error in recognizing audio")
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