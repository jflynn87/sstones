$( function() {
   $( "#id_date" ).datepicker({
     dateFormat: 'yy-mm-dd',
     changeMonth: true,
     changeYear: true,
     beforeShowDay: checkDate,
});
});

function getHolidays() {
    var holidays = holidays.getElementsByTagName('li')

    return [holidays];


};

function checkDate(date) {
  var today = new Date()

  if (date < today) {
    return [false, ""]
  }

  holidays = holiday_sect.getElementsByTagName('li')
  var holiday_list = []
  for (var i =0; i < holidays.length; i++) {
    holiday_list.push(new Date(holidays[i].innerText).getTime())
  }
  var formatted_date = ((jQuery.datepicker))

  if (holiday_list.includes(date.getTime())) {
     return [false, ""]
  }
  else {
    return [true, ""]
  }

  }

function getSlots() {
       var url = $("#appt_form").attr("data-slots-url");  // get the url of the `load_cities` view
       var dayId = $('#id_date').val();  // get the selected country ID from the HTML input
       var client = $('#id_email').val()
       if ($("#add_appt").length) {
         var mode = "add"
       }
       else if ($('#update_appt').length) {
         var mode = "update"
       }
       console.log(dayId);
       console.log('client', client);
       console.log(mode);


       $.ajax({                       // initialize an AJAX request
         url: url,                    // set the url of the request (= localhost:8000/hr/ajax/load-cities/)
         data: {
           'day': dayId,
           'client': client,
           'mode': mode       // add the country id to the GET parameters
         },

           success: function (data) {   // `data` is the return of the `load_cities` view function
           $("#id_time").html(data);  // replace the contents of the city input with the data that came from the server

        },
           failure: function(json) {
           console.log('fail');
           console.log(json);
        }

          });

  };


$( function() {
   $("#id_date").change(function () {
     getSlots()
   });
 });

$(function() {
  $("#id_time").focus(function () {
    console.log("select");
  if ($('#id_date').val() != '') {
   getSlots()
 }
})
})


$( function() {
  $("#id_email").change(function () {
    console.log("email changed");
    var client = $("#id_email").val();  // get the url of the `load_cities` view

    if ($('#id_date').val() != '') {
      getSlots()
    }

    $.ajax({                       // initialize an AJAX request
      url: "/ss_app/ajax/appt_get_client/",                    // set the url of the request (= localhost:8000/hr/ajax/load-cities/)
      data: {
        'client': client       // add the country id to the GET parameters
      },

        success: function (data) {   // `data` is the return of the `load_cities` view function
        $("#id_name").val(data[0]);  // replace the contents of the city input with the data that came from the server
        $("#id_phone").val(data[1]);

     },
        failure: function(json) {
     console.log('fail');
     console.log(json);
      }
       });
 });
});




// Initialize and add the map
function initMap() {
// The location of Uluru
var office = {lat: 35.627353, lng: 139.726217};
// The map, centered at Uluru
var map = new google.maps.Map(
   document.getElementById('map'), {zoom: 16, center: office});
// The marker, positioned at Uluru
var marker = new google.maps.Marker({position: office, map: map});
}
