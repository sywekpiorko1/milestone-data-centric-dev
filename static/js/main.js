$(document).ready(function() {
  $(".sidenav").sidenav();
  $("select").formSelect();
  $(".modal").modal();
  $(".tabs").tabs();
  $(".materialboxed").materialbox();
  $(".collapsible").collapsible();
  $(".tooltipped").tooltip();
  $('.slider').slider({
      indicators: false,
      full_width: true,
      // height: 924,
      interval: 3000,
      duration: 1000
  });

  flashed_messages();
});

function flashed_messages() {
  let messages = parseInt($("#messages h4").length);
  if (messages) {
    console.log("Im in function flashed_messages()");
    $("#alerts").slideDown(1500);
    setTimeout(() => {
      $("#alerts").slideUp(1500);
    }, 4000);
  }
}
