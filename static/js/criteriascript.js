// Update ratings
$(document).ready(function() {

  $('#criteria_save_button').click(function(event) {

    $.ajax({
      data : {
        artist_name : $('#artist_name').val(), criteria_content : $('#criteria_content').val(),
        criteria_delivery : $('#criteria_delivery').val(), criteria_hits : $('#criteria_hits').val(),
        criteria_albums : $('#criteria_albums').val(), criteria_consistency : $('#criteria_consistency').val(),
        criteria_longevity : $('#criteria_longevity').val(), criteria_impact : $('#criteria_impact').val(),
        criteria_sales : $('#criteria_sales').val(), criteria_personality : $('#criteria_personality').val(),
        criteria_creativity : $('#criteria_creativity').val(), criteria_popularity : $('#criteria_popularity').val()
      },
      type : 'POST',
      url : '/changecriteria'
    })
    .done(function(data) {

      if (data.error) {
        $('#errorAlert').text(data.error).hide().fadeIn(1000).delay(1000).fadeOut(1000);
      }
      else {
        alert(success);
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
