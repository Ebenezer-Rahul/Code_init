$(document).ready(function(){
    var ctx = $("#mycanvas").get(0).getContext("2d");

    var data = [
        {
            value: 50,
            color: "#c21b1b",
            highlight: "#cc3f3f",
            label: "JavaScript"
        },
        {
            value: 270,
            color: "#6fd461",
            highlight: "lightgreen",
            label: "HTML"
        }
    ];

    var chart = new Chart(ctx).Doughnut(data);
});