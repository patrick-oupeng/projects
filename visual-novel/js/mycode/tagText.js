const tagText = async inputText => {
  // Returns POS-tagged Irish text
  // [{lemma: 'y', tags: 'x x x x', word: 'z'}, ...]
  // Full description of Morphological tags:
  // https://www.scss.tcd.ie/~uidhonne/morphtag.htm
  // New API (abair) appears to be broken as of 9/2024. Switching back to the old API and using CORS.
  api_str_old = "LINK REMOVED";
  api_str_new = "LINK REMOVED";
  send_str_new = api_str_new + encodeURIComponent(inputText);
  send_str_old = api_str_old + encodeURIComponent(inputText);
  console.log('Tagging input text: ' + inputText);
  // console.log('Tagging API call: ' + send_str);
  try {
    console.log('Trying new API')
    const response = await fetch(
        send_str_new,
      {
      method: "GET",
      headers: {
        "accept": "application/json",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
      },
    });
    if (response.ok) {
      console.log('new API response OK')
      const data = await response.json()
      console.log(data)
      return data
    } else {
      const errorText = await response.text()
      // Handle non-2xx HTTP error status codes
      throw new Error(
        `Request failed with status ${response.status}. ${errorText}`
      )
    }
  } catch (error1) {
    console.log('new API response bad')
    try {
      // second try put in January 2025
      // Not sure if the new API is broken or if it's a weird CORS thing again.
      console.log(error1.message)
      console.log("Trying old API")
      const response = await fetch(
          send_str_new,
        {
        method: "GET",
        headers: {
          "accept": "application/json",
          "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        },
      });
      if (response.ok) {
        console.log('old API response ok')
        const data = await response.json()
        console.log(data)
        return data
      } else {
        const errorText = await response.text()
        // Handle non-2xx HTTP error status codes
        throw new Error(
          `Request failed with status ${response.status}. ${errorText}`
        )
      }
    } catch (error2) {
      console.log('old API response bad')
      // todo: check how this is used.
      console.log(error2.message)
      console.log("Both tagger APIs failed!")
      // I guess now I just return it as a list of dicts of words?
      // input
      // word_list = input.split()
      // data = [{lemma: w, word: w}] for w in word_list
      // return false
      input_list = inputText.split(' ')
      ret_list = []
      for (var i=0; i < input_list.length; i++) {
        ret_list[i] = {'lemma':input_list[i], 'word':input_list[i]}
      }
    }
  }
}