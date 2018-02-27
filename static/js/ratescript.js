// Update ratings
$(document).ready(function() {

  $('#save_button').click(function(event) {

    $.ajax({
      data : {
        artist_name : $('#artist_name').val(), slider_content : $('#slider_content').val(),
        slider_delivery : $('#slider_delivery').val(), slider_hits : $('#slider_hits').val(),
        slider_albums : $('#slider_albums').val(), slider_consistency : $('#slider_consistency').val(),
        slider_longevity : $('#slider_longevity').val(), slider_impact : $('#slider_impact').val(),
        slider_sales : $('#slider_sales').val(), slider_personality : $('#slider_personality').val(),
        slider_creativity : $('#slider_creativity').val(), slider_popularity : $('#slider_popularity').val()
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
