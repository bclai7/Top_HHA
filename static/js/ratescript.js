// Update ratings
$(document).ready(function() {

  $('#rating_save_button').click(function(event) {

    $.ajax({
      data : {
        artist_name : $('#artist_name').val(), rating_content : $('#rating_content').val(),
        rating_delivery : $('#rating_delivery').val(), rating_hits : $('#rating_hits').val(),
        rating_albums : $('#rating_albums').val(), rating_consistency : $('#rating_consistency').val(),
        rating_longevity : $('#rating_longevity').val(), rating_impact : $('#rating_impact').val(),
        rating_sales : $('#rating_sales').val(), rating_personality : $('#rating_personality').val(),
        rating_creativity : $('#rating_creativity').val(), rating_popularity : $('#rating_popularity').val()
      },
      type : 'POST',
      url : '/rated'
    })
    .done(function(data) {

      if (data.error) {
        $('#errorAlert').text(data.error).hide().fadeIn(1000).delay(1000).fadeOut(1000);
      }
      else {
        $('#successAlert').text('Saved').hide().fadeIn(1000).delay(1000).fadeOut(1000);
      }

    });

    // Disables default HTML form action when clicking a submit button
    event.preventDefault();

    // Scroll to bottom of page to view "Saved" message
    $("html, body").animate({ scrollTop: $(document).height() }, "slow");
    return false;

  });

});
