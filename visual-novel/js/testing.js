// for testing
function test_POS () {
	console.log("Testing that part-of-speech tagger works")
	inputstr = "Patrick is ainm dom";
	console.log("Test string: " + inputstr)
	potential_names = []
	tagText(inputstr).then( resp => {
		for (var i = 0; i < resp.length; i++) {
			word = resp[i].word
			tags = resp[i].tags
			if (tags.includes('Prop')) {
				potential_names.push(word)
			}
		}
		console.log(potential_names)
		if (potential_names.length === 1) {
			console.log('found a name')
			console.log(potential_names[0])
			return potential_names[0]
		} else {
			console.log('too many or too few names found')
		}
	});
}

function test_TTS () {
	console.log("Testing that TTS works")
	inputstr = "Dia dhuit";
	console.log("Test string: " + inputstr)
	const audio = document.createElement("audio");
	audioTTS(inputstr).then( resp => {
		console.log("in test tts")
		audio.src ="data:audio/mp3;base64," + resp.audioContent
		console.log(audio)
		audio.play()
			.then(() => {
				console.log("sound is playing")
			})
			.catch( error => {
				console.log(error)
			})
		})
}

// Old regex name method
// name_rgx = /(?:[Nn]ame is|[Ss]?[Hh]e(?:'s| is) called|[Cc]all (?:me|him|her)|I'm|I am|[Ss]?[Hh]e(?: is|'s)) (.*)[\. \n\r$]?/;
// parsed_name = name_rgx.exec(inputstr);
// if (parsed_name === null){
// 	console.log('1')
// 	return inputstr;
// } else if (parsed_name.length > 1) {
// 	console.log('2')
// 	return parsed_name[1];
// } else {
// 	console.log('3')
// 	return inputstr;
// }