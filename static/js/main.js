$(function () {
    $.ajaxSetup({"contentType": "text/json"});
});

function getdata() {
    $.get(ccu3api_url, function(data){
        console.log(data);
        for (var i = 0; i < data.rooms.length; i++) {
            setstate(i, data.rooms[i].state, data.rooms[i].name);
        }
    });
}

function setstate(room_number, state, name) {
    var room_id = "#btn_room_" + room_number;
    console.log("Setting room " + room_number + " (" + name + ") to " + state);
    $(room_id).text(name);
    if (state) {
        $(room_id).removeClass('btn-danger');
        $(room_id).addClass('btn-success');
    }
    else {
        $(room_id).removeClass('btn-success');
        $(room_id).addClass('btn-danger');
    }
    
}

console.log(window.location.origin);
var ccu3api_url = window.location.origin + "/api/v1/ccu3_get_windowstates";

getdata();
window.setInterval(getdata, 5000);
