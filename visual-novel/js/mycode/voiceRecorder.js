// Most of this code was taken directly from web-dictaphone.
// I removed extra stuff that saves the audio to a list and displays its length, lets you play it back, etc. since that's not needed for ASR.
// See https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API/Using_the_MediaStream_Recording_API
const voiceRecorder = () => {

	// Set up basic variables for app
	const record = document.querySelector(".record");
	const stop = document.querySelector(".stop");
	const inputField = document.querySelector(".input-field")
	// inputField.style.fontSize = "2rem"
	const validaudio = document.querySelector(".transcription");
	const mainSection = document.querySelector(".main-controls");
	// defined explicitly for type = voiceIrish in myTextInput.js
	const submitbutton = document.getElementById("submitbutton")
	const warningtext = document.getElementById("warningtext")

	// Disable stop button while not recording
	stop.disabled = true;

	// Main block for doing the audio recording
	if (navigator.mediaDevices.getUserMedia) {
	  console.log("The mediaDevices.getUserMedia() method is supported.");

	  const constraints = { audio: true };
	  let chunks = [];

	  let onSuccess = function (stream) {
	    const mediaRecorder = new MediaRecorder(stream);

	    record.onclick = function () {
	      mediaRecorder.start();
	      console.log("Recorder started.");
	      validaudio.textContent = "";
	      record.style.background = "red";

	      stop.disabled = false;
	      record.disabled = true;
	    };

	    stop.onclick = function () {
	      mediaRecorder.stop();
	      console.log("Recorder stopped.");
	      record.style.background = "";
	      record.style.color = "";

	      stop.disabled = true;
	      record.disabled = false;
	    };

	    mediaRecorder.onstop = function (e) {
	      console.log("Last data to read (after MediaRecorder.stop() called).");

	      // abair returns in wav format
	      const blob = new Blob(chunks, { type: "audio/wav" });
	      chunks = [];

	      // the warning 'you have to say something' has html id of: warningtext
	      // and the 'okay' button has html id of: submitbutton
	      // we want to hide the warning text when the user hits record
	      // and we only want to show the 'okay' button once the user hits record
	      
	      // below is all that's needed for speech recognition
	      convertBlobToBase64(blob).then(result => {
	      	// Maybe set inputField.textContent to "Lodail"?
	        validaudio.textContent = "Lódáil...";
	        warningtext.textContent = "";
	        audioASR(result.slice(22)).then(data => { // see code/audioASR.js
	          // setAwaitingTranscription(false); // helper
	        	if (data.transcriptions[0].utterance.replaceAll("\n","") !== "") {
	        		inputField.textContent = data.transcriptions[0].utterance;
	        		validaudio.textContent = "";
	        		submitbutton.style.display="inline-block";
	        	} else {
	        		// validaudio.textContent = "No valid audio detected";
	        		validaudio.textContent = "Easpa fuaime bailí"; // lack (of) valid audio
	        	}
	          // setTranscription(data.transcriptions[0].utterance); // helper
	        })
	      })
	      // end speech recognition
	    };

	    mediaRecorder.ondataavailable = function (e) {
	      chunks.push(e.data);
	    };
	  };

	  let onError = function (err) {
	    console.log("The following error occured: " + err);
	  };

	  navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);
	} else {
	  console.log("MediaDevices.getUserMedia() not supported on your browser!");
	}

	// Adds a waveform visualizer for the audio stream.
	// Unnecessary for my purposes but kept in here for now.
	function visualize(stream) {
	  if (!audioCtx) {
	    audioCtx = new AudioContext();
	  }

	  const source = audioCtx.createMediaStreamSource(stream);

	  const analyser = audioCtx.createAnalyser();
	  analyser.fftSize = 2048;
	  const bufferLength = analyser.frequencyBinCount;
	  const dataArray = new Uint8Array(bufferLength);

	  source.connect(analyser);

	  draw();

	  function draw() {
	    const WIDTH = canvas.width;
	    const HEIGHT = canvas.height;

	    requestAnimationFrame(draw);

	    analyser.getByteTimeDomainData(dataArray);

	    canvasCtx.fillStyle = "rgb(200, 200, 200)";
	    canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

	    canvasCtx.lineWidth = 2;
	    canvasCtx.strokeStyle = "rgb(0, 0, 0)";

	    canvasCtx.beginPath();

	    let sliceWidth = (WIDTH * 1.0) / bufferLength;
	    let x = 0;

	    for (let i = 0; i < bufferLength; i++) {
	      let v = dataArray[i] / 128.0;
	      let y = (v * HEIGHT) / 2;

	      if (i === 0) {
	        canvasCtx.moveTo(x, y);
	      } else {
	        canvasCtx.lineTo(x, y);
	      }

	      x += sliceWidth;
	    }

	    canvasCtx.lineTo(canvas.width, canvas.height / 2);
	    canvasCtx.stroke();
	  }
	}

	/* END copied directly from web dictaphone */ 
}