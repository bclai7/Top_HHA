$(function() {
    $('#artist_name').change(function() {
        $.ajax({
            url: '/sliderchanged',
            type: 'GET',
            // This is query string i.e. country_id=123
            data: {artist_name : $('#artist_name').val()},
            success: function(data) {
              // parse incoming json list
              var ratingList = jQuery.parseJSON(data);

              // set sliders to correct values
              $('#slider_content').val(ratingList[0]);
              $('#slider_delivery').val(ratingList[1]);
              $('#slider_hits').val(ratingList[2]);
              $('#slider_albums').val(ratingList[3]);
              $('#slider_consistency').val(ratingList[4]);
              $('#slider_longevity').val(ratingList[5]);
              $('#slider_impact').val(ratingList[6]);
              $('#slider_sales').val(ratingList[7]);
              $('#slider_personality').val(ratingList[8]);
              $('#slider_creativity').val(ratingList[9]);
              $('#slider_popularity').val(ratingList[10]);

            },
            error: function(jqXHR, textStatus, errorThrown) {
                $('#slider_content').val(1);
                $('#slider_delivery').val(1);
                $('#slider_hits').val(1);
                $('#slider_albums').val(1);
                $('#slider_consistency').val(1);
                $('#slider_longevity').val(1);
                $('#slider_impact').val(1);
                $('#slider_sales').val(1);
                $('#slider_personality').val(1);
                $('#slider_creativity').val(1);
                $('#slider_popularity').val(1);
            }
        });
    });
});
