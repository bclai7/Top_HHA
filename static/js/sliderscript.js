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

              alert(ratingList[0]);
              // set sliders to correct values
              $("#slider_content").html($(ratingList[0]));

            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert(errorThrown);
            }
        });
    });
});
