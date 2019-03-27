$(document).ready(function () {
    flashed_messages();
});

function flashed_messages() {
    let messages = parseInt($("#messages h4").length);
    if (messages) {
        console.log('Im in function flashed_messages()');
        $("#alerts").slideDown(1500);
        setTimeout(() => {
            $("#alerts").slideUp(1500);
        }, 4000);
    }
}