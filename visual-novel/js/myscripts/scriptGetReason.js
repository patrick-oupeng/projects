monogatari.script({
	'GetReason': [
		'show scene cozy',
		'play voice phone',
		'(Glaoch...)',
		'show character s happy at left',
		'play voice s16',
		's Dia duit, seo í an rúnaí.', // Hi, I'm the secretary - name?
		'play voice s3',
		's An bhfuil tú ag cur glaoch chun asláithreacht a thuairisciú, am sroichte níos déanaí a thuairisciú, nó dalta a bhailiú níos luaithe i rith an lae?', // calling about absence, arrival, or pickup?
		'jump GetReasonLoop',
	],
	'GetReasonLoop': [
		{
			'Input': { 
				// 'Type': 'text',
				'Type': 'voiceIrish',
				'Text': 'Cén fáth a bhfuil tú ag glaoch?', // why are you calling
				'Validation': function (input) {
					return input.trim ().length > 0;
				},
				'Save': async function (input) {
					foundreason = await getreason(input)
					console.log("after getreason")
					this.storage ({
						player: {
							reason: foundreason
						}
					});
					console.log("after storage")
					return true;
				},
				'Revert': function () {
					this.storage ({
						player: {
							reason: ''
						}
					});
				},
				'Warning': 'Caithfidh tú rud éigin a rá!' // you have to say something!
			},
		},
		'jump ReasonResp',
	],
	'InvalidReason': [
		'show character s pensive at left',
		'play voice s21',
		's Gabh mo leithscéal, ní féidir liom cabhrú leat ach le hasláithreacht, páiste ag teacht isteach déanach nó ag bailiú páiste luath.', // sorry can only help with absence late arrival or early collection
		'play voice s4',
		's An féidir é sin a rá arís?', // could you say that again?
		'jump GetReasonLoop',
	],
	'ReasonResp': [
		{
			'Conditional': {
			    'Condition': function () {
			        return this.storage ('player').reason == '';
			    },
			    'True': 'jump NoResponseFound',
			    'False': 'next',
			}
		},
		{
			'Conditional': {
			    'Condition': function () {
			        return ['asláithreacht', 'bailiú', 'sroichte níos déanaí'].includes(this.storage ('player').reason)
			    },
			    'True': 'next',
			    'False': 'jump InvalidReason',
			},
		},
		'show character s happy at left',
		'$ _toAudio s Go breá, tá tú ag cur glaoch maidir le {{player.reason}}.', // great, you're calling about reason
		'play voice s19',
		's Tá píosa eolais breise ag teastáil uaim uaitse mar sin.', // I'll need some more info
		'jump ChildName',
	],
})