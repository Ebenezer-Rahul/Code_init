console.log("hello")

var xmlhttp = new XMLHttpRequest();

var url = "/recive"

xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        var myArr = JSON.parse(this.responseText);
        console.log(myArr)
    }
};


//xmlhttp.open("GET", url, true);


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function sendRequests() 
{

    while (true) {

        xmlhttp.open("GET", url, true);
        xmlhttp.send();
        await sleep(500)
    }
}

sendRequests();


