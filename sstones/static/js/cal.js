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

$(document).ready(function () {

  var cal_table = document.getElementById("cal_table")
  var days_list = []

  for (var i = 0; i< cal_table.rows.length -1; i++) {

    day = $("#id_form-" + i + "-day").val()
    var index = i + 1
    //console.log(index, day);
    get_count(index, day)
  }
})

function get_count(index, day) {

    $.ajax({                       // initialize an AJAX request
      url: "/ss_app/ajax/cal_get_mtg_cnt/",                    // set the url of the request (= localhost:8000/hr/ajax/load-cities/)
      data: {
        'day': day
      },

        success: function (data) {   // `data` is the return of the `load_cities` view function
          var mtg_cnt = $("<a />", {
            id: "slots" + index,
            href: "/ss_app/calendar/" + data[1],
            text: "Meeting Count: " + data[2]

          })

          $('#slots' + index).html(mtg_cnt)

     },
        failure: function(json) {
        console.log('fail');
        console.log(json);
     }

     });

}

$( function() {
   $( "#date-filter" ).datepicker({
     dateFormat: 'yy-mm-dd',
     changeMonth: true,
     changeYear: true,
     onSelect: function() {
         var date = $(this).datepicker('getDate');
         var cal_table = document.getElementById("cal_table")
         console.log(date);
         for (var i = 0; i< cal_table.rows.length -1; i++) {
           var day = new Date($("#id_form-" + i + "-day").val())
           console.log(typeof Date);
           if (day < date) {
              $(cal_table.rows[i+1]).css({"display": "none"})
            }
           else {$(cal_table.rows[i+1]).css({"display": "table-row"})}
}
}
});
});


function reset_dates() {
  var cal_table = document.getElementById("cal_table")
  $('#date-filter').val('')
      for (var i = 0; i< cal_table.rows.length -1; i++) {
        $(cal_table.rows[i+1]).css({"display": "table-row"})

}
}
