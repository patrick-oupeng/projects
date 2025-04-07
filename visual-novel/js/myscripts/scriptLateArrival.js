monogatari.script({
	'Late': [
		// the check could be returned directly without the if/else, but I want to set the reasonstr
		{
			'Conditional': {
			    'Condition': function () {
			        if (this.storage ('player').date == ''){
			        	this.storage ('player').reasonstr = 'Cén lá a bheidh siad déanach?'
			        	return true
			        } else {
			        	return false
			        }
			    },
			    'True': 'jump LateGetDate',
			    'False': 'next',
			}
		},
		{
			'Conditional': {
			    'Condition': function () {
			        if (this.storage ('player').time == ''){
			        	this.storage ('player').reasonstr = 'Cén t-am a shroichfidh siad an scoil?'
			        	return true
			        } else {
			        	return false
			        }
			    },
			    'True': 'jump LateGetTime',
			    'False': 'next',
			}
		},
		'jump Confirmation',
	],
	// helper labels to be able to say things before jumping to the getdate loop
	'LateGetDate': [
		'$ _toAudio s Cén lá a bheidh {{player.childname}} déanach?', // what day will they be late
		'jump GetDateLoop',
	],
	'LateGetTime': [
		'play voice s1',
		's Agus cén t-am a shroichfidh siad an scoil?', // when will they arrive at school
		'jump GetTimeLoop',
	]
})