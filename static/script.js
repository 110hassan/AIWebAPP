//function loading(){
    //let loader = document.getElementById("loader");
    //loader.classList.add("loader");
    //loader.innerHTML = "<h3>Please wait the image is being Processed...<h3>";
//}
document.addEventListener("DOMContentLoaded", () => {
    var text1 = document.getElementById('text1');
    let printButton = document.getElementById('printButton');
    // Check if text1 element exists and it's not empty
    if (text1 && text1.textContent.trim() !== "") {
        // Show the alert after a delay of 8 seconds
        setTimeout(() => {
            var recommendationAlert = document.getElementById('recommendationAlert');
            recommendationAlert.style.display = 'block';
            printButton.style.display = 'inline';
        }, 8000); // 8000 milliseconds = 8 seconds
    }
});

function showInterpretationAlert() {
    var interpretationAlert = document.getElementById('interpretationAlert');
    interpretationAlert.style.display = 'block';
}


function showInterpretations(){
    var interpretations = document.getElementById('text3');
    var t3 = document.getElementById('t3');
    var interpretationAlert = document.getElementById('interpretationAlert');

    // Show #text3
    t3.style.display = 'block';
    interpretations.style.display = 'block';
    animateText('text3');

    // Hide #interpretationAlert
    interpretationAlert.style.display = 'none';
}

function showRecommendations(){
    var recommendations = document.getElementById('text2');
    var t2 = document.getElementById('t2')
    var recommendationAlert = document.getElementById('recommendationAlert');

    // Show #text2
    t2.style.display = 'block'
    recommendations.style.display = 'block';
    animateText('text2');

    // Hide #interpretationAlert
    recommendationAlert.style.display = 'none';

    setTimeout(showInterpretationAlert, 14000);
}


// Function to animate text
function animateText(elementId) {
    var i = 0;
    let textElement = document.getElementById(elementId);
    var txt = textElement.innerText;
    var speed = 50;
    textElement.innerHTML = "";

    function typeWriter() {
        if (i < txt.length) {
            textElement.innerHTML += txt.charAt(i);
            i++;
            setTimeout(typeWriter, speed);
        }
    }

    // Start the typewriter animation
    typeWriter();
}

// Call the animation function for text1 when DOM content is loaded
document.addEventListener("DOMContentLoaded", function() {
    animateText('text1');
});

var printButton = document.getElementById("btn-print");
var header = document.getElementsByClassName("header");
function hideButton(){
    printButton.style.display = 'none';
    window.print();
    printButton.style.display = '';
}