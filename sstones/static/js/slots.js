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
         console.log(json);
         var i;
         for (i = 0; i <= json.length; ++i) {
           console.log($('#client' + [i]));
          $('#client' + [i+1]).html(json[i]);
        }
       },
       failure: function(json) {
         console.log('fail');
         console.log(json);
       }
 });

});
