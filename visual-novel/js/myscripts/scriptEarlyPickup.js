monogatari.script({
	'Pickup': [
		// the check could be returned directly without the if statement, but I want to set the reasonstr
		{
			'Conditional': {
			    'Condition': function () {
			        if (this.storage ('player').date == ''){
			        	this.storage ('player').reasonstr = 'Cén lá a bheidh siad bailithe luath?'
			        	return true
			        } else {
			        	return false
			        }
			    },
			    'True': 'jump PickupGetDate',
			    'False': 'next',
			}
		},
		{
			'Conditional': {
			    'Condition': function () {
			        if (this.storage ('player').time == ''){
			        	this.storage ('player').reasonstr = 'Agus thart ar cén t-am a bheidh siad bailithe?'
			        	return true
			        } else {
			        	return false
			        }
			    },
			    'True': 'jump PickupGetTime',
			    'False': 'next',
			}
		},
		{
			'Conditional': {
			    'Condition': function () {
			        if (this.storage ('player').pickup_name == '' && this.storage('player').name == ''){
			        	this.storage ('player').reasonstr = 'Cé a bheidh ar an duine atá ag déanamh an bhailiúcháin?'
			        	return true
			        } else if (this.storage ('player').pickup_name == '' && this.storage('player').name != ''){
			        	this.storage('player').pickup_name = this.storage('player').name
			        	this.storage('player').name = ''
			        } else {
			        	console.log("This should never happen")
			        	return false
			        }
			    },
			    'True': 'jump PickupGetName',
			    'False': 'next',
			},
		},
		'jump Confirmation',
	],
	'PickupGetDate': [
		'$ _toAudio s Cén lá a bheidh {{player.childname}} bailithe luath?', // what date will they be collected early
		'jump GetDateLoop',
	],
	'PickupGetTime': [
		'$ _toAudio s Agus thart ar cén t-am a bheidh {{player.childname}} bailithe ag{{player.date}}?', // when on date will they be collected early
		'jump GetTimeLoop',
	],
	'PickupGetName': [
		'play voice s0',
		's Agus cén duine atá ag déanamh an bhailiúcháin?', // and who will be making the collection?
		// the pickup name is not used because I don't have handling if the user says 'me' to change to 'you'
		'jump GetNameLoop',
	],
})