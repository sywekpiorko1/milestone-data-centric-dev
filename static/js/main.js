
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

// disable enter key within textarea
$('textarea').keypress(function(event) {
    if ((event.keyCode || event.which) == 13) {
        event.preventDefault();;
        return false;
      }
    });
$('textarea').keyup(function() {
    var keyed = $(this).val().replace(/\n/g, '<br/>');

    $(this).html(keyed);

}); 