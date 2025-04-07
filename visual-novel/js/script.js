/* global monogatari */

// Define the messages used in the game.
// leftover from the base tutorial code
monogatari.action ('message').messages ({
	'Help': {
		title: 'Help',
		subtitle: 'Some useful Links',
		body: `
			<p><a href='https://developers.monogatari.io/documentation/'>Documentation</a> - Everything you need to know.</p>
			<p><a href='https://monogatari.io/demo/'>Demo</a> - A simple Demo.</p>
		`
	},
	// 'Survey': {
	// 	title: '<center>Survey link:</center>',
	// 	body:`
	// 		<center>
	// 			<b><a href="LINK REMOVED" target="_blank" style="color: #0000ff; background-color: #FFFF00">click here</a></b>
	// 		</center>
	// 	`
	// },
	'Survey': {
		title: '<center>Survey link:</center>',
		body:`
			<center>
				<b>The survey has closed. Thanks to everyone who participated!</b>
			</center>
		`
	},
});

// Define the notifications used in the game
// leftover from the base tutorial code
monogatari.action ('notification').notifications ({
	'Welcome': {
		title: 'Welcome',
		body: 'This is the Monogatari VN Engine',
		icon: ''
	}
});

// Define the Particles JS Configurations used in the game
monogatari.action ('particles').particles ({

});

// Define the canvas objects used in the game
monogatari.action ('canvas').objects ({

});

// Credits of the people involved
// todo add references for pictures and AI gen?
monogatari.configuration ('credits', {
	"":{
		"Developer": "Patrick O'Neil",
		"Lead advisor": "Dr. Neasa Ní Chiaráin",
		"Co-advisor": "Dr. John Sloan",
		"Irish translator": "Muireann Nic Corcráin",
		"Playtesting": "TCD Speech & Phonetics Lab",
		"Special thanks to": 'The ABAIR initiative: <a href="https://abair.ie" style="color: #0000ff">abair.ie</a>',
		"": "MidZM, Hyuchia, and the rest of the Monogatari discord",
	},
});

// Define the images that will be available on your game's image gallery
monogatari.assets ('gallery', {

});

// Define the music used in the game.
monogatari.assets ('music', {

});

// Define the voice files used in the game.
monogatari.assets ('voices', {
	// These are voice lines that don't have any variables, so it's easier to just play
	// Some are repeats, and could certainly be cleaned up. 
	// Also, due to coding constraints, some have to be generated anyway - see GetAbsenceReasonLoop
	// The phone sounds are coded as voices so that they stop once you click the next screen
	phone: 'phone-ringing-faster.mp3', // from pixabay
	hangup: 'cell-phone-hang-up-100514.mp3', // from pixabay
	s0: 	'script0.mp3',	// 'Agus cén duine atá ag déanamh an bhailiúcháin?',
	s1: 	'script1.mp3',	// 'Agus cén t-am a shroichfidh siad an scoil?',
	s2: 	'script2.mp3',	// 'Agus thart ar cén t-am a bheidh siad bailithe?',
	s3: 	'script3.wav',	// 'An bhfuil tú ag cur glaoch chun asláithreacht a thuairisciú, am sroichte níos déanaí a thuairisciú, nó dalta a bhailiú níos luaithe i rith an lae?',
	s4: 	'script4.mp3',	// 'An féidir é sin a rá arís?',
	s5: 	'script5.mp3',	// 'Cathain a fhillfidh siad ar an scoil?',
	s6: 	'script6.mp3',	// 'Ceart go leor, déanfaidh mé taifead don asláithreacht anseo mar eile.', 
	s7: 	'script7.mp3',	// 'Cé a bheidh ar an duine atá ag déanamh an bhailiúcháin?',
	s8: 	'script8.wav',	// 'Cén chúis atá ann don asláithreacht seo?',
	s10:	'script10.mp3',	// 'Cén dáta a bheidh siad as láthair?',
	s11:	'script11.mp3',	// 'Cén lá a bheidh siad bailithe luath?',
	s12:	'script12.mp3',	// 'Cén lá a bheidh siad déanach?',
	s13:	'script13.mp3',	// 'Cén t-ainm atá ar an dalta scoile?',
	s15:	'script15.mp3',	// 'Cén t-am a shroichfidh siad an scoil?',
	s16:	'script16.mp3',	// 'Dia duit, seo í an rúnaí.',
	s17:	'script17.mp3',	// 'Déarfaidh mé leat céard atá scriofa agam faoi láthair...',
	s18:	'script18.mp3',	// 'Tá brón orm, níor chuala mé thú. An féidir é sin a rá arís?',
	s19:	'script19.mp3',	// 'Tá píosa eolais breise ag teastáil uaim uaitse mar sin.',
	s21:	'script21.mp3',	// 'Gabh mo leithscéal, ní féidir liom cabhrú leat ach le hasláithreacht, páiste ag teacht isteach déanach nó ag bailiú páiste luath.',
	s22:	'script22.mp3',	// 'Ó, bain sult as sin.',
	s23:	'script23.mp3',	// 'Ó, tá súil agam go bhfuil gach rud ceart go leor.',
	s24:	'script24.mp3',	// 'Tá brón orm é sin a chloisint.',
	s25:	'script25.wav',	// 'An bhuil sin ceart?',
});

// Define the sounds used in the game.
monogatari.assets ('sounds', {
	// 'phone-ringing': 'phone-ringing-faster.mp3',
});

// Define the videos used in the game.
monogatari.assets ('videos', {

});

// Define the images used in the game.
monogatari.assets ('images', {

});

// Define the backgrounds for each scene.
monogatari.assets ('scenes', {
	'admin': 'admin-office-1.jpg',
	'clutter': 'cluttered-desk.jpg',
	'principal': 'principal-office.jpg',
	'couches': 'welcome-couches.jpg',
	'big': 'big-office.jpg',
	'cozy': 'cozy-office.jpg',

	'parliament': 'parliament-square.jpeg',
	'tcd': 'tcd-cropped.jpeg',
});

// Define the Characters
monogatari.characters ({
	'y': {
		name: 'Yui',
		color: '#5bcaff'
	},
	'p': {
		name: 'Patrick',
		color: '#87ceeb',
		sprites: {
			'smiling': 'patrick2-small.png',
		}
	},
	's': {
		// name: 'Secretary',
		name: 'Rúnaí',
		color: '#442d65',
		sprites: {
			// old
            // asking: 'asking.png',
            // confused: 'confused.png',
            // happy: 'happy.png',
            // laughing: 'laughing.png',
            // pensive: 'pensive.png',
            
            // new
            asking: 'serious.png',
            bored: 'bored.png',
            confused: 'clutching.png',
            empty: 'empty-nochair.png',
            happy: 'laughing-smiling.png',
            pensive: 'distant.png',
            writing: 'writing-nochair-desk.png',
        }
	}
});

// I *think* that storage.js is used to save/load games.
// Not sure how it works, but not important for my purposes.
monogatari.storage ({
	player: {
		name: '', // Optional player name - currently used as a placeholder
		childname: '', // Child's name
		reason: '', // reason for calling: absence/late/pickup
		absence_reason: '', // reason for absence: sick/urgent/holiday/other
		date: '', // Date for pickup/late arrival
		startdate: '', // only for absence - start day of absence
		enddate: '', // only for absence - end day of absence
		time: '', // Time for pickup/late arrival
		reasonstr: '', // Used for printing to dialogues dynamically
		pickup_name: '', // name of person picking them up
	},
});

function capitalize_first_letter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function capitalize_all_words(inputstr){
	split_input = inputstr.split(' ')
	caps = split_input.map(s => capitalize_first_letter(s))
	return caps.join(' ')
}

async function getname (inputstr) {
	caps_input = capitalize_all_words(inputstr)
	// If we know the child's name, then we're asking about who 
	// will pick them up, which could be pronominal
	if (monogatari.storage('player').childname != '') {
		tagged_lower_text = await tagText(inputstr)
		// todo if I store just like this, then some strings will be weird
		// e.g. scriptHelpers confirmation
		const pickup_pronouns = [
			'bean', 
			'fear', 
			'chéile', 
			'céile', 
			'máthair', 
			'athair',
			'mé',
			'féin',
		]
		lemmas = tagged_lower_text.map(l => l.lemma)
		const filteredArray = pickup_pronouns.filter(pron => lemmas.includes(pron))
		if (filteredArray.length > 0){
			// naive, but workable
			// could change this to check if it's 'bean' or 'fear' or etc. and then switch to like 'your bean / fear/ self'
			return filteredArray[0]
		}		
	}
	// can also check the Guess tag?
	tagged_upper_text = await tagText(caps_input)
	found_names = _get_tagged_text(tagged_upper_text, 'Prop')
	console.log('Found potential names: ' + found_names)
	if (found_names.length == 1) { // Aoife
		return found_names[0]
	} else if (found_names.length == 2) { // Aoife Cunningham
		return found_names.join(' ')
	} else {
		return ''
	}
}

async function getabsencereason (inputstr) {
	console.log("In getabsencereason")
	tagged_text = await tagText(inputstr)
	console.log(tagged_text)
	lemmas = tagged_text.map(l => l.lemma)
	console.log("lemmas: " + lemmas)
	const absence_reason_keywords = {
		// 'illness': ['sick', 'cold', 'flu', 'came down with something', 'not feeling well', 'doctor'],
		// 'family': ['grandma', 'grandpa', 'wedding', 'funeral', 'died'], // this is depressing
		// 'holiday': ['vacation', 'holiday', 'traveling'],
		'tinneas': ['tinn', 'fuar', 'fliú', 'dochtúir', 'slaghdán', 'coinne', 'breoite'],
		// bainis couldn't be tagged
  		'teaghlach': ['seanmháthair', 'seanathair', 'bainis', 'sochraid', 'bás', 'teaghlach', 'bráthair', 'deirfiúr', 'siúr'], // this is depressing
  		'saoire': ['saoire', 'taisteal'],
	}
	for (var reason in absence_reason_keywords) {
		if (absence_reason_keywords.hasOwnProperty(reason)){
			const filteredArray = absence_reason_keywords[reason].filter(value => lemmas.includes(value))
			if (filteredArray.length != 0) {
				return reason
			}
		}
	}
	return ''
}


async function getreason (inputstr) {
	// Matches keywords (lemmas) for each reason we are checking
	// Note that the keys *must* match the keys in scriptHelpers.js:GoToReason
	console.log("In getreason")
	const reason_keywords = {
		// "absence": 	["gone", "absent", "leaving"],
		'asláithreacht': 	['neamhláithreach', 'imigh/imeacht', 'fág', 'fágáil', 'láthair', 'amach', 'cruinniú', 'láithreacht', 'asláithreacht'],
		// "pickup": 	["early", "pickup"],
		'bailiú': 	['tóg', 'mochóirí', 'bailiú', 'bhailiú'],
		// "late": 	["late", "arrival"], 
		'sroichte níos déanaí': ['gabh', 'tar', 'anall', 'déanach'],
	}
	tagged_text = await tagText(inputstr)
	console.log(tagged_text)
	lemmas = tagged_text.map(l => l.lemma)
	console.log("input lemmas: " + lemmas)
	for (var reason in reason_keywords) {
		if (reason_keywords.hasOwnProperty(reason)){
			const filteredArray = reason_keywords[reason].filter(value => lemmas.includes(value))
			if (filteredArray.length != 0) {
				return reason
			}
		}
	}
	absence_reason = await getabsencereason(inputstr)
	if (absence_reason != '') {
		return "asláithreacht"
	}
	return ''
}

async function getdate (inputstr) {
	// This function naively tries to get the date from a user-supplied input.
	// The assumption is that the date will be in the form of 
	// "Month (the) Day" or "(the) Day (of) Month" or an optional weekday, 
	// e.g. "July the 8th" or "8th of July" or "next/last/this tuesday" or "today/tomorrow"

	// Due to weird stuff about case and the POS tagger's lemmas, I tried to put all possible forms in here.
	// A better solution would be to lemmatize our word list when we check and then do case-insensitive comparison.

	// this method needs to be decomposed, good lord.

	// Dé
	const all_weekdays = [
		'Luain', 
		'Máirt', 
		'Céadaoin', 
		'Déardaoin', 
		'Aoine', 
		'Sathairn', 
		'Domhnaigh', 
		'Domhnach',
		'Luan',
		'Satharn',
		'luain', 
		'máirt', 
		'céadaoin', 
		'déardaoin', 
		'aoine', 
		'sathairn', 
		'domhnaigh', 
		'domhnach',
		'luan',
		'satharn',
	]
	// mí
	const all_months = [
		'Eanáir', 
		'Feabhra', 
		'Feabhr', 
		'Márta', 
		'Aibreán', 
		'Bealtaine', 
		'Meitheamh', 
		'Iúil', 
		'Lúnasa', 
		'Meán', 
		'Deireadh', 
		'Samhain', 
		'Nollaig',
		'eanáir', 
		'feabhra', 
		'feabhr', 
		'márta', 
		'aibreán', 
		'bealtaine', 
		'meitheamh', 
		'iúil', 
		'lúnasa', 
		'meán', 
		'deireadh', 
		'samhain', 
		'nollaig',
		]
	// today/tomorrow
	const all_deictic = [
		'inniu', 
		'amárach', 
		'amanathar', 
		'amainiris',
		'mháireach', 
		'mhárach',
		'máireach',
		'márach',
		]
	// check these directly against the input string
	const explicit_deictic = [
		'an lá arna mhárach',
		'an lá dar gcionn',
		'an lá dár gcionn',
		'an lá ina dhiaidh sin',
		'an lá i ndéidh sin',
		]
	tagged_text = await tagText(inputstr)
	// necessary for the tagger to recognize proper nouns, since the ASR returns all lowercase
	// However there is probably a better way to reduce the number of checks and only send to the tagger once
	caps_input = capitalize_all_words(inputstr)
	tagged_caps_text = await tagText(caps_input)
	console.log('In getdate. Tagged text: ')
	console.log(tagged_text)
	lemmas = tagged_text.map(l => l.lemma)
	caps_lemmas = tagged_caps_text.map(l => l.lemma)
	console.log('All lemmas: ' + lemmas)
	
	// return priority:
	// 	- deictic
	// 	- month + day
	//  - weekday

	// find deictic pronouns
	potential_deictic = all_deictic.filter(v => lemmas.includes(v))
	found_deictic = ''
	if (potential_deictic.length == 1) {
		found_deictic = potential_deictic[0]
	} else {
		for (var explicit_day of explicit_deictic) {
			if (inputstr.includes(explicit_day) ) {
				found_deictic = explicit_day
			}
		}
	}
	console.log("Found deictic: " + found_deictic)

	// find month
	potential_caps_months = _get_tagged_text(tagged_caps_text, 'Prop').filter(v => all_months.includes(v))
	potential_months = caps_lemmas.filter(v => all_months.includes(v))
	console.log("potential months: " + potential_months)
	if (potential_caps_months.length == 1) {
		found_month = potential_caps_months[0]
	} else if (potential_months.length == 1 ) {
		found_month = potential_months[0]
	} else {
		found_month = ''
	}

	potential_numdays = _get_tagged_text(tagged_text, 'Num')
	console.log("potential numdays: " + potential_numdays)
	if (potential_numdays.length == 1) {
		found_numday = potential_numdays[0]
		// if (found_month != '') {
		// 	return found_month + ' ' + found_numday
		// }
	} else {
		found_numday = ''
	}
	console.log("Found numeral: " + found_numday)

	potential_weekdays = all_weekdays.filter(v => lemmas.includes(v))
	console.log("potential weekdays: " + potential_weekdays)
	if (potential_weekdays.length == 1) {
		// Also look for 'next'/'this' if found_weekday is not empty
		found_weekday = potential_weekdays[0]
		// this is imperfect, seo is used for both 'this' and 'next' week
		// Also I think there are multiple ways to say next/last?
		const all_relations = [
			'céad', 
			'sin', 
			'chugainn', 
			'chuig',
			'cuig',
			'seo', 
		] // seo is 'this', but also used for next - check for seo after the others
		potential_rel = all_relations.filter(v => lemmas.includes(v))
		weekday_rel = ''
		if (potential_rel.size == 1) {
			weekday_rel = potential_rel[0]
		}
	} else {
		found_weekday = ''
	}
	console.log("Found weekday: " + found_weekday)

	if (found_deictic != '') {
		return found_deictic
	} else if (found_month != '' && found_numday != '') {
		return found_month + ' ' + found_numday
	} else if (found_weekday != '') {
		if (weekday_rel != '') {
			return weekday_rel + ' ' + found_weekday
		}
		return found_weekday
	}
	return ''
}

async function gettime (inputstr) {
	// todo translate from time of day -> time?
	tagged_text = await tagText(inputstr)
	console.log("In gettime. Tagged text: " + tagged_text)
	lemmas = tagged_text.map(l => l.lemma)
	console.log("All lemmas: " + lemmas)
	
	const times_of_day = [
		'maidin', 
		'nóin', 
		'iarnóin', 
		'meán lae', 
		'trathnóna', 
		'trathnón',
		]
	potential_times_of_day = times_of_day.filter(v => lemmas.includes(v))
	if (potential_times_of_day.length == 1) {
		return potential_times_of_day[0]
	}
	time_num = _get_tagged_text(tagged_text, 'Num')
	if (time_num.length == 0) { // [] (not found)
		return ''
	} else if (time_num.length == 1) { // [12] (o'clock)
		return time_num[0]
	} else if (time_num.length == 2) { // [12, 30]
		return time_num.join(':')
	}
	return '' // 
}

function _get_tagged_text (tagged_text, find_str) {
	console.log(tagged_text)
	console.log('Looking for words with tag ' + find_str + ' in text ' + tagged_text.forEach(v => v.word))
	potential_matches = []
	for (var i = 0; i < tagged_text.length; i++) {
		word = tagged_text[i].lemma // should we be checking lemma or word?
		tags = tagged_text[i].tags
		if (tags.includes(find_str)) {
			potential_matches.push(word)
		}
	}
	return potential_matches
}

// https://stackoverflow.com/questions/34094806/return-from-a-promise-then
// The .then here is good for error handling *I think*
async function _generate_audio (inputstr, character = '') {
	console.log('in generate audio, character: ' + character)
	// I added an <audio> element in index.html so we don't need to create it here
	audio = document.querySelector('audio');
	if (audio !== null && !audio.paused) {
		audio.pause()
	}
	// Get the lódáil modal
	modal = document.getElementById('myModal');
	modal.style.display = 'block'
	resp = await audioTTS(inputstr)
	audio.src ="data:audio/mp3;base64," + resp.audioContent
	console.log(audio)
	return audio.play().then(() => {
		// once the audio plays, get rid of the popup
		modal.style.display = "none";
		if (character == '') {
			return inputstr
		} else {
			return character + ' ' + inputstr
		}
	})
	.catch( error => {
		// make sure to get rid of the popup regardless
		modal.style.display = "none";
		console.log(error)
	})
}

// A Monogatari.Action would be cleaner, but this works
monogatari.$ ('_toAudio', function (...args) {
	// Check if this is supposed to be said by a defined character
	test = tagText("conas atá tú")
	if (args[0] in monogatari.characters()) {
		character = args[0]
		inputstr = args.slice(1).join(' ')
	} else {
		character = ''
		inputstr = args.join(' ')
	}
	console.log("in toAudio, character: " + character)
	return _generate_audio(inputstr, character)
})

monogatari.script ({
	// The game starts here.
	'Start': [
		'show scene tcd with fadeIn',
		'Welcome! \n (Click/tap or spacebar to proceed)',
		{
			'Choice': {
				'Dialog': 'Would you like to play the intro?',
		    	'SkipIntro': {
		    	    'Text': 'Skip intro',
		    	    'Do': 'jump GetReason',
		    	},
		    	'PlayIntro': {
		    	    'Text': 'Play intro',
		    	    'Do': 'jump Intro',
		    	},
			},
		},
	],
	'Intro': [
		'show character p smiling at left',
		'p I\'m Patrick, the creator of this visual novel. Firstly, thank you for playing! I\'ll go through some instructions before we get started.',
		'p At the end of the game, there will be link to an optional survey, and any feedback you have is much appreciated. You can also reach out directly to me at: oneilp@tcd.ie',
		"p As you've figured out, you can advance to the next dialog with a click (tap if on mobile), or with the spacebar. If you're on a computer you can also navigate with the arrow keys.",
		'p You can go back by pressing the \'back\' button at the bottom of the screen, although sometimes you might not be able to.', 
		'p Some of the audio in this visual novel is generated on the spot, so there might be a bit of a delay before the next screen.',
		'p In fact, let\'s try one now: ',
		'$ _toAudio Dia duit, conas atá tú?',
		'p Hopefully you just saw and heard the phrase "Dia duit, conas atá tú?". If not, then something is probably wrong!',
		'p The goal of this scenario is to simulate what it might be like if you called a local Gaelscoil to report an absence, late arrival, or early pickup for a student.',
		'p You will be prompted to speak in Irish in order to provide the relevant information.',
		'p The program we\'re using to recognize your speech is imperfect, so you have as many tries as you need to record, and then when you\'re happy with it, you can click \'okay\'.\n Let\'s try one now!',
		{
			'Input': { 
				// 'Type': 'text',
				'Type': 'voiceIrish', // see code/myTextInput.js
				'Text': 'Say something in Irish, like \'Conas atá tú\'',
				'Validation': function (input) {
					return input.trim ().length > 0;
				},
				'Save': async function (input) {
					console.log("found input: " + input)
					this.storage ({
						player: {
							temp: input
						}
					});
					return true;
				},
				'Revert': function () {
					this.storage ({
						player: {
							temp: ''
						}
					});
				},
				'Warning': 'Caithfidh tú rud éigin a rá!'
			}
		},
		'p Great! I can see that you said: {{player.temp}}',
		'p That\'s the basic gist of it - now you\'re ready for the real scenario.',
		'p If you like it, you can try replaying and saying different things!',
		'p Again, thanks for playing!',
		'hide character p',
		'jump GetReason',
	],
	'EndGame': [
		'show character s happy at left',
		'$ _toAudio Go breá, go raibh maith agat. Slán!',
		'hide character s',
		'play voice hangup',
		'(Bíp)',
		'show scene parliament with fadeIn',
		'show character p smiling at left',
		'p This is as far as the game goes, though you can play it as many times as you like. Thank you again for playing!',
		'p If you would like, it would help me out a lot if you filled out the following 5-minute survey.',
		'show message Survey',
		'p Slán!',
		'hide character p',
		'Contact me with any feedback: <a href="mailto:hf.helium741@passmail.net" style="color: #0000ff">hf.helium741@passmail.net</a> | Made with ABAIR: <a href="https://abair.ie" target="_blank" style="color: #0000ff">abair.ie</a>',
		'end',
	],
});
