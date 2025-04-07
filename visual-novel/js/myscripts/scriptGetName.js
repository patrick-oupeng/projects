monogatari.script({
	'ChildName': [
		{
			'Conditional': {
			    'Condition': function () {
			        if (this.storage('player').childname == '' && this.storage ('player').name == '') {
			        	this.storage('player').reasonstr = "Cén t-ainm atá ar an dalta scoile?"
			        	return true
			        } else if (this.storage ('player').childname == '' && this.storage ('player').name != '') {
			        	this.storage('player').childname = this.storage('player').name
			        	this.storage('player').name = ''
			        	return false
			        } else {
			        	console.log("This should never happen")
			        	return false
			        }
			    },
			    'True': 'jump GetChildName',
			    'False': 'next',
			}
		},
		'jump ChildNameResp',
	],
	'GetChildName': [
		'show character s asking at left',
		'play voice s13',
		's Cén t-ainm atá ar an dalta scoile?', // what is the name of the student?
		'jump GetNameLoop',
	],
	'ChildNameResp': [
		{
			'Conditional': {
			    'Condition': function () {
			        return this.storage ('player').childname == "";
			    },
			    'True': 'jump NoName',
			    'False': 'next',
			}
		},
		'show character s happy at left',
		'$ _toAudio s Go breá, tá tú ag cur glaoch maidir le {{player.reason}} do {{player.childname}}.', // calling about reason for child
		'play voice s19',
		's Tá píosa eolais breise ag teastáil uaim uaitse mar sin.', // i'll need some more info
		'jump GoToReason', // start the specific loop for each reason
	],
})