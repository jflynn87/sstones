// $(function() {
//   $( ".datepicker" ).daterangepicker({
//     changeMonth: true,
//     changeYear: true,
//     yearRange: "2018:2021",
//     // You can put more options here.
//   });
// });

$(document).ready(function() {
  var cal_table = document.getElementById("cal_table")
  var days_list = {}


  for (var i = 0; i<= cal_table.rows.length; i++) {


    var cal_date = new Date(cal_date =  $("#id_form-" + i + "-day").val());
    var weekday = new Array(7);
    weekday[0] = "Sunday";
    weekday[1] = "Monday";
    weekday[2] = "Tuesday";
    weekday[3] = "Wednesday";
    weekday[4] = "Thursday";
    weekday[5] = "Friday";
    weekday[6] = "Saturday";

    var dow = weekday[cal_date.getDay()]
    var row = $("#display_day" + [i + 1])
    row.html(dow)

      }
});
