// clear the screen for testing
/*
document.body.innerHTML = '';
document.body.style.background="white";

var nums = [1,2,3];

// Let's loop over the numbers in our array
for (var i = 0; i < nums.length; i++) {

    // This is the number we're on...
    var num = nums[i];

    // We're creating a DOM element for the number
    var elem = document.createElement('div');
    elem.textContent = num;

    // ... and when we click, alert the value of `num`
    elem.addEventListener('click', (function(numCopy) {
        return function() {
         	alert(numCopy);
        };
    })(num));

    // finally, let's add this element to the document
    document.body.appendChild(elem);
};
*/
var numClicks = 0;
var cat1 = document.getElementById("cat-5");
var c5 = document.getElementById("n5");
var pElem = document.createElement('p');


cat1.addEventListener('click', function() {
	numClicks++;
	console.log(numClicks);
	//return alert('click');
	c5.innerHTML = numClicks;
});

pElem.textContent = numClicks;

document.body.appendChild(pElem);

