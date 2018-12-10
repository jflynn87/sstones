$(document).ready(function() {
  var day = $("#day_id").html()

   $.ajax({
       type: "GET",
       url: "/ss_app/ajax/get_client/",
       dataType: 'json',
       data: {
         activity: day
             },
       success: function (json) {

         var i;
         for (i = 0; i < json.length; ++i) {
           console.log(i);
           if (json[i][0] != undefined)  {

              var client_link = $("<a />", {
                id : "client" + [i+1],
                href : '/ss_app/update_client/' + json[i][0].client__pk,
                text : json[i][0].client__name
              })

              var appt_link = $("<a />", {
                id : "appt" + [i+1],
                href : '/ss_app/thanks/' + json[i][0].pk,
                text : "Appointment Detail/Info"
              })
              console.log(client_link);
              $('#client' + [i+1]).html(client_link)
              $('#appt' + [i+1]).html(appt_link);


        }
      }
       },
       failure: function(json) {
         console.log('fail');
         console.log(json);
       }
 });

});
