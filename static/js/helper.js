$(document).ready(function () {

    // change recipe card size depends on window width

    if ($(window).width() < 500) {
        $('.check-size').addClass('small');
    } else if (($(window).width() >= 500) && ($(window).width() < 600)) {
        $('.check-size').addClass('medium');
    } else if (($(window).width() >= 600) && ($(window).width() < 997)) {
        $('.check-size').addClass('large');
    } else if (($(window).width() >= 977) && ($(window).width() < 1500)) {
        $('.check-size').addClass('medium');
    } else {
        $('.check-size').addClass('large');
    }


    // show/hide search/filter section

    $('#show').click(function () {

        // for fast scrolling
        // window.scrollTo(0, 0);

        // for smooth scrolling
        $("html, body").animate({ scrollTop: 0 }, "slow");

        $('.filterSearch').toggle("slide");
        $('#show').toggle("slide");

    });

    // enable filter button

    $(".filter-section").change(function () {

        if (($('.filled-in').is(':checked') == true) || ($('#category').val()) != null || ($('#cuisine').val() != null)) {
            $('#filter-button').removeAttr('disabled');
        } else {
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

// change recipe card hight depends on window width

$(window).resize(function () {
    if ($(window).width() < 500) {
        $('.check-size').removeClass('medium');
        $('.check-size').removeClass('large');
        $('.check-size').addClass('small');
    } else if (($(window).width() >= 500) && ($(window).width() < 600)) {
        $('.check-size').removeClass('small');
        $('.check-size').removeClass('large');
        $('.check-size').addClass('medium');
    } else if (($(window).width() >= 600) && ($(window).width() < 997)) {
        $('.check-size').removeClass('small');
        $('.check-size').removeClass('medium');
        $('.check-size').addClass('large');
    } else if (($(window).width() >= 977) && ($(window).width() < 1500)) {
        $('.check-size').removeClass('large');
        $('.check-size').removeClass('small');
        $('.check-size').addClass('medium');
    } else {
        $('.check-size').removeClass('small');
        $('.check-size').removeClass('medium');
        $('.check-size').addClass('large');
    }
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