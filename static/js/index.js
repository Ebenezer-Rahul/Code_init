console.log("hello")

var xmlhttp = new XMLHttpRequest();

var url = "/recive"

var done = false

var total_links = 0;
var goodlinks = 0;
var badLinks = 0;

xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        var res = JSON.parse(this.responseText);
        
        console.log(typeof(res.isDone));

        if (res.isDone == 1) {
            done = true;
            return;
        }
        //console.log(isDone, isLink);
        if (res.isLink == 0) {
            return;    
        }

        console.log("here", res.isDone, res.isLink);
        tag = document.createElement('tr');
        //tag.insertBefore(   c );
        currtd = document.createElement('td');
        currtd.innerHTML = res.status_code;

        tag.appendChild(currtd);

        //console.log(myArr.link);
        currtd = document.createElement('td');
        currlink = document.createElement('a');
        currlink.href = res.link;
        currlink.target = "_blank"
        currlink.innerHTML = res.link;
        currtd.appendChild(currlink);
        tag.appendChild(currtd);


        currtd = document.createElement('td');
        if(res.status_code/100 == 2) {
            currtd.innerHTML = "OK"
            goodlinks = goodlinks + 1;
        }
        else {
            currtd.innerHTML = "NOT OK"
            badLinks = badLinks + 1;
        }
        tag.appendChild(currtd);
        table = document.getElementById("resList");
        table.appendChild(tag);
        total_links = res.total_links;
        console.log(goodlinks, badLinks, total_links);
    }
};


//xmlhttp.open("GET", url, true);


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function sendRequests() 
{
    while (!done) {
        xmlhttp.open("GET", url, true);
        xmlhttp.send();
        await sleep(500)
    }
}



var chart = null;
var data = null;

$(document).ready(function(){
    var ctx = $("#mycanvas").get(0).getContext("2d");

    data = [
        {
            value: 1,
            color: "black",
            highlight: "black",
            label: "UnvisitedLinks"
        },
        {
            value: 1,
            color: "red",
            highlight: "red",
            label: "goodlinks"
        },
        {
            value: 1,
            color: "green",
            highlight: "green",
            label: "badLinks"
        }
    ];

    chart = new Chart(ctx,{options: {
        events: []
    }});
    chart.Doughnut(data)
});


setInterval(function(){
    console.log("new Chart");
    console.log(chart);
    if (data === null || chart === null) 
    {
        return;
    }
    data[2].value = goodlinks; 
    data[1].value = badLinks; 
    data[0].value = total_links; 
    chart.Doughnut(data, {animation : false});
    console.log("new Chart");

}, 500);



sendRequests();



