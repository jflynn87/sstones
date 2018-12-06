// $(document).ready(function() {
//   var day = $("#day_id").html()
//
//    $.ajax({
//        type: "GET",
//        url: "/ss_app/ajax/get_client/",
//        dataType: 'json',
//        data: {
//          activity: day
//              },
//        success: function (json) {
//
//          var i;
//          for (i = 0; i < json.length; ++i) {
//            console.log(i);
//            if (json[i][0] != undefined)  {
//             console.log(json[i][0].client__name);
//
//           $('#client' + [i+1]).html(json[i][0].client__name);
//
//           $('#client a' + [i+1]).attr("href", 'ss_app:client_form' + 'pk=' + json[i][0].client__pk)
//
//         }
//       }
//        },
//        failure: function(json) {
//          console.log('fail');
//          console.log(json);
//        }
//  });
//
// });
