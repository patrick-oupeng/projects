monogatari.script({
	'Absence': [
		{
			'Conditional': {
			    'Condition': function () {
			        if (this.storage ('player').absence_reason == '') {
			        	this.storage ('player').reasonstr = "Cén chúis atá ann don asláithreacht seo?" // What is the reason for this absence?
			        	return true
			        } else {
			        	return false
			        }
			    },
			    'True': 'jump AbsenceGetReason',
			    'False': 'next',
			}
		},
		// if all are empty, get the start date
		{
			'Conditional': {
			    'Condition': function () {
			        if (this.storage ('player').startdate == '' 
			        && this.storage ('player').enddate == '' 
			        && this.storage ('player').date == '') {
			        	this.storage ('player').reasonstr = 'Cén dáta a bheidh siad as láthair?' // When does the absence start
			        	return true
			        } else {
			        	return false
			        }
			    },
			    'True': 'jump AbsenceStartGetDate',
			    'False': 'next',
			}
		},
		// if the start date is empty but we have *a* date stored, that's the start date
		{
			'Conditional': {
			    'Condition': function () {
			    	if (this.storage ('player').startdate == '' 
			        && !this.storage ('player').date == '') {
			    		this.storage ('player').startdate = this.storage ('player').date;
			    		this.storage ('player').date = '';
			        	this.storage ('player').reasonstr = 'Cathain a fhillfidh siad ar an scoil?' // when do they return to school
			    		return true;
			    	} else {
			    		return false;
			    	}
			    },
			    'True': 'jump AbsenceEndGetDate',
			    'False': 'next',
			}
		},
		// if the end date is empty and we have a date,
		// then by this point the start date is filled in,
		// so the date stored is the end date
		{
			'Conditional': {
			    'Condition': function () {
			    	if (this.storage ('player').enddate == '' 
			        && !this.storage ('player').date == '') {
			    		this.storage ('player').enddate = this.storage ('player').date;
			    		this.storage ('player').date = '';
			    		this.storage ('player').reasonstr = '';
			    		return true;
			    	} else {
			    		return false;
			    	}
			    },
			    'True': 'next',
			    'False': 'Something went wrong!',
			}
		},
		'jump Confirmation',
	],
	// helper labels to be able to say things before jumping to the relevant loop
	'AbsenceGetReason': [
		'play voice s8',
		's Cén chúis atá ann don asláithreacht seo?', // what is the reason for this absence?
		'jump GetAbsenceReasonLoop',
	],
	'AbsenceStartGetDate': [
		// todo add picture
		'$ _toAudio s Cén dáta a bheidh {{player.childname}} as láthair?', // when will this absence start
		'jump GetDateLoop',
	],
	'AbsenceEndGetDate': [
		// todo add picture
		'$ _toAudio s Agus cathain a fhillfidh {{player.childname}} ar an scoil?', // when will child return to school
		'jump GetDateLoop',
	]
})