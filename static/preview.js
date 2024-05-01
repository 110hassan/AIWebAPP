const selectImage = document.querySelector('.select-image');
const inputFile = document.querySelector('#file');
const imgArea = document.querySelector('.img-area');
let loader = document.getElementById("loader");
let predictButton = document.getElementById('predict-btn');

selectImage.addEventListener('click', function () {
	inputFile.click();
})

inputFile.addEventListener('change', function () {
	if (this.files.length > 0) {
		const image = this.files[0];
		const allowedExtensions = ['jpg', 'jpeg', 'png'];
		const fileExtension = image.name.split('.').pop().toLowerCase();
		if (allowedExtensions.includes(fileExtension)) {
			const reader = new FileReader();
			reader.onload = ()=> {
				const allImg = imgArea.querySelectorAll('img');
				allImg.forEach(item=> item.remove());
				const imgUrl = reader.result;
				const img = document.createElement('img');
				img.src = imgUrl;
				imgArea.appendChild(img);
				const loaderimg = document.createElement('img');
				loaderimg.src = imgUrl;
				loader.appendChild(loaderimg);
				loaderimg.setAttribute("id", "loader-img");
				loaderimg.style.display = 'none';
				imgArea.classList.add('active');
				imgArea.dataset.img = image.name;
				predictButton.style.display = 'block';
			}
			reader.readAsDataURL(image);
		} else {
			alert("Invalid file format. Only JPG, JPEG, and PNG files are allowed.");
		}
	} else {
		alert("No image selected");
	}
})




function loading(){
    let loader = document.getElementById("loader");
	let img = document.getElementById("loader-img");
    loader.classList.add("loader");
	img.style.display = 'block';
	let newElement = document.createElement("h3");
    newElement.textContent = "Please wait the image is being processed";
	// Append the new element to the div
    loader.appendChild(newElement);
}


//index1.html js code

const previousButton = document.querySelector('#prev')
const nextButton = document.querySelector('#next')
const submitButton = document.querySelector('#submit')
const tabTargets = document.querySelectorAll('.tab')
const tabPanels = document.querySelectorAll('.tabpanel')
const isEmpty = (str) => !str.trim().length
let currentStep = 0

// Validate first input on load
validateEntry()
// Next: Change UI relative to current step and account for button permissions
nextButton.addEventListener('click', (event) => {
  event.preventDefault()

  // Hide current tab
  tabPanels[currentStep].classList.add('hidden')
  tabTargets[currentStep].classList.remove('active')

  // Show next tab
  tabPanels[currentStep + 1].classList.remove('hidden')
  tabTargets[currentStep + 1].classList.add('active')
  currentStep += 1
  
  validateEntry()
  updateStatusDisplay()
})

// Previous: Change UI relative to current step and account for button permissions
previousButton.addEventListener('click', (event) => {
  event.preventDefault()

  // Hide current tab
  tabPanels[currentStep].classList.add('hidden')
  tabTargets[currentStep].classList.remove('active')

  // Show previous tab
  tabPanels[currentStep - 1].classList.remove('hidden')
  tabTargets[currentStep - 1].classList.add('active')
  currentStep -= 1

  nextButton.removeAttribute('disabled')
  updateStatusDisplay()
})


function updateStatusDisplay() {
  // If on the last step, hide the next button and show submit
  if (currentStep === tabTargets.length - 1) {
    nextButton.classList.add('hidden')
    previousButton.classList.remove('hidden')
    //submitButton.classList.remove('hidden')
    validateEntry()

    // If it's the first step hide the previous button
  } else if (currentStep == 0) {
    nextButton.classList.remove('hidden')
    previousButton.classList.add('hidden')
    //submitButton.classList.add('hidden')
    // In all other instances display both buttons
  } else {
    nextButton.classList.remove('hidden')
    previousButton.classList.remove('hidden')
    //submitButton.classList.add('hidden')
  }
}

function validateEntry() {
  let input = tabPanels[currentStep].querySelector('.form-input')
  
  // Start but disabling continue button
  nextButton.setAttribute('disabled', true)
  //submitButton.setAttribute('disabled', true)
  
  // Validate on initial function fire
  setButtonPermissions(input)
  
  // Validate on input
  input.addEventListener('input', () => setButtonPermissions(input))
  // Validate if bluring from input
  input.addEventListener('blur', () => setButtonPermissions(input))
}

function setButtonPermissions(input) {
  if (isEmpty(input.value)) {
    nextButton.setAttribute('disabled', true)
    //submitButton.setAttribute('disabled', true)
  } else {
    nextButton.removeAttribute('disabled')
    //submitButton.removeAttribute('disabled')
  }
}

const emailInput = document.getElementById('emailInput');
  const emailError = document.getElementById('emailError');

  emailInput.addEventListener('input', function() {
    if (!emailInput.validity.valid) {
      emailError.style.display = 'block';
    } else {
      emailError.style.display = 'none';
    }
  });