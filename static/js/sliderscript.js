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
                console.log(errorThrown);
            }
        });
    });
});
