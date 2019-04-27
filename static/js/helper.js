$(document).ready(function () {
    
    // show/hide search/filter section
    
    $('#show').click(function () {
        
        // for fast scrolling
        // window.scrollTo(0, 0);

        // for smooth scrolling
        $("html, body").animate({ scrollTop: 0 }, "slow");

        $('.filterSearch').toggle("slide");

    });

    // enable filter button

    $(".filter-section").change(function () {

        if(($('.filled-in').is(':checked') == true) || ($('#category').val()) != null || ($('#cuisine').val() != null)) {
            $('#filter-button').removeAttr('disabled');
        }else{
            $('#filter-button').attr('disabled', 'disabled');
        };
    });

    // enable search button

    $('.search-section input').keyup(function () {

        var empty = true;
        $('.search-section input').each(function () {
            if ($(this).val().length >= 3) {
                empty = false;
            }
            console.log(empty)
        });

        if (empty) {
            $('#search-button').attr('disabled', 'disabled');
        } else {
            $('#search-button').removeAttr('disabled');
        }
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

// extend clicable area

$(".myClicableBox").click(function () {
    window.location = $(this).find("a").attr("href");
    return false;
});