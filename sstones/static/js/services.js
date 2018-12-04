$(document).ready(function() {
  console.log("ready"); })

$(function() {
  $("#opt1").hover(function() {
  $('#desc1').removeAttr('hidden');
  $('#desc1').fadeIn('slow');
  $('#desc2').attr('hidden', true);
  $('#desc3').attr('hidden', true);
  $('#desc4').attr('hidden', true);
  $('#intro').attr('hidden', true);
});
})

$(function() {
  $("#opt2").hover(function() {
  $('#desc2').removeAttr('hidden');
  $('#desc1').attr('hidden', true);
  $('#desc3').attr('hidden', true);
  $('#desc4').attr('hidden', true);
  $('#intro').attr('hidden', true);
});
})

$(function() {
  $("#opt3").hover(function() {
  $('#desc3').removeAttr('hidden');
  $('#desc2').attr('hidden', true);
  $('#desc1').attr('hidden', true);
  $('#desc4').attr('hidden', true);
  $('#intro').attr('hidden', true);
});
})

$(function() {
  $("#opt4").hover(function() {
  $('#desc4').removeAttr('hidden');
  $('#desc2').attr('hidden', true);
  $('#desc1').attr('hidden', true);
  $('#desc3').attr('hidden', true);
  $('#intro').attr('hidden', true);
});
})
