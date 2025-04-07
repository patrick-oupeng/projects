function clearvariables() {
	// clears the reason-specific variables to allow a re-run of a reason if something was wrong
	// Assumes that the child name and the overall reason are correct
	this.storage ({
		player: {
			date: '', // Date for pickup/late arrival
			startdate: '', // only for absence - start day of absence
			enddate: '', // only for absence - end day of absence
			time: '', // Time for pickup/late arrival
			reasonstr: '', // Used for printing to dialogues dynamically
		}
	});
}

monogatari.$ ('_dialog', function () {
	reason = this.storage('player').reason
	if (reason == 'asláithreacht') {
		return  '$ _toAudio s Ar fheabhas, tá taifead déanta agam anois go mbeidh {{player.childname}} as láthair ó {{player.startdate}} go dtí {{player.enddate}}.' // I have here that student will be absent from start to end
	}
	if (reason == 'bailiú') {
		// return '$ _toAudio s Ar fheabhas, tá taifead déanta agam anois go mbeidh {{player.childname}} pioctha suas go luath {{player.date}}, timpeall {{player.time}}, ag {{player.pickup_name}}.' // I have here that student will be picked up on date at time by name
		return '$ _toAudio s Ar fheabhas, tá taifead déanta agam anois go mbeidh {{player.childname}} pioctha suas go luath {{player.date}}, timpeall {{player.time}}.' //, ag {{player.pickup_name}}.' taking out the pickup_name until I have the proper handling for it in script.js
	}
	if (reason == 'sroichte níos déanaí') {
		if (this.storage('player').time == 'UNK') {
			return  '$ _toAudio s Ar fheabhas, tá taifead déanta agam anois go mbeidh {{player.childname}} níos déanaí {{player.date}}, níl tú cinnte cathain go díreach.' // late arrival, time UNK
		}
		return '$ _toAudio s Ar fheabhas, tá taifead déanta agam anois go mbeidh {{player.childname}} ag teacht isteach níos déanaí {{player.date}}, timpeall {{player.time}}.' // late arrival 
	}
	console.log(this.storage('player'))
	return 'Chuaigh rud éigin mícheart, níor cheart go dtaispeánfadh an teachtaireacht seo choíche!' // todo check?
});

monogatari.script({
	'GetAbsenceReasonLoop': [ // not really a loop, since it defaults to 'other' if not found
		{
			'Input': { 
				// 'Type': 'text',
				'Type': 'voiceIrish',
				'Text': '{{player.reasonstr}}',
				'Validation': function (input) {
					return input.trim ().length > 0;
				},
				'Save': async function (input) {
					foundabsencereason = await getabsencereason(input)
					console.log("after getabsencereason, found: " + foundabsencereason)
					this.storage ({
						player: {
							absence_reason: foundabsencereason
						}
					});
					console.log("after storage")
					return true;
				},
				'Revert': function () {
					this.storage ({
						player: {
							foundabsencereason: ''
						}
					});
				},
				'Warning': 'Caithfidh tú rud éigin a rá!' // you have to say something!
			}
		},
		{
			'Conditional': {
			    'Condition': function () {
			    	console.log("in absencereason conditoinal")
			    	console.log(this.storage('player'))
			    	if (this.storage('player').absence_reason == '') {
			    		console.log('inside empty reason conditional')
			        	this.storage ('player').absence_reason = 'other';
			    	}
			    	console.log(this.storage('player').absence_reason)
			    	return this.storage('player').absence_reason
			    },
			    // Preferably these would be voice lines since they don't include any variables,
			    // But as far as I can tell that would require jumping to a new label, or having some placeholder, so this is easier.
			    'other': '$ _toAudio s Ceart go leor, déanfaidh mé taifead don asláithreacht anseo mar "eile".', // I'll record the reason here as 'other'
			    'tinneas': "$ _toAudio s Ó, tá brón orm cloisteáil nach bhfuil {{player.childname}} ag mothú go maith.", // maybe change to "I hope they're okay"? e.g. going to doctor
			    'teaghlach': "$ _toAudio s Ó, tá súil agam go bhfuil gach rud ceart go leor/Tá brón orm é sin a chloisint.", // todo this has a slash
			    'saoire': '$ _toAudio s Ó, bain sult as sin.', // oh, have fun
			}
		},
		'jump GoToReason',
	],
	'GetDateLoop': [
		{
			'Input': { 
				// 'Type': 'text',
				'Type': 'voiceIrish',
				'Text': '{{player.reasonstr}}',
				'Validation': function (input) {
					return input.trim ().length > 0;
				},
				'Save': async function (input) {
					founddate = await getdate(input)
					console.log("after getdate, found: " + founddate)
					this.storage ({
						player: {
							date: founddate
						}
					});
					console.log("after storage")
					return true;
				},
				'Revert': function () {
					this.storage ({
						player: {
							date: ''
						}
					});
				},
				'Warning': 'Caithfidh tú rud éigin a rá!' // you have to say something!
			}
		},
		{
			'Conditional': {
			    'Condition': function () {
			    	console.log("in getdate conditoinal")
			    	console.log(this.storage('player'))
			        return this.storage ('player').date == '';
			    },
			    'True': 'jump NoResponseFound',
			    'False': 'jump GoToReason',
			}
		},
	],
	'NoDateFound': [
		'show character s confused at left',
		'play voice s18',
		's Tá brón orm, níor chuala mé thú. An féidir é sin a rá arís?',
		'jump GetDateLoop',
	],
	'GetTimeLoop': [
		{
			'Input': { 
				// 'Type': 'text',
				'Type': 'voiceIrish',
				'Text': '{{player.reasonstr}}',
				'Validation': function (input) {
					return input.trim ().length > 0;
				},
				'Save': async function (input) {
					foundtime = await gettime(input)
					console.log("after gettime, found: " + foundtime)
					this.storage ({
						player: {
							time: foundtime
						}
					});
					console.log("after storage")
					return true;
				},
				'Revert': function () {
					this.storage ({
						player: {
							time: ''
						}
					});
				},
				'Warning': 'Caithfidh tú rud éigin a rá!' // you have to say something!
			}
		},
		{
			'Conditional': {
			    'Condition': function () {
			    	if (this.storage('player').reason == 'late' && this.storage('player').time == '') {
			    		this.storage('player').time = 'UNK'
			    		return false
			    	} else { 
			        	return this.storage ('player').time == '';
			        }
			    },
			    'True': 'jump NoResponseFound',
			    'False': 'jump GoToReason',
			}
		},
	],
	'NoTimeFound': [
		'show character s bored at left',
		'play voice s18',
		's Tá brón orm, níor chuala mé thú. An féidir é sin a rá arís?',
		'jump GetTimeLoop',
	],
	'GetNameLoop': [
		{
			'Input': { 
				// 'Type': 'text',
				'Type': 'voiceIrish',
				'Text': '{{player.reasonstr}}',
				'Validation': function (input) {
					return input.trim ().length > 0;
				},
				'Save': async function (input) {
					foundname = await getname(input)
					console.log("after getname")
					console.log('startdate: ' + this.storage('player').startdate)
					this.storage ({
						player: {
							//capitalize
							name: foundname.charAt(0).toUpperCase() + foundname.slice(1)
						}
					});
					console.log("after storage")
					return true;
				},
				'Revert': function () {
					this.storage ({
						player: {
							name: ''
						}
					});
				},
				'Warning': 'Caithfidh tú rud éigin a rá!' // you have to say something!
			},
		},
		{
			'Conditional': {
			    'Condition': function () {
			        return this.storage ('player').name == '';
			    },
			    'True': 'jump NoNameFound',
			    'False': 'jump GoToReason',
			}
		},
	],
	'NoNameFound': [
		'show character s empty at left',
		'play voice s18',
		's Tá brón orm, níor chuala mé thú. An féidir é sin a rá arís?',
		'jump GetNameLoop',
	],
	// Old method - issue was that this would restart the whole Reason, when I only need it to restart the loop
	// Could probably be cleaned up.
	'NoResponseFound': [
		'show character s confused at left',
		'play voice s18',
		's Tá brón orm, níor chuala mé thú. An féidir é sin a rá arís?',
		'jump GoToReason',
	],
	// Simple wrapper to jump back to the Reason label
	'GoToReason': [
		{
			'Conditional': {
			    'Condition': function () {
			    	console.log("In GoToReason, current variables: ")
			    	console.log(this.storage('player'))
			    	if (this.storage('player').reason != '' && this.storage('player').childname == ''){
			    		return 'childname'
			    	} else {
			        	return this.storage ('player').reason
			        }
			    },
			    '': 'jump GetReasonLoop',
			    'childname': 'jump ChildName',
			    'asláithreacht': 'jump Absence',
			    'bailiú': 'jump Pickup',
			    'sroichte níos déanaí': 'jump Late',
			},
		},
	],
	
	'Confirmation': [
		'play voice s17',
		'show character s writing at left',
		's Déarfaidh mé leat céard atá scriofa agam faoi láthair...',
		'$ _dialog',
		'play voice s25',
		's An bhuil sin ceart?',
		{
			'Choice': {
				'FirstOption': {
					'Text': 'Tá',
					'Do': 'jump Correct',
				},
				'SecondOption': {
					'Text': 'Níl',
					'Do': 'jump Incorrect',
				},
			},
		},
	],
	'Correct': [
		'jump EndGame',
	],
	// this part feels a bit hacky
	'Incorrect': [
		clearvariables,
		'$ _toAudio s Ár leithscéal, déanaimis iarracht arís.', // sorry let's try again
		// since everything except the reason and childname are cleared, it should be identical to the first time through the main Reason loop
		'jump GoToReason',
	],
})