'use strict';
/* global Monogatari */
/* global monogatari */

/**
 * =============================================================================
 * This is the file where you should put all your custom JavaScript code,
 * depending on what you want to do, there are 3 different places in this file
 * where you can add code.
 *
 * 1. Outside the $_ready function: At this point, the page may not be fully
 *    loaded yet, however you can interact with Monogatari to register new
 *    actions, components, labels, characters, etc.
 *
 * 2. Inside the $_ready function: At this point, the page has been loaded, and
 *    you can now interact with the HTML elements on it.
 *
 * 3. Inside the init function: At this point, Monogatari has been initialized,
 *    the event listeners for its inner workings have been registered, assets
 *    have been preloaded (if enabled) and your game is ready to be played.
 *
 * You should always keep the $_ready function as the last thing on this file.
 * =============================================================================
 * 
 **/

const { $_ready, $_ } = Monogatari;

// 1. Outside the $_ready function:

// Could do this for the main menu as well - translating all the UI components would be a good project
// jk this doesn't work - I think there has to be language select, or somethign done at pre-compile
monogatari.component ('loading-screen').template (() => {
    return `
        <div data-content="wrapper">
			<h2 data-string="Loading" data-content="title">Lódáil</h2>
			<progress value="0" max="100" data-content="progress"></progress>
			<small data-string="LoadingMessage" data-content="message">Fan go fóill na dáilaí á lódáil.</small>
		</div>
    `;
});

// Add background image to main screen
monogatari.component ('main-screen').template (() => {
    return `
		<img src="assets/scenes/parliament-square.jpeg" alt="Trinity Parliament Square"></img>
        <main-menu></main-menu>
    `;
});

$_ready (() => {
	// 2. Inside the $_ready function:

	// Adds an <audio> html element for the generated voices to attach to later.
	// Also adds a 'loading' modal to prevent users from accidentally advancing the story while the audio is generated.
	// see script.js: _generate_audio()
	class MyAudio extends Monogatari.Component {
	    render () {
	     	return `
				<audio></audio>
		 		<my-stuff class="modal" id=myModal>
		 			<div class="modal__content">
						<div data-content="toAudio">
			    		  	<p>Lódáil...</p>
			    		</div>
			    	</div>
			    </my-stuff>
	    	`;   
	    }
	}
	MyAudio.tag = 'my-audio-element';
	monogatari.registerComponent (MyAudio);
	
	// Defines and registers a new TextInput component. Necessary for adding ASR voice input. see code/myTextInput.js
	myTextInput()
	// Defines and registers a new Play Action (e.g. 'play voice s2') that pauses other audio. Necessary to prevent audio overlap. see code/myPlay.js
	myPlay()

	monogatari.init ('#monogatari').then (() => {
		// 3. Inside the init function:

	});
});
