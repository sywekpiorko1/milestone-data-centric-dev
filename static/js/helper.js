$(document).ready(function () {
    $('#show').click(function () {
        $('.filterSearch').toggle("slide");
    });

});

// disable enter key within textarea
$('textarea').keypress(function (event) {
    if ((event.keyCode || event.which) == 13) {
        event.preventDefault();;
        return false;
    }
});
$('textarea').keyup(function () {
    var keyed = $(this).val().replace(/\n/g, '<br/>');

    $(this).html(keyed);

});
$(".myClicableBox").click(function () {
    window.location = $(this).find("a").attr("href");
    return false;
});