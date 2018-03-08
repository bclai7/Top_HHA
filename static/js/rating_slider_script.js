$(function() {
    $('#artist_name').change(function() {
        $.ajax({
            url: '/artistchanged',
            type: 'GET',
            // This is query string i.e. country_id=123
            data: {artist_name : $('#artist_name').val()},
            success: function(data) {
              // parse incoming json list
              var ratingList = jQuery.parseJSON(data);

              // set sliders to correct values
              $('#rating_content').val(ratingList[0]);
              $('#rating_delivery').val(ratingList[1]);
              $('#rating_hits').val(ratingList[2]);
              $('#rating_albums').val(ratingList[3]);
              $('#rating_consistency').val(ratingList[4]);
              $('#rating_longevity').val(ratingList[5]);
              $('#rating_impact').val(ratingList[6]);
              $('#rating_sales').val(ratingList[7]);
              $('#rating_personality').val(ratingList[8]);
              $('#rating_creativity').val(ratingList[9]);
              $('#rating_popularity').val(ratingList[10]);

              // Set Display scores to correct values
              $('#slider_score_content').text(ratingList[0]);
              $('#slider_score_delivery').text(ratingList[1]);
              $('#slider_score_hits').text(ratingList[2]);
              $('#slider_score_albums').text(ratingList[3]);
              $('#slider_score_consistency').text(ratingList[4]);
              $('#slider_score_longevity').text(ratingList[5]);
              $('#slider_score_impact').text(ratingList[6]);
              $('#slider_score_sales').text(ratingList[7]);
              $('#slider_score_personality').text(ratingList[8]);
              $('#slider_score_creativity').text(ratingList[9]);
              $('#slider_score_popularity').text(ratingList[10]);



            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(errorThrown);
            }
        });
    });
});
